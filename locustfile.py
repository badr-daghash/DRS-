from locust import HttpUser, task, between
import random

class DjangoUser(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get token
        response = self.client.post("/api/token/", json={
            "username": "admin",
            "password": "test"
        })

        print("Login status:", response.status_code)
        print("Login response:", response.text)

        if response.status_code == 200:
            try:
                self.token = response.json()["access"]
            except Exception as e:
                print("Failed to parse JSON from login:", e)
                self.token = None
        else:
            print("Login failed, cannot get token")
            self.token = None

        # Optionally set the user ID for orders
        self.user_id = 1

    @task
    def create_order(self):
        if not self.token:
            # Skip task if login failed
            print("Skipping order creation because no token is available")
            return

        # Generate 1–5 random products
        items = [
            {"product": random.randint(1, 1000), "quantity": random.randint(1, 5)}
            for _ in range(random.randint(1, 5))
        ]

        payload = {
            "status": "Pending",
            "user": self.user_id,
            "items": items
        }

        response = self.client.post(
            "/order/",
            json=payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        # Print response for debugging
        print(f"Order payload: {payload}")
        print(f"Response status: {response.status_code}, body: {response.text}")
