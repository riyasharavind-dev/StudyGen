import json
from pathlib import Path

from provider_config import ProviderConfig


class ProviderStore:

    def __init__(self):

        self.data_directory = (
            Path(__file__).parent / "data"
        )

        self.data_directory.mkdir(
            exist_ok=True
        )

        self.file_path = (
            self.data_directory /
            "providers.json"
        )

        if not self.file_path.exists():
            self._write([])


    # =====================================================
    # READ
    # =====================================================

    def _read(self):

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if not isinstance(data, list):
                return []

            return data

        except (
            FileNotFoundError,
            json.JSONDecodeError,
        ):

            return []


    # =====================================================
    # WRITE
    # =====================================================

    def _write(self, data):

        temporary_file = (
            self.file_path.with_suffix(".tmp")
        )

        with open(
            temporary_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
            )

        temporary_file.replace(
            self.file_path
        )


    # =====================================================
    # LIST PROVIDERS
    # =====================================================

    def list_providers(self):

        data = self._read()

        providers = []

        for item in data:

            try:

                providers.append(
                    ProviderConfig(
                        name=item["name"],
                        api_key=item["api_key"],
                        model=item["model"],
                        base_url=item.get(
                            "base_url"
                        ),
                        enabled=item.get(
                            "enabled",
                            True,
                        ),
                        priority=item.get(
                            "priority",
                            10,
                        ),
                    )
                )

            except (
                KeyError,
                TypeError,
            ):

                continue

        return providers


    # =====================================================
    # SAVE PROVIDER
    # =====================================================

    def save_provider(
        self,
        config: ProviderConfig,
    ):

        data = self._read()

        updated = False

        for index, item in enumerate(data):

            if (
                item.get("name", "").lower()
                ==
                config.name.lower()
            ):

                data[index] = {
                    "name": config.name,
                    "api_key": config.api_key,
                    "model": config.model,
                    "base_url": config.base_url,
                    "enabled": config.enabled,
                    "priority": config.priority,
                }

                updated = True

                break

        if not updated:

            data.append({

                "name": config.name,

                "api_key": config.api_key,

                "model": config.model,

                "base_url": config.base_url,

                "enabled": config.enabled,

                "priority": config.priority,

            })

        self._write(data)


    # =====================================================
    # DELETE PROVIDER
    # =====================================================

    def delete_provider(
        self,
        provider_name: str,
    ):

        data = self._read()

        data = [

            item

            for item in data

            if item.get(
                "name",
                "",
            ).lower()
            !=
            provider_name.lower()

        ]

        self._write(data)