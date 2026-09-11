from backend.app.ai.llm_provider import OpenAIProvider
from backend.app.core.config import settings


def test_nvidia_model_uses_nvidia_key_and_base_url(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "openai-key")
    monkeypatch.setattr(settings, "OPENAI_API_BASE", "")
    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "nvapi-key")
    monkeypatch.setattr(settings, "NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1")

    provider = OpenAIProvider(model_name="openai/nvidia/nemotron-3.5-lightning-30b-a3b")

    assert provider._resolve_api_config() == {
        "api_key": "nvapi-key",
        "api_base": "https://integrate.api.nvidia.com/v1",
    }


def test_plain_nvidia_model_name_is_normalized_for_litellm():
    provider = OpenAIProvider(model_name="nvidia/nemotron-3.5-lightning-30b-a3b")

    assert provider._completion_model_name() == "openai/nvidia/nemotron-3.5-lightning-30b-a3b"


def test_openai_compatible_base_can_be_set_directly(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "compatible-key")
    monkeypatch.setattr(settings, "OPENAI_API_BASE", "https://example.com/v1")
    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "")

    provider = OpenAIProvider(model_name="openai/custom-model")

    assert provider._resolve_api_config() == {
        "api_key": "compatible-key",
        "api_base": "https://example.com/v1",
    }
