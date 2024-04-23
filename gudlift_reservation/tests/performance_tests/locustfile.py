from locust import HttpUser, task, between


class PerfTest(HttpUser):
    # wait_time = between(1, 3)

    @task
    def index(self):
        self.client.get("/")

    @task
    def login(self):
        self.client.get("/login")

    @task
    def show_summary(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task
    def purchase_places(self):
        self.client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply pytestLift",
                "places": 1,
            },
        )

    @task
    def logout(self):
        self.client.get("/logout")
