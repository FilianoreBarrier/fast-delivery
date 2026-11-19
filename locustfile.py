import uuid
from locust import HttpUser, task, between

class FastDeliveryUser(HttpUser):
    wait_time = between(1,2)

    @task(3)
    def get_products(self):
        self.client.get("/api/v1/products/")

    @task(1)
    def register_user(self):
        unique_id = str(uuid.uuid4())[:8]
        self.client.post("/api/v1/auth/register", json={
            "username": f"user_{unique_id}",
            "email": f"{unique_id}@test.com",
            "full_name": "Load User",
            "role": "buyer",
            "password": "StrongPassword123"
        })
