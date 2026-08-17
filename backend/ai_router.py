import time
from dataclasses import dataclass
from typing import Optional

from provider_manager import ProviderManager


@dataclass
class ProviderState:

    failures: int = 0

    cooldown_until: float = 0.0

    available: bool = True

    last_error: Optional[str] = None


class AIRouter:

    def __init__(self):

        self.manager = ProviderManager()

        # Default priority.
        # Actual provider priority from ProviderConfig
        # is used when providers are configured.

        self.default_priority = [
            "gemini",
            "openai",
            "openrouter",
        ]

        self.states = {
            provider: ProviderState()
            for provider in self.default_priority
        }

        # Initial cooldown.

        self.base_cooldown_seconds = 30

        # Maximum cooldown.

        self.max_cooldown_seconds = 300


    # =====================================================
    # GET / CREATE PROVIDER STATE
    # =====================================================

    def _get_state(
        self,
        provider_name: str,
    ) -> ProviderState:

        if provider_name not in self.states:

            self.states[
                provider_name
            ] = ProviderState()

        return self.states[
            provider_name
        ]


    # =====================================================
    # CHECK AVAILABILITY
    # =====================================================

    def _is_available(
        self,
        provider_name: str,
    ) -> bool:

        state = self._get_state(
            provider_name
        )

        now = time.time()


        # Cooldown expired.

        if (
            state.cooldown_until > 0
            and
            now >= state.cooldown_until
        ):

            state.available = True

            state.cooldown_until = 0.0

            state.last_error = None


        return state.available


    # =====================================================
    # MARK FAILURE
    # =====================================================

    def _mark_failure(
        self,
        provider_name: str,
        error: Exception,
    ):

        state = self._get_state(
            provider_name
        )

        state.failures += 1

        state.available = False

        state.last_error = str(
            error
        )


        # Exponential cooldown:
        #
        # failure 1 → 30 sec
        # failure 2 → 60 sec
        # failure 3 → 120 sec
        # failure 4 → 240 sec
        # failure 5+ → 300 sec

        cooldown = min(
            self.base_cooldown_seconds
            *
            (2 ** (state.failures - 1)),

            self.max_cooldown_seconds,
        )


        state.cooldown_until = (
            time.time()
            +
            cooldown
        )


    # =====================================================
    # MARK SUCCESS
    # =====================================================

    def _mark_success(
        self,
        provider_name: str,
    ):

        state = self._get_state(
            provider_name
        )

        state.failures = 0

        state.available = True

        state.cooldown_until = 0.0

        state.last_error = None


    # =====================================================
    # PROVIDER ORDER
    # =====================================================

    def _get_provider_order(
        self,
        preferred_provider: Optional[str] = None,
    ):

        configs = (
            self.manager.get_priority_order()
        )


        configured_names = [
            config.name.lower()
            for config in configs
        ]


        # If there are no configured
        # providers, return empty list.

        if not configured_names:

            return []


        order = configured_names.copy()


        # Preferred provider gets first priority.

        if preferred_provider:

            preferred = (
                preferred_provider
                .strip()
                .lower()
            )

            if preferred in order:

                order.remove(
                    preferred
                )

                order.insert(
                    0,
                    preferred
                )


        return order


    # =====================================================
    # GENERATE
    # =====================================================

    def generate(
        self,
        prompt: str,
        preferred_provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> dict:

        if not prompt or not prompt.strip():

            return {
                "success": False,
                "provider": None,
                "model": model,
                "response": None,
                "errors": [
                    {
                        "provider": None,
                        "error":
                            "Prompt cannot be empty.",
                    }
                ],
            }


        providers = self._get_provider_order(
            preferred_provider
        )


        if not providers:

            return {
                "success": False,
                "provider": None,
                "model": model,
                "response": None,
                "errors": [
                    {
                        "provider": None,
                        "error":
                            "No enabled AI providers are configured.",
                    }
                ],
            }


        errors = []


        # =================================================
        # TRY PROVIDERS
        # =================================================

        for provider_name in providers:


            # ---------------------------------------------
            # SKIP COOLDOWN
            # ---------------------------------------------

            if not self._is_available(
                provider_name
            ):

                state = self._get_state(
                    provider_name
                )


                remaining = max(
                    0,
                    int(
                        state.cooldown_until
                        -
                        time.time()
                    ),
                )


                errors.append({

                    "provider":
                        provider_name,

                    "error":
                        (
                            "Provider is in "
                            f"cooldown for "
                            f"{remaining}s."
                        ),

                })


                continue


            # ---------------------------------------------
            # GET PROVIDER
            # ---------------------------------------------

            try:

                provider = (
                    self.manager.get_provider(
                        provider_name
                    )
                )

            except Exception as error:

                self._mark_failure(
                    provider_name,
                    error,
                )


                errors.append({

                    "provider":
                        provider_name,

                    "error":
                        str(error),

                })


                continue


            # ---------------------------------------------
            # GENERATE
            # ---------------------------------------------

            try:

                response = provider.generate(

                    prompt=prompt,

                    model=model,

                )


                # Successful provider.

                self._mark_success(
                    provider_name
                )


                return {

                    "success": True,

                    "provider":
                        provider_name,

                    "model":
                        model or
                        getattr(
                            provider,
                            "model",
                            None,
                        ),

                    "response":
                        response,

                    "failover": (
                        len(errors) > 0
                    ),

                    "attempts":
                        len(errors) + 1,

                    "errors":
                        errors,

                }


            except Exception as error:

                # Provider failed.

                self._mark_failure(
                    provider_name,
                    error,
                )


                errors.append({

                    "provider":
                        provider_name,

                    "error":
                        str(error),

                })


                # IMPORTANT:
                #
                # Do not return here.
                #
                # Continue to the next provider.

                continue


        # =================================================
        # ALL PROVIDERS FAILED
        # =================================================

        return {

            "success": False,

            "provider": None,

            "model": model,

            "response": None,

            "failover": (
                len(errors) > 1
            ),

            "attempts":
                len(errors),

            "errors":
                errors,

        }


    # =====================================================
    # STATUS
    # =====================================================

    def status(self):

        result = {}


        # Make sure configured providers
        # also have state objects.

        for config in (
            self.manager.get_configs()
        ):

            name = config.name.lower()

            self._get_state(name)


        # Include built-in providers even
        # if not configured.

        for name in self.default_priority:

            self._get_state(name)


        for name, state in (
            self.states.items()
        ):

            config = (
                self.manager.registry.get(
                    name
                )
            )


            # ---------------------------------------------
            # NOT CONFIGURED
            # ---------------------------------------------

            if config is None:

                result[name] = {

                    "configured":
                        False,

                    "enabled":
                        False,

                    "available":
                        False,

                    "failures":
                        state.failures,

                    "cooldown_remaining":
                        0,

                }

                continue


            # ---------------------------------------------
            # COOLDOWN
            # ---------------------------------------------

            cooldown_remaining = max(

                0,

                int(
                    state.cooldown_until
                    -
                    time.time()
                ),

            )


            # ---------------------------------------------
            # STATUS
            # ---------------------------------------------

            result[name] = {

                "configured":
                    True,

                "enabled":
                    config.enabled,

                "available":
                    (
                        config.enabled
                        and
                        self._is_available(
                            name
                        )
                    ),

                "failures":
                    state.failures,

                "cooldown_remaining":
                    cooldown_remaining,

                "priority":
                    config.priority,

                "last_error":
                    state.last_error,

            }


        return result