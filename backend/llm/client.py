
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@lru_cache
def get_client() -> OpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("LLM API key is not configured")

    return OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL") or None,
    )


def get_model_name() -> str:
    model_name = os.getenv("DEEPSEEK_MODEL_NAME")
    if not model_name:
        raise RuntimeError("LLM model name is not configured")
    return model_name

