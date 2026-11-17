
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from content_templates import CONTENT_MODELS, PROMPTS, VideoClassification


class TemporaryGeminiError(RuntimeError):
    pass


class AISummarizer:
    def __init__(self, api_key=None, model=None, max_attempts=2):
        load_dotenv()

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL")
        self.fallback_model = os.getenv("GEMINI_FALLBACK_MODEL")
        self.max_attempts = max_attempts

        if not self.api_key:
            raise ValueError(
                "Gemini API key missing. Add GEMINI_API_KEY to .env."
            )

        if not self.model or self.model == "your_available_gemini_model":
            raise ValueError(
                "Set GEMINI_MODEL in .env to a model available to your API key."
            )

        # Avoid trying the same model twice.
        if self.fallback_model == self.model:
            self.fallback_model = None

        # Request timeout is configured in milliseconds.
        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(timeout=120000)
        )

    @staticmethod
    def _temporary(exc):
        msg = str(exc).lower()

        temporary_errors = (
            "503",
            "unavailable",
            "high demand",
            "429",
            "resource_exhausted",
            "rate limit",
            "500",
            "502",
            "504",
            "temporarily",
            "internal error",
            "timeout",
            "timed out",
        )

        return any(error in msg for error in temporary_errors)

    def _request(self, prompt, schema, callback=None, stage="Gemini"):
        models_to_try = [self.model]

        if self.fallback_model:
            models_to_try.append(self.fallback_model)

        last_error = None

        for model_index, current_model in enumerate(models_to_try):

            for attempt in range(1, self.max_attempts + 1):
                try:
                    if callback:
                        callback(
                            f"{stage}: {current_model} "
                            f"(attempt {attempt}/{self.max_attempts})"
                        )

                    response = self.client.models.generate_content(
                        model=current_model,
                        contents=prompt,
                        config={
                            "response_mime_type": "application/json",
                            "response_schema": schema,
                            "temperature": 0.2,
                        },
                    )

                    if not response.text:
                        raise RuntimeError(
                            "Gemini returned an empty response."
                        )

                    return schema.model_validate_json(response.text)

                except Exception as exc:
                    last_error = exc

                    if not self._temporary(exc):
                        raise RuntimeError(
                            f"Gemini request failed using {current_model}. "
                            f"Check API key, model access and quota. {exc}"
                        ) from exc

                    if attempt < self.max_attempts:
                        delay = 2 ** attempt

                        if callback:
                            callback(
                                f"{current_model} is temporarily busy. "
                                f"Retrying in {delay} seconds..."
                            )

                        time.sleep(delay)

            # Primary model failed after retries.
            # Try the fallback model if one is configured.
            if model_index + 1 < len(models_to_try):
                if callback:
                    callback(
                        f"{current_model} is unavailable. "
                        f"Switching to {models_to_try[model_index + 1]}..."
                    )

        raise TemporaryGeminiError(
            "Gemini was unavailable using all configured models. "
            "Your transcript remains cached. Please retry later. "
            f"Last error: {last_error}"
        ) from last_error

    @staticmethod
    def _text(transcript):
        if not transcript or not transcript.strip():
            raise ValueError("Transcript is empty.")

        if len(transcript) > 100000:
            half = 50000
            return (
                transcript[:half]
                + "\n[Middle omitted: transcript too long]\n"
                + transcript[-half:]
            )

        return transcript

    def classify(self, transcript, callback=None):
        text = self._text(transcript)[:8000]

        prompt = (
            "Choose exactly one category: education, entertainment, "
            "technical_tutorial, podcast_interview, news_current_affairs, "
            "documentary, general. "
            "Base this on transcript meaning, not audio language. "
            "Choose general if uncertain. "
            "Return confidence and a short reason.\n\n"
            "TRANSCRIPT:\n"
            + text
        )

        return self._request(
            prompt,
            VideoClassification,
            callback,
            "Classifying video",
        )

    def generate_category_content(
        self, transcript, category, callback=None
    ):
        category = (
            category if category in CONTENT_MODELS else "general"
        )

        prompt = (
            "Create accurate English content using only the transcript. "
            "If details are absent, use empty lists or say unclear; "
            "do not invent facts.\n"
            "CATEGORY: "
            + category
            + "\nTASK: "
            + PROMPTS[category]
            + "\n\nTRANSCRIPT:\n"
            + self._text(transcript)
        )

        return self._request(
            prompt,
            CONTENT_MODELS[category],
            callback,
            "Generating tailored notes",
        )


