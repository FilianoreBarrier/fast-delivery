from app.routes.v1.auth import router as auth_router
from app.routes.v1.seller.products import router as seller_prod_routes
from app.routes.v1.seller.categories import router as seller_cat_routes
__all__ = ["auth_router","seller_prod_routes","seller_cat_routes"]
