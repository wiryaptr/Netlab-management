import io
import json
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthAndImportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="Rahasia123!"
        )

    def test_auth_flow(self):
        # 1. CSRF
        res = self.client.get("/api/v1/auth/csrf/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("csrf_token", res.json())

        # 2. Login
        res = self.client.post(
            "/api/v1/auth/login/",
            data=json.dumps({"username": "admin", "password": "Rahasia123!"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["user"]["username"], "admin")

        csrf_token = self.client.cookies["csrftoken"].value

        # 3. Me
        res = self.client.get("/api/v1/auth/me/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["username"], "admin")

        # 4. Import CSV Preview
        csv_data = b"name,location_type,description\nLab C,room,Ruang praktikum C\n"
        f = io.BytesIO(csv_data)
        f.name = "locations.csv"
        res = self.client.post(
            "/api/v1/imports/",
            data={"file": f, "resource": "locations", "mode": "preview"},
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["summary"]["valid"], 1)

        # 5. Import CSV Commit
        f = io.BytesIO(csv_data)
        f.name = "locations.csv"
        res = self.client.post(
            "/api/v1/imports/",
            data={"file": f, "resource": "locations", "mode": "commit"},
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["created"], 1)

        # 6. Logout
        res = self.client.post("/api/v1/auth/logout/", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(res.status_code, 204)

        # 7. Me after logout
        res = self.client.get("/api/v1/auth/me/")
        self.assertEqual(res.status_code, 403)
