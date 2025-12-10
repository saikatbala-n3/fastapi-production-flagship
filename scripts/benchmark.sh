#!/bin/bash

echo "Installing locust..."
pip install locust

echo "Creating locustfile..."
cat > locustfile.py <<'EOF'
from locust import HttpUser, task, between

class FastAPIUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # Register and login
        response = self.client.post("/api/v1/auth/register", json={
            "email": f"user{self.environment.runner.user_count}@example.com",
            "username": f"user{self.environment.runner.user_count}",
            "password": "testpassword123"
        })

        if response.status_code == 201:
            login_response = self.client.post("/api/v1/auth/login", json={
                "username": f"user{self.environment.runner.user_count}",
                "password": "testpassword123"
            })
            self.token = login_response.json()["access_token"]

    @task(3)
    def get_health(self):
        self.client.get("/api/v1/health")

    @task(2)
    def get_profile(self):
        self.client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def update_profile(self):
        self.client.put(
            "/api/v1/users/me",
            json={"full_name": "Updated Name"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
EOF

echo "Running benchmark..."
echo "Visit http://localhost:8089 to view results"
locust -f locustfile.py
