
from locust import HttpUser, task, between


class AssetTrackerUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def list_assets(self):
        with self.client.get(
            "/assets?limit=100&offset=0",
            name="/assets",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Unexpected status code: {response.status_code}"
                )
