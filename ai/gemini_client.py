
import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from ai.ai_client import AIClient

class GeminiClient(AIClient):
    def __init__(self, model="gemini-3.5-flash-lite"):
        self._model = model
        self._client = None

    def connect(self):
        load_dotenv(override=True)

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from .env")

        try:
            self._client = genai.Client(api_key=api_key)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialise Gemini client: {e}"
            ) from e

    def generate(self, prompt):
        if self._client is None:
            raise RuntimeError("Gemini client is not connected")

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

        except errors.APIError as e:
            if getattr(e, "code", None) == 429:
                raise RuntimeError(
                    "Gemini API rate limit or quota exceeded. Please try again later."
                ) from e

            raise RuntimeError(
                f"Gemini API request failed: {e}"
            ) from e

        except (ConnectionError, TimeoutError) as e:
            raise RuntimeError(
                f"Unable to connect to Gemini: {e}"
            ) from e

        try:
            response_text = response.text
        except (ValueError, AttributeError) as e:
            raise RuntimeError(
                f"Unable to read Gemini response: {e}"
            ) from e

        if not isinstance(response_text, str) or not response_text.strip():
            raise RuntimeError("Gemini returned an empty response")

        return response_text
