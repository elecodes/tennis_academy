import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from asgiref.sync import async_to_sync

load_dotenv()

try:
    from genkit.ai import Genkit
    from genkit.plugins.google_genai import GoogleAI

    # Initialize Genkit with the Google AI plugin
    # googleai/gemini-2.5-flash-lite is the stable free-tier model in 2026
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_GENAI_API_KEY")
    ai = Genkit(
        plugins=[GoogleAI(api_key=api_key)],
        model="googleai/gemini-2.5-flash-lite",
    )
    GENKIT_AVAILABLE = True
except ImportError:
    GENKIT_AVAILABLE = False
    ai = None


class DraftInput(BaseModel):
    message_type: str = Field(
        description="Type of the message (e.g., coach_delay, etc)"
    )
    notes: str = Field(description="Rough notes or talking points for the email")


class DraftOutput(BaseModel):
    subject: str = Field(description="Professional email subject line")
    content: str = Field(description="Professional email body content")


def generate_email_draft(message_type: str, notes: str):
    """
    Generates a professional email draft using Genkit and Gemini 2.5 Flash-Lite.
    """
    if not GENKIT_AVAILABLE:
        raise Exception("AI draft feature not available - genkit not installed")

    prompt = f"""Act as a professional administrator for SF TENNIS KIDS Club.
You are writing an email of type: {message_type}.
Take these rough notes and write a VERY CONCISE email. 
Notes: {notes}
STRICT RULE: Maximum 2-3 sentences. Be direct, warm, and professional. Avoid any fluff or filler."""

    # Generate structured draft using the JSON schema
    result = async_to_sync(ai.generate)(
        prompt=prompt,
        output={"schema": DraftOutput.model_json_schema(), "format": "json"},
    )

    if not result.text:
        raise Exception("Failed to generate draft text from AI.")

    try:
        # Standard Pydantic validation from JSON
        parsed_output = DraftOutput.model_validate_json(result.text)
        return {"subject": parsed_output.subject, "content": parsed_output.content}
    except Exception:
        # Fallback if raw JSON has markdown block or is slightly malformed
        clean_text = result.text.replace("```json", "").replace("```", "").strip()
        parsed_output = DraftOutput.model_validate_json(clean_text)
        return {"subject": parsed_output.subject, "content": parsed_output.content}
