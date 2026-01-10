"""
Performance testing with Locust
Tests API endpoints under load to verify p95 latency < 200ms
"""

from locust import HttpUser, task, between, events
import random
import json
import time

# Test data
SAMPLE_TASKS = [
    {"title": "Complete project documentation", "priority": "high"},
    {"title": "Review pull requests", "priority": "medium"},
    {"title": "Update dependencies", "priority": "low"},
    {"title": "Fix authentication bug", "priority": "high"},
    {"title": "Implement search feature", "priority": "medium"},
]


class TodoAppUser(HttpUser):
    """Simulates a user interacting with the Todo App API"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when a simulated user starts"""
        self.task_ids = []
        self.auth_token = None

        # Register/login user
        user_id = random.randint(1000, 9999)
        self.username = f"loadtest_user_{user_id}"
        self.password = "TestPass123!"

        # Register
        response = self.client.post(
            "/api/auth/register",
            json={
                "username": self.username,
                "email": f"{self.username}@test.com",
                "password": self.password,
            },
            name="/api/auth/register",
        )

        if response.status_code in [200, 201]:
            self.auth_token = response.json().get("access_token")
        else:
            # Try login if already exists
            response = self.client.post(
                "/api/auth/login",
                json={"username": self.username, "password": self.password},
                name="/api/auth/login",
            )
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")

    @property
    def headers(self):
        """Get headers with auth token"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    @task(5)
    def create_task(self):
        """Create a new task"""
        task_data = random.choice(SAMPLE_TASKS).copy()
        task_data["description"] = f"Task created at {time.time()}"

        with self.client.post(
            "/api/tasks",
            json=task_data,
            headers=self.headers,
            catch_response=True,
            name="/api/tasks [POST]",
        ) as response:
            if response.status_code == 201:
                task_id = response.json().get("id")
                self.task_ids.append(task_id)
                response.success()
            else:
                response.failure(f"Failed to create task: {response.status_code}")

    @task(10)
    def list_tasks(self):
        """List all tasks"""
        with self.client.get(
            "/api/tasks",
            headers=self.headers,
            catch_response=True,
            name="/api/tasks [GET]",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to list tasks: {response.status_code}")

    @task(3)
    def get_task(self):
        """Get a specific task"""
        if not self.task_ids:
            return

        task_id = random.choice(self.task_ids)

        with self.client.get(
            f"/api/tasks/{task_id}",
            headers=self.headers,
            catch_response=True,
            name="/api/tasks/:id [GET]",
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Task might have been deleted
                self.task_ids.remove(task_id)
            else:
                response.failure(f"Failed to get task: {response.status_code}")

    @task(2)
    def update_task(self):
        """Update a task"""
        if not self.task_ids:
            return

        task_id = random.choice(self.task_ids)

        with self.client.patch(
            f"/api/tasks/{task_id}",
            json={"title": f"Updated task {time.time()}"},
            headers=self.headers,
            catch_response=True,
            name="/api/tasks/:id [PATCH]",
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                self.task_ids.remove(task_id)
            else:
                response.failure(f"Failed to update task: {response.status_code}")

    @task(2)
    def complete_task(self):
        """Mark a task as complete"""
        if not self.task_ids:
            return

        task_id = random.choice(self.task_ids)

        with self.client.post(
            f"/api/tasks/{task_id}/complete",
            headers=self.headers,
            catch_response=True,
            name="/api/tasks/:id/complete [POST]",
        ) as response:
            if response.status_code in [200, 204]:
                response.success()
            elif response.status_code == 404:
                self.task_ids.remove(task_id)
            else:
                response.failure(f"Failed to complete task: {response.status_code}")

    @task(1)
    def search_tasks(self):
        """Search tasks"""
        search_terms = ["project", "bug", "feature", "review", "documentation"]
        search_term = random.choice(search_terms)

        with self.client.get(
            f"/api/tasks/search?q={search_term}",
            headers=self.headers,
            catch_response=True,
            name="/api/tasks/search [GET]",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to search tasks: {response.status_code}")

    @task(1)
    def filter_tasks(self):
        """Filter tasks by priority"""
        priority = random.choice(["high", "medium", "low"])

        with self.client.get(
            f"/api/tasks?priority={priority}",
            headers=self.headers,
            catch_response=True,
            name="/api/tasks?priority [GET]",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to filter tasks: {response.status_code}")

    @task(1)
    def health_check(self):
        """Check API health"""
        with self.client.get(
            "/health", catch_response=True, name="/health [GET]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print("=" * 60)
    print("Performance Test Started")
    print("=" * 60)
    print(f"Target: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    print("=" * 60)
    print("Performance Test Completed")
    print("=" * 60)

    stats = environment.stats

    # Check if p95 latency is under 200ms
    passed = True

    print("\nLatency Statistics:")
    print("-" * 60)

    for name, stat in stats.entries.items():
        if stat.num_requests > 0:
            p95 = stat.get_response_time_percentile(0.95)
            p99 = stat.get_response_time_percentile(0.99)

            status = "✓ PASS" if p95 < 200 else "✗ FAIL"

            print(
                f"{name:40} p50: {stat.median_response_time:6.0f}ms "
                f"p95: {p95:6.0f}ms p99: {p99:6.0f}ms {status}"
            )

            if p95 >= 200:
                passed = False

    print("=" * 60)
    print(f"Overall result: {'PASSED' if passed else 'FAILED'}")
    print(f"Success rate: {stats.total.success_percentage:.2f}%")
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print("=" * 60)
