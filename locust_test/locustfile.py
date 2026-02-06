from locust import HttpUser, task

class NormalUser(HttpUser):
    @task
    def index(self):
        self.client.get("/")
    def count(self):
        self.client.get("/count")