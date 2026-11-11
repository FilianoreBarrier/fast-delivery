from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
import logging
# Импорт роутеров
from app.routes.v1 import auth_router, seller_prod_routes,seller_cat_routes, user_router, cart_router, order_router
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Создаем таблицы в PostgreSQL...")
    await init_db()
    yield
    logging.info("Сервер останавливается...")

app = FastAPI(
    lifespan=lifespan,
    title="FastDelivery",
    description="Приложение сервиса доставки 'Fast-Delivery.'",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(seller_prod_routes, prefix='/api/v1', tags = ["products"])
app.include_router(seller_cat_routes, prefix='/api/v1', tags = ["categories"])
app.include_router(user_router, prefix='/api/v1', tags = ["users"])
app.include_router(cart_router, prefix='/api/v1', tags = ["cart"])
app.include_router(order_router, prefix='/api/v1', tags = ["orders"])



@app.on_event("startup")
async def startup_event():
    await init_db()
    print("✅ FastDelivery запущен. База данных инициализирована.")


@app.get("/")
async def root():
    return {"message": "FastDelivery API работает!", "docs": "/docs"}
