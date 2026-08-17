from abc import ABC, abstractmethod
from typing import Optional


class BaseProvider(ABC):

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
    ) -> str:
        pass