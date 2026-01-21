from locust import HttpUser, task, between
import random

class DjangoUser(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(1, 3)

    product_ids = list(range(1, 11001))  

    @task(3)
    def list_products(self):
        self.client.get("/products/")

    @task(1)
    def get_product(self):
        product_id = random.choice(self.product_ids)
        self.client.get(f"/products/{product_id}/")

