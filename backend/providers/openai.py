from typing import Optional

import requests

from .base import BaseProvider


class OpenAIProvider(BaseProvider):

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

        self.base_url = (
            base_url.rstrip("/")
            if base_url
            else "https://api.openai.com/v1"
        )

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
    ) -> str:

        selected_model = (
            model or self.model
        )

        response = requests.post(
            f"{self.base_url}/chat/completions",

            headers={
                "Authorization":
                    f"Bearer {self.api_key}",

                "Content-Type":
                    "application/json",
            },

            json={
                "model": selected_model,

                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            },

            timeout=60,
        )

        if response.status_code >= 400:

            raise RuntimeError(
                f"OpenAI API error "
                f"{response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]

        except (
            KeyError,
            IndexError,
            TypeError,
        ):

            raise RuntimeError(
                "OpenAI returned an invalid response."
            )