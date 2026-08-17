from typing import Optional

from provider_store import ProviderStore
from provider_config import ProviderConfig

from providers import (
    BaseProvider,
    GeminiProvider,
    OpenAIProvider,
    OpenRouterProvider,
)



class ProviderManager:

    def __init__(self):

        self.store = ProviderStore()

        self.registry = {}

        self._load_providers()


    # =====================================================
    # LOAD PROVIDERS
    # =====================================================

    def _load_providers(self):

        self.registry.clear()

        configs = self.store.list_providers()

        for config in configs:

            self.registry[
                config.name.lower()
            ] = config


    # =====================================================
    # CREATE PROVIDER INSTANCE
    # =====================================================

    def _create_provider(
        self,
        config: ProviderConfig,
    ) -> BaseProvider:

        name = config.name.lower()

        if name == "gemini":

            return GeminiProvider(
                api_key=config.api_key,
                model=config.model,
                base_url=config.base_url,
            )


        if name == "openai":

            return OpenAIProvider(
                api_key=config.api_key,
                model=config.model,
                base_url=config.base_url,
            )


        if name == "openrouter":

            return OpenRouterProvider(
                api_key=config.api_key,
                model=config.model,
                base_url=config.base_url,
            )


        if name == "custom":

            return OpenAIProvider(
                api_key=config.api_key,
                model=config.model,
                base_url=config.base_url,
            )


        raise ValueError(
            f"Unsupported provider: {config.name}"
        )


    # =====================================================
    # GET PROVIDER
    # =====================================================

    def get_provider(
        self,
        provider_name: str,
    ) -> BaseProvider:

        name = provider_name.lower()

        config = self.registry.get(name)

        if config is None:

            raise ValueError(
                f"Provider '{provider_name}' is not configured."
            )


        if not config.enabled:

            raise ValueError(
                f"Provider '{provider_name}' is disabled."
            )


        return self._create_provider(config)


    # =====================================================
    # LIST PROVIDERS
    # =====================================================

    @property
    def providers(self):

        return {
            name: config
            for name, config
            in self.registry.items()
            if config.enabled
        }


    def list_providers(self):

        return [
            config.name
            for config in self.registry.values()
            if config.enabled
        ]


    # =====================================================
    # GET CONFIGS
    # =====================================================

    def get_configs(self):

        return list(
            self.registry.values()
        )


    # =====================================================
    # ADD PROVIDER
    # =====================================================

    def add_provider(
        self,
        name: str,
        api_key: str,
        model: str,
        base_url: Optional[str] = None,
        enabled: bool = True,
        priority: int = 10,
    ):

        name = name.strip().lower()


        if not name:

            raise ValueError(
                "Provider name is required."
            )


        if not api_key:

            raise ValueError(
                "API key is required."
            )


        if not model:

            raise ValueError(
                "Model is required."
            )


        if priority < 1:

            raise ValueError(
                "Priority must be at least 1."
            )


        config = ProviderConfig(

            name=name,

            api_key=api_key,

            model=model,

            base_url=base_url,

            enabled=enabled,

            priority=priority,

        )


        # Validate provider type before saving.

        self._create_provider(
            config
        )


        self.store.save_provider(
            config
        )


        self._load_providers()


        return config


    # =====================================================
    # ENABLE PROVIDER
    # =====================================================

    def enable_provider(
        self,
        provider_name: str,
    ):

        name = provider_name.lower()

        config = self.registry.get(name)


        if config is None:

            raise ValueError(
                f"Provider '{provider_name}' not found."
            )


        config.enabled = True


        self.store.save_provider(
            config
        )


        self._load_providers()


    # =====================================================
    # DISABLE PROVIDER
    # =====================================================

    def disable_provider(
        self,
        provider_name: str,
    ):

        name = provider_name.lower()

        config = self.registry.get(name)


        if config is None:

            raise ValueError(
                f"Provider '{provider_name}' not found."
            )


        config.enabled = False


        self.store.save_provider(
            config
        )


        self._load_providers()


    # =====================================================
    # REMOVE PROVIDER
    # =====================================================

    def remove_provider(
        self,
        provider_name: str,
    ):

        name = provider_name.lower()


        if name not in self.registry:

            raise ValueError(
                f"Provider '{provider_name}' not found."
            )


        self.store.delete_provider(
            name
        )


        self._load_providers()


    # =====================================================
    # SORT BY PRIORITY
    # =====================================================

    def get_priority_order(self):

        configs = [
            config
            for config in self.registry.values()
            if config.enabled
        ]


        configs.sort(
            key=lambda config:
                config.priority
        )


        return configs