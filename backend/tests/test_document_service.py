from io import BytesIO

import pytest
from fastapi import UploadFile

from services import document_service
from storage import local_storage


@pytest.mark.asyncio
async def test_process_upload_file_removes_saved_file_when_processing_fails(
    monkeypatch, tmp_path
) -> None:
    async def fail_processing(file_path, file_extension):
        raise ValueError("cannot parse file")

    monkeypatch.setattr(local_storage, "STORAGE_ROOT", tmp_path)
    monkeypatch.setattr(document_service, "process_file", fail_processing)

    upload = UploadFile(filename="broken.txt", file=BytesIO(b"broken"))

    with pytest.raises(ValueError, match="cannot parse file"):
        await document_service.process_upload_file(upload, ".txt")

    assert list(tmp_path.iterdir()) == []
