from fastapi import HTTPException, status


def raise_user_not_found(user_id: int):
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = f"User with id {user_id} not found."
    )

def raise_product_not_found(product_id: int):
    raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Product with id {product_id} not found."

            )
def raise_category_not_found(category_id: int):
    raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Category with id {category_id} not found."

            )

def raise_order_not_found(order_id: int):
    raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Order with id {order_id} not found."

            )
