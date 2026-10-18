from abc import ABC, abstractmethod


class ChatProvider(ABC):
    """The only interface the pipeline depends on: prompt in, text out."""

    name = "base"

    @abstractmethod
    def complete(self, prompt: str) -> str:
        raise NotImplementedError
