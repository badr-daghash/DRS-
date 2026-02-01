from locust import HttpUser, task, between
import random

class DjangoUser(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(1, 3)

    def on_start(self):

        response = self.client.post("/api/token/", json={
            "username": "john-doe",
            "password": "test"
        })
        self.token = response.json()["access"]

    @task
    def create_order(self):
        # generate 1–5 random products for each order
        items = [
            {"product": random.randint(1, 1000), "quantity": random.randint(1, 5)}
            for _ in range(random.randint(1, 5))
        ]

        self.client.post(
            "/order/",
            json={ "status": "Pending",  "items": items},
            headers={"Authorization": f"Bearer {self.token}"}
        )