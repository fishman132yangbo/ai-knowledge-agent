from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import document_api


def _client(raise_server_exceptions: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(document_api.router, prefix="/api")
    return TestClient(app, raise_server_exceptions=raise_server_exceptions)


def test_upload_accepts_supported_suffix(monkeypatch) -> None:
    async def process_uploaded_file(file, file_extension):
        assert file_extension == ".txt"
        assert await file.read() == b"hello"
        return "doc_123", Path("/tmp/note.txt"), []

    monkeypatch.setattr(document_api, "process_upload_file", process_uploaded_file)

    response = _client().post(
        "/api/documents/upload",
        files={"file": ("note.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["document_id"] == "doc_123"


def test_upload_rejects_filename_without_suffix() -> None:
    response = _client().post(
        "/api/documents/upload",
        files={"file": ("pdf", b"%PDF-1.4\n", "application/pdf")},
    )

    assert response.status_code == 400
    assert "extension" in response.json()["detail"].lower()


def test_upload_rejects_empty_file() -> None:
    response = _client().post(
        "/api/documents/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_rejects_oversized_file(monkeypatch) -> None:
    monkeypatch.setattr(document_api, "MAX_UPLOAD_SIZE", 4)

    response = _client().post(
        "/api/documents/upload",
        files={"file": ("large.pdf", b"%PDF-1.4\n", "application/pdf")},
    )

    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_upload_rejects_pdf_with_wrong_content_type() -> None:
    response = _client().post(
        "/api/documents/upload",
        files={"file": ("document.pdf", b"%PDF-1.4\n", "text/plain")},
    )

    assert response.status_code == 422
    assert "content-type" in response.json()["detail"].lower()


def test_upload_rejects_pdf_with_wrong_magic_header() -> None:
    response = _client(raise_server_exceptions=False).post(
        "/api/documents/upload",
        files={"file": ("document.pdf", b"not a pdf", "application/pdf")},
    )

    assert response.status_code == 422
    assert "pdf" in response.json()["detail"].lower()


def test_upload_maps_duplicate_file_to_409(monkeypatch) -> None:
    async def fail_duplicate(file, file_extension):
        raise FileExistsError("File already exists")

    monkeypatch.setattr(document_api, "process_upload_file", fail_duplicate)

    response = _client().post(
        "/api/documents/upload",
        files={"file": ("document.pdf", b"%PDF-1.4\n", "application/pdf")},
    )

    assert response.status_code == 409
    assert "exists" in response.json()["detail"].lower()


def test_upload_maps_processing_errors_to_422(monkeypatch) -> None:
    async def fail_processing(file, file_extension):
        raise ValueError("cannot parse file")

    monkeypatch.setattr(document_api, "process_upload_file", fail_processing)

    response = _client().post(
        "/api/documents/upload",
        files={"file": ("document.pdf", b"%PDF-1.4\n", "application/pdf")},
    )

    assert response.status_code == 422
    assert "parse" in response.json()["detail"].lower()
