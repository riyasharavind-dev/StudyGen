from typing import Optional

from google import genai

from .base import BaseProvider


class GeminiProvider(BaseProvider):

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: Optional[str] = None,
    ):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url=base_url,
        )

        self.client = genai.Client(
            api_key=api_key
        )

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
    ) -> str:

        selected_model = (
            model or self.model
        )

        if not selected_model:
            selected_model = "gemini-3.6-flash"

        interaction = self.client.interactions.create(
            model=selected_model,
            input=prompt,
        )

        output_text = getattr(
            interaction,
            "output_text",
            None,
        )

        if not output_text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return output_text