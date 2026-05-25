import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "fastapi",
        "openai",
        "dotenv",
        "pdfplumber",
        "pandas",
        "fitz",
    ],
)
def test_runtime_dependencies_are_importable(module_name: str) -> None:
    importlib.import_module(module_name)


@pytest.mark.parametrize(
    "module_name",
    [
        "api.document_api",
        "api.document_processing.pdf_processor",
        "schemas.document",
        "services.document_cleaner",
        "services.document_service",
        "storage.local_storage",
    ],
)
def test_backend_modules_are_importable(module_name: str) -> None:
    importlib.import_module(module_name)
