import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from services.ai.magic_draft import generate_email_draft


class TestAIServiceRefactor(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("services.ai.magic_draft.ai.generate")
    def test_generate_email_draft_service(self, mock_generate):
        # Mocking the async generate call
        mock_result = MagicMock()
        mock_result.text = '{"subject": "Test Subject", "content": "Test Content"}'

        # We need to mock the async behavior as generate is called within async_to_sync

        async def mock_async_generate(*args, **kwargs):
            return mock_result

        mock_generate.side_effect = mock_async_generate

        result = generate_email_draft("coach_delay", "I am running late")

        self.assertEqual(result["subject"], "Test Subject")
        self.assertEqual(result["content"], "Test Content")

    @patch("app.generate_email_draft")
    def test_admin_draft_message_endpoint(self, mock_service):
        mock_service.return_value = {
            "subject": "Mocked Subject",
            "content": "Mocked Content",
        }

        with self.app.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "admin"

        response = self.app.post(
            "/admin/api/draft-message",
            json={"message_type": "coach_delay", "notes": "running late"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["subject"], "Mocked Subject")
        self.assertEqual(data["content"], "Mocked Content")


if __name__ == "__main__":
    unittest.main()
