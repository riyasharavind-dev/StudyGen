from typing import Dict

from provider_config import ProviderConfig


class ProviderRegistry:

    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}

    def register(self, config: ProviderConfig):
        self.providers[config.name] = config

    def remove(self, name: str):
        self.providers.pop(name, None)

    def get(self, name: str):
        return self.providers.get(name)

    def list(self):
        return list(self.providers.values())

    def enable(self, name: str):
        provider = self.get(name)

        if provider is None:
            raise ValueError(
                f"Provider '{name}' is not configured."
            )

        provider.enabled = True

    def disable(self, name: str):
        provider = self.get(name)

        if provider is None:
            raise ValueError(
                f"Provider '{name}' is not configured."
            )

        provider.enabled = False