import os
import tempfile
import unittest

from fastapi.testclient import TestClient
from sqlmodel import SQLModel


_database_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_database_file.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_database_file.name}"

from backend.app.database import engine  # noqa: E402
from backend.app.main import app  # noqa: E402


class HabitApiTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        engine.dispose()
        os.unlink(_database_file.name)

    def setUp(self):
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
        self.client = TestClient(app)

    def test_complete_habit_flow(self):
        response = self.client.post(
            "/bot/register_user",
            params={"telegram_id": 42, "username": "matvey"},
        )
        self.assertEqual(response.status_code, 200)
        user_id = response.json()["id"]

        repeated = self.client.post(
            "/bot/register_user",
            params={"telegram_id": 42, "username": "matvey"},
        )
        self.assertEqual(repeated.json()["id"], user_id)

        habit = self.client.post(
            "/bot/add_habit",
            params={"user_id": user_id, "name": "Read"},
        )
        self.assertEqual(habit.status_code, 200)
        habit_id = habit.json()["id"]

        first_mark = self.client.post(
            "/bot/done",
            params={"user_id": user_id, "habit_id": habit_id},
        )
        second_mark = self.client.post(
            "/bot/done",
            params={"user_id": user_id, "habit_id": habit_id},
        )
        self.assertEqual(first_mark.json(), {"ok": True})
        self.assertEqual(second_mark.json()["ok"], False)

        habits = self.client.get(f"/users/{user_id}/habits").json()
        self.assertEqual(habits[0]["done_count"], 1)
        stats = self.client.get(f"/users/{user_id}/stats").json()
        self.assertEqual(stats, {"habits": 1, "done_last_7_days": 1})

    def test_unknown_user_and_habit_return_404(self):
        response = self.client.post(
            "/bot/add_habit",
            params={"user_id": 999, "name": "Missing"},
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            "/bot/done",
            params={"user_id": 999, "habit_id": 999},
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
