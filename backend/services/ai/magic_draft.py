import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from asgiref.sync import async_to_sync

load_dotenv()


class AIDraftError(Exception):
    """Base error for AI draft generation failures."""


class AIDraftUnavailableError(AIDraftError):
    """Raised when AI draft cannot run due to configuration/runtime setup."""


class AIDraftProviderError(AIDraftError):
    """Raised when upstream AI provider call fails."""


try:
    from groq import Groq
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key:
        groq_client = Groq(api_key=groq_api_key)
    else:
        groq_client = None
except Exception:
    groq_client = None


try:
    from genkit.ai import Genkit
    from genkit.plugins.google_genai import GoogleAI

    # Initialize Genkit with the Google AI plugin
    # googleai/gemini-2.5-flash-lite is the stable free-tier model in 2026
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_GENAI_API_KEY")
    if not api_key:
        GENKIT_AVAILABLE = False
        ai = None
    else:
        ai = Genkit(
            plugins=[GoogleAI(api_key=api_key)],
            model="googleai/gemini-2.5-flash-lite",
        )
        GENKIT_AVAILABLE = True
except Exception:
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
    Generates a professional email draft using Groq (primary) or Genkit and Gemini.
    """
    prompt = f"""Act as a professional administrator for SF TENNIS KIDS Club.
You are writing an email of type: {message_type}.
Take these rough notes and write a VERY CONCISE email.
Notes: {notes}
STRICT RULE: Maximum 2-3 sentences. Be direct, warm, and professional. Avoid any fluff or filler."""

    if groq_client:
        # Try primary model first, fallback to llama options if failed
        models_to_try = ["openai/gpt-oss-120b", "llama-3.1-8b-instant", "llama3-8b-8192"]
        last_error = None
        for model in models_to_try:
            try:
                response = groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a professional administrator. You must output JSON only, "
                                "matching this schema exactly:\n"
                                "{\n"
                                "  \"subject\": \"Professional email subject line\",\n"
                                "  \"content\": \"Professional email body content\"\n"
                                "}"
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model=model,
                    response_format={"type": "json_object"},
                    temperature=0.7
                )
                text_content = response.choices[0].message.content
                if not text_content:
                    raise AIDraftProviderError(f"Groq model {model} returned empty response.")
                
                try:
                    parsed_output = DraftOutput.model_validate_json(text_content)
                    return {"subject": parsed_output.subject, "content": parsed_output.content}
                except Exception:
                    clean_text = text_content.replace("```json", "").replace("```", "").strip()
                    parsed_output = DraftOutput.model_validate_json(clean_text)
                    return {"subject": parsed_output.subject, "content": parsed_output.content}
            except Exception as e:
                last_error = e
                continue
        raise AIDraftProviderError(
            f"Failed to generate message draft from Groq after trying models {models_to_try}."
        ) from last_error

    if not GENKIT_AVAILABLE:
        raise AIDraftUnavailableError(
            "AI draft feature unavailable. Check Groq/Gemini API keys or installation."
        )

    # Generate structured draft using the JSON schema (Gemini Genkit fallback)
    try:
        result = async_to_sync(ai.generate)(
            prompt=prompt,
            output={"schema": DraftOutput.model_json_schema(), "format": "json"},
        )
    except Exception as e:
        raise AIDraftProviderError(
            "Failed to generate message draft from AI provider."
        ) from e

    if not result.text:
        raise AIDraftProviderError("Failed to generate draft text from AI.")

    try:
        # Standard Pydantic validation from JSON
        parsed_output = DraftOutput.model_validate_json(result.text)
        return {"subject": parsed_output.subject, "content": parsed_output.content}
    except Exception:
        # Fallback if raw JSON has markdown block or is slightly malformed
        clean_text = result.text.replace("```json", "").replace("```", "").strip()
        try:
            parsed_output = DraftOutput.model_validate_json(clean_text)
            return {"subject": parsed_output.subject, "content": parsed_output.content}
        except Exception as e:
            raise AIDraftProviderError(
                "AI provider returned an invalid draft format."
            ) from e
