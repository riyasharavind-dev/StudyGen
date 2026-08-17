from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderConfig:

    name: str

    api_key: str

    model: str

    base_url: Optional[str] = None

    enabled: bool = True

    priority: int = 10