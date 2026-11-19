const { createApp, ref, reactive, computed, onMounted } = Vue;

const API = '/api/v1';
const TOKEN_KEY = 'fd_token';

createApp({
  setup() {
    /* ---------- состояние ---------- */
    const token = ref(localStorage.getItem(TOKEN_KEY));
    const user = ref(null);
    const tab = ref('catalog');
    const authMode = ref('login');
    const busy = ref(false);
    const loading = reactive({ catalog: false, cart: false, orders: false });

    const categories = ref([]);
    const products = ref([]);
    const selectedCategory = ref(null);
    const productNames = reactive({});

    const cart = ref({ items: [], total: 0, items_count: 0 });
    const orders = ref([]);

    const loginForm = reactive({ email: '', password: '' });
    const regForm = reactive({ username: '', email: '', full_name: '', password: '', role: 'buyer' });
    const catForm = reactive({ name: '', slug: '' });
    const catSlugTouched = ref(false);
    const prodForm = reactive({ name: '', description: '', price: null, category_id: '', image_url: '' });

    const toast = reactive({ text: '', type: 'ok' });
    let toastTimer = null;

    const inspector = reactive({
      open: true, pending: false, method: '', url: '',
      status: null, requestBody: null, responseBody: null,
    });

    /* ---------- вычисляемые ---------- */
    const isSeller = computed(() => user.value?.role === 'seller');

    const tabs = computed(() => {
      const list = [{ id: 'catalog', label: 'Каталог' }];
      if (!user.value) return [...list, { id: 'auth', label: 'Вход / Регистрация' }];
      if (isSeller.value) list.push({ id: 'seller', label: 'Панель продавца' });
      list.push({ id: 'cart', label: 'Корзина' }, { id: 'orders', label: 'Мои заказы' });
      return list;
    });

    const inspectorStatusClass = computed(() => {
      const s = inspector.status;
      if (inspector.pending) return 'bg-white/10';
      if (typeof s !== 'number') return 'bg-red-500 text-white';
      if (s < 300) return 'bg-emerald-500 text-ink';
      if (s < 400) return 'bg-sky-400 text-ink';
      if (s < 500) return 'bg-amber-400 text-ink';
      return 'bg-red-500 text-white';
    });

    /* ---------- утилиты ---------- */
    function notify(text, type = 'ok') {
      toast.text = text;
      toast.type = type;
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => (toast.text = ''), 4000);
    }

    const moneyFmt = new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' });
    const money = (v) => moneyFmt.format(Number(v) || 0);
    const dateTime = (v) => (v ? new Date(v).toLocaleString('ru-RU') : '');

    const STATUS_CLASSES = {
      Unpaid: 'bg-amber-100 text-amber-800',
      Paid: 'bg-emerald-100 text-emerald-800',
      Processing: 'bg-sky-100 text-sky-800',
      Shipped: 'bg-indigo-100 text-indigo-800',
      Delivered: 'bg-green-200 text-green-900',
      Cancelled: 'bg-red-100 text-red-800',
    };
    const statusClass = (s) => STATUS_CLASSES[s] || 'bg-slate-100 text-slate-700';

    function errorText(data, status) {
      const d = data && data.detail;
      if (typeof d === 'string') return d;
      if (Array.isArray(d)) return d.map((e) => `${(e.loc || []).slice(1).join('.')}: ${e.msg}`).join('; ');
      return `Ошибка ${status}`;
    }

    const slugify = (s) => s.toLowerCase().trim()
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

    /* ---------- HTTP-клиент + инспектор ---------- */
    async function api(method, path, { body, auth = true } = {}) {
      const url = API + path;
      const headers = {};
      if (body !== undefined) headers['Content-Type'] = 'application/json';
      if (auth && token.value) headers['Authorization'] = `Bearer ${token.value}`;

      const shown = body && typeof body === 'object' ? { ...body } : body;
      if (shown && shown.password) shown.password = '••••••••';

      Object.assign(inspector, {
        pending: true, method, url, status: null,
        requestBody: shown !== undefined ? JSON.stringify(shown, null, 2) : null,
        responseBody: null,
      });

      let res;
      try {
        res = await fetch(url, {
          method, headers,
          body: body !== undefined ? JSON.stringify(body) : undefined,
        });
      } catch (e) {
        Object.assign(inspector, {
          pending: false, status: 'NETWORK',
          responseBody: `Не удалось выполнить запрос: ${e.message}\nПроверьте, что Nginx проксирует /api/ на бэкенд.`,
        });
        throw new Error('Нет связи с сервером');
      }

      const text = await res.text();
      let data = null;
      try { data = text ? JSON.parse(text) : null; } catch { data = text; }

      Object.assign(inspector, {
        pending: false, status: res.status,
        responseBody: typeof data === 'string' ? data : JSON.stringify(data, null, 2),
      });

      if (!res.ok) {
        if (res.status === 401 && auth && token.value) {
          clearSession();
          tab.value = 'auth';
          throw new Error('Сессия истекла. Войдите снова.');
        }
        throw new Error(errorText(data, res.status));
      }
      return data;
    }

    // Обёртка для действий: busy + показ ошибок
    async function run(fn) {
      busy.value = true;
      try { return await fn(); }
      catch (e) { notify(e.message, 'error'); }
      finally { busy.value = false; }
    }

    /* ---------- сессия ---------- */
    function clearSession() {
      token.value = null;
      user.value = null;
      localStorage.removeItem(TOKEN_KEY);
      cart.value = { items: [], total: 0, items_count: 0 };
      orders.value = [];
    }

    async function loadMe() {
      user.value = await api('GET', '/users/me');
    }

    async function login() {
      await run(async () => {
        const data = await api('POST', '/auth/login', { body: { ...loginForm }, auth: false });
        token.value = data.access_token;
        localStorage.setItem(TOKEN_KEY, token.value);
        await loadMe();
        loginForm.password = '';
        notify(`Добро пожаловать, ${user.value.full_name || user.value.username}!`);
        tab.value = 'catalog';
        loadCart(true);
      });
    }

    async function register() {
      await run(async () => {
        const wantedRole = regForm.role;
        const payload = {
          username: regForm.username,
          email: regForm.email,
          password: regForm.password,
          role: wantedRole,
        };
        if (regForm.full_name) payload.full_name = regForm.full_name;

        const created = await api('POST', '/auth/register', { body: payload, auth: false });

        // Бэкенд всегда создаёт buyer — предупреждаем, если выбран seller
        if (wantedRole === 'seller' && created.role !== 'seller') {
          notify('Аккаунт создан, но сервер назначил роль «buyer». Роль seller выдаётся через БД.', 'warn');
        }

        const data = await api('POST', '/auth/login', {
          body: { email: regForm.email, password: regForm.password }, auth: false,
        });
        token.value = data.access_token;
        localStorage.setItem(TOKEN_KEY, token.value);
        await loadMe();
        regForm.password = '';
        if (wantedRole !== 'seller' || created.role === 'seller') notify('Аккаунт создан, вы вошли в систему');
        tab.value = 'catalog';
      });
    }

    async function logout() {
      await run(async () => {
        try { await api('POST', '/auth/logout'); }
        catch (e) { /* токен всё равно удаляем локально */ }
        clearSession();
        tab.value = 'catalog';
        notify('Вы вышли из аккаунта');
      });
    }

    /* ---------- каталог ---------- */
    async function loadCategories() {
      categories.value = await api('GET', '/categories/');
    }

    async function loadProducts() {
      loading.catalog = true;
      try {
        const path = selectedCategory.value === null
          ? '/products/'
          : `/products/category/${selectedCategory.value}`;
        const data = await api('GET', path);
        products.value = data.products;
        data.products.forEach((p) => (productNames[p.id] = p.name));
      } finally {
        loading.catalog = false;
      }
    }

    function selectCategory(id) {
      selectedCategory.value = id;
      run(loadProducts);
    }

    async function addToCart(product) {
      if (!user.value) {
        notify('Войдите, чтобы добавлять товары в корзину', 'warn');
        tab.value = 'auth';
        return;
      }
      await run(async () => {
        cart.value = await api('POST', '/cart/add', { body: { product_id: product.id, quantity: 1 } });
        notify(`«${product.name}» добавлен в корзину`);
      });
    }

    /* ---------- продавец ---------- */
    function autoSlug() {
      if (!catSlugTouched.value) catForm.slug = slugify(catForm.name);
    }

    async function createCategory() {
      await run(async () => {
        const c = await api('POST', '/categories/', { body: { name: catForm.name, slug: catForm.slug } });
        notify(`Категория «${c.name}» создана`);
        catForm.name = '';
        catForm.slug = '';
        catSlugTouched.value = false;
        await loadCategories();
      });
    }

    async function createProduct() {
      await run(async () => {
        const body = {
          name: prodForm.name,
          description: prodForm.description || null,
          price: prodForm.price,
          category_id: prodForm.category_id,
          image_url: prodForm.image_url || null,
        };
        const p = await api('POST', '/products/', { body });
        notify(`Товар «${p.name}» добавлен`);
        Object.assign(prodForm, { name: '', description: '', price: null, image_url: '' });
        await loadProducts();
      });
    }

    /* ---------- корзина ---------- */
    async function loadCart(silent = false) {
      if (!user.value) return;
      if (!silent) loading.cart = true;
      try {
        cart.value = await api('GET', '/cart/');
      } catch (e) {
        notify(e.message, 'error');
      } finally {
        loading.cart = false;
      }
    }

    async function changeQty(item, qty) {
      if (qty < 1) return removeItem(item);
      await run(async () => {
        cart.value = await api('PUT', '/cart/update', { body: { product_id: item.product_id, quantity: qty } });
      });
    }

    async function removeItem(item) {
      await run(async () => {
        cart.value = await api('DELETE', `/cart/remove/${item.product_id}`);
      });
    }

    async function checkout() {
      await run(async () => {
        const order = await api('POST', '/orders/');
        notify(`Заказ №${order.id} оформлен`);
        cart.value = { items: [], total: 0, items_count: 0 };
        await goTo('orders');
      });
    }

    /* ---------- заказы ---------- */
    async function loadOrders() {
      loading.orders = true;
      try {
        // Сначала справочник названий товаров, последним — заказы (виден в инспекторе)
        const all = await api('GET', '/products/');
        all.products.forEach((p) => (productNames[p.id] = p.name));
        const list = await api('GET', '/orders/');
        orders.value = [...list].sort((a, b) => b.id - a.id);
      } catch (e) {
        notify(e.message, 'error');
      } finally {
        loading.orders = false;
      }
    }

    /* ---------- навигация ---------- */
    async function goTo(id) {
      tab.value = id;
      if (id === 'cart') await loadCart();
      if (id === 'orders') await loadOrders();
      if (id === 'catalog') await run(async () => { await loadCategories(); await loadProducts(); });
      if (id === 'seller') await run(loadCategories);
    }

    /* ---------- старт ---------- */
    onMounted(async () => {
      if (token.value) {
        try { await loadMe(); }
        catch { clearSession(); }
      }
      await run(async () => {
        await loadCategories();
        await loadProducts();
        if (user.value) await loadCart(true);
      });
    });

    return {
      tab, tabs, authMode, busy, loading, toast, inspector, inspectorStatusClass,
      user, isSeller, categories, products, selectedCategory, productNames,
      cart, orders, loginForm, regForm, catForm, catSlugTouched, prodForm,
      money, dateTime, statusClass,
      login, register, logout, goTo, selectCategory, addToCart,
      autoSlug, createCategory, createProduct,
      changeQty, removeItem, checkout,
    };
  },
}).mount('#app');
