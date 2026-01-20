import random
from datetime import datetime, timedelta, timezone
from locust import HttpUser, task, between

PROMOS = ["M1_E3A", "PSEE", "Saphire", "Intranet"]
CLASSROOMS = ["2Z34", "2Z42", "1Y40", "C2N"]

class WebCafeUser(HttpUser):
    wait_time = between(0.1, 1.0)   # “temps humain” entre actions

    def on_start(self):
        # endpoint simple
        self.client.get("/api/status/healthcheck")

        # login (si tu as un user existant dans la DB de test)
        # sinon, tu peux créer un user ici puis login.
        # NOTE: /token attend form-data OAuth2
        r = self.client.post(
            "/api/token",
            data={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if r.status_code == 200:
            self.token = r.json()["access_token"]
        else:
            self.token = None

    @task(6)
    def health(self):
        self.client.get("/api/status/healthcheck")

    @task(3)
    def csv_download(self):
        promo = random.choice(PROMOS)
        self.client.get("/api/csv", params={"promo_str": promo})

    @task(2)
    def ics_get_all(self):
        self.client.get("/api/ics/get_all")

    @task(1)
    def ics_insert_event(self):
        # nécessite elevated rights (teacher/su) -> token obligatoire
        if not self.token:
            return

        now = datetime.now(timezone.utc)
        start = now + timedelta(hours=random.randint(1, 48))
        end = start + timedelta(hours=2)

        payload = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "matiere": "Test",
            "type_cours": "CM",
            "infos_sup": "loadtest",
            "classroom_str": random.choice(CLASSROOMS),
            "user_id": 0,
            "promo_str": random.choice(PROMOS),
        }

        self.client.post(
            "/api/ics/insert",
            json=payload,
            headers={"Authorization": f"Bearer {self.token}"},
        )
