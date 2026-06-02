from dotenv import load_dotenv

load_dotenv()
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from services.ai.magic_draft import generate_email_draft, AIDraftProviderError


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

    @patch("services.ai.magic_draft.ai.generate")
    def test_generate_email_draft_raises_provider_error_on_invalid_json(
        self, mock_generate
    ):
        mock_result = MagicMock()
        mock_result.text = "not-json-response"

        async def mock_async_generate(*args, **kwargs):
            return mock_result

        mock_generate.side_effect = mock_async_generate

        with self.assertRaises(AIDraftProviderError):
            generate_email_draft("coach_delay", "I am running late")

    @patch("app.generate_email_draft")
    def test_api_draft_message_endpoint_admin(self, mock_service):
        mock_service.return_value = {
            "subject": "Mocked Subject",
            "content": "Mocked Content",
        }

        with self.app.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "admin"

        response = self.app.post(
            "/api/draft-message",
            json={"message_type": "coach_delay", "notes": "running late"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["subject"], "Mocked Subject")
        self.assertEqual(data["content"], "Mocked Content")

    @patch("app.generate_email_draft")
    def test_admin_api_draft_message_legacy_endpoint_admin(self, mock_service):
        mock_service.return_value = {
            "subject": "Legacy Subject",
            "content": "Legacy Content",
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
        self.assertEqual(data["subject"], "Legacy Subject")
        self.assertEqual(data["content"], "Legacy Content")

    @patch("app.generate_email_draft")
    def test_api_draft_message_endpoint_coach(self, mock_service):
        mock_service.return_value = {
            "subject": "Mocked Subject Coach",
            "content": "Mocked Content Coach",
        }

        with self.app.session_transaction() as sess:
            sess["user_id"] = 2
            sess["role"] = "coach"

        response = self.app.post(
            "/api/draft-message",
            json={"message_type": "coach_delay", "notes": "running late"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["subject"], "Mocked Subject Coach")
        self.assertEqual(data["content"], "Mocked Content Coach")

    def test_api_draft_message_endpoint_family_denied(self):
        with self.app.session_transaction() as sess:
            sess["user_id"] = 3
            sess["role"] = "family"

        response = self.app.post(
            "/api/draft-message",
            json={"message_type": "coach_delay", "notes": "running late"},
        )

        # Redirect to dashboard because family is not coach/admin
        self.assertEqual(response.status_code, 302)

    @patch("app.generate_email_draft")
    def test_api_draft_message_returns_503_when_ai_unavailable(self, mock_service):
        from services.ai.magic_draft import AIDraftUnavailableError

        mock_service.side_effect = AIDraftUnavailableError("missing ai config")

        with self.app.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "admin"

        response = self.app.post(
            "/api/draft-message",
            json={"message_type": "coach_delay", "notes": "running late"},
        )

        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("app.generate_email_draft")
    def test_api_draft_message_returns_502_on_provider_error(self, mock_service):
        from services.ai.magic_draft import AIDraftProviderError

        mock_service.side_effect = AIDraftProviderError("provider down")

        with self.app.session_transaction() as sess:
            sess["user_id"] = 2
            sess["role"] = "coach"

        response = self.app.post(
            "/api/draft-message",
            json={"message_type": "coach_delay", "notes": "running late"},
        )

        self.assertEqual(response.status_code, 502)
        data = response.get_json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
