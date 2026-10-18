import os

PROVIDERS = ("mock", "openai", "anthropic", "ollama")


def _ids(var):
    return [x.strip() for x in os.getenv(var, "").split(",") if x.strip()]


def get_provider(name=None):
    """Select a provider by name or the TRIAGE_PROVIDER env var (default: mock)."""
    name = (name or os.getenv("TRIAGE_PROVIDER", "mock")).lower()
    if name == "mock":
        from .mock import MockProvider
        return MockProvider(fail_first=_ids("TRIAGE_MOCK_FAIL_FIRST"),
                            always_fail=_ids("TRIAGE_MOCK_ALWAYS_FAIL"))
    if name == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider()
    if name == "anthropic":
        from .anthropic_provider import AnthropicProvider
        return AnthropicProvider()
    if name == "ollama":
        from .ollama_provider import OllamaProvider
        return OllamaProvider()
    raise ValueError(f"Unknown provider {name!r}. Choose from: {', '.join(PROVIDERS)}")
