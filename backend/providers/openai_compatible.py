import httpx

from providers.base import AIProvider


class OpenAICompatibleProvider(AIProvider):

    def __init__(
        self,
        provider_name: str,
        api_key: str,
        base_url: str,
        default_model: str,
    ):
        self.provider_name = provider_name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    @property
    def name(self) -> str:
        return self.provider_name

    def generate(
        self,
        prompt: str,
        model: str | None = None,
    ) -> str:

        selected_model = model or self.default_model

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": selected_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        response = httpx.post(
            url,
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code >= 400:
            raise RuntimeError(
                f"{self.provider_name} returned "
                f"{response.status_code}: {response.text}"
            )

        data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise RuntimeError(
                f"{self.provider_name} returned an unexpected response."
            )

        if not content:
            raise RuntimeError(
                f"{self.provider_name} returned an empty response."
            )

        return content

    def health_check(self) -> bool:
        return bool(self.api_key)