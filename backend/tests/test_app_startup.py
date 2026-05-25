import importlib
import sys


def test_main_import_does_not_require_llm_credentials(monkeypatch) -> None:
    for key in (
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_BASE_URL",
        "DEEPSEEK_MODEL_NAME",
        "OPENAI_API_KEY",
        "OPENAI_ADMIN_KEY",
    ):
        monkeypatch.delenv(key, raising=False)

    for module_name in ("main", "api.chat_api", "llm.client"):
        sys.modules.pop(module_name, None)

    importlib.import_module("main")
