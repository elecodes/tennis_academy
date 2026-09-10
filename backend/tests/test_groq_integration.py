import os
import sys
import unittest
from dotenv import load_dotenv

# Load env variables including GROQ_API_KEY
load_dotenv()

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ai.magic_draft import generate_email_draft


class TestGroqIntegration(unittest.TestCase):
    def setUp(self):
        # Verify GROQ_API_KEY is present
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            self.skipTest("GROQ_API_KEY is not configured in the environment.")

    def test_real_generate_email_draft_groq(self):
        # We perform a real, unmocked API call to Groq
        message_type = "coach_delay"
        notes = "Hey, running late by 15 mins due to traffic. Start warming up!"

        result = generate_email_draft(message_type, notes)

        # Print the actual model response for manual inspection
        print("\n--- Real Groq Response ---")
        print(f"Subject: {result.get('subject')}")
        print(f"Content: {result.get('content')}")
        print("--------------------------")

        # Assertions
        self.assertIn("subject", result)
        self.assertIn("content", result)
        self.assertTrue(isinstance(result["subject"], str))
        self.assertTrue(isinstance(result["content"], str))
        self.assertGreater(len(result["subject"]), 0)
        self.assertGreater(len(result["content"]), 0)


if __name__ == "__main__":
    unittest.main()
