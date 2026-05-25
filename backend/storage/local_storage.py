
import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile


STORAGE_ROOT = Path("storage_data/documents")

async def save_file(file: UploadFile) -> tuple[str, Path]:
    """保存上传的文件到本地，并返回文件的 MD5 哈希和保存路径。"""
    content = await file.read()
    file_md5 = hashlib.md5(content).hexdigest()


    document_id = f"doc_{file_md5}"
    document_dir = STORAGE_ROOT/document_id

    filename = Path(file.filename or "uploaded_file").name
    file_path = document_dir/filename
    if file_path.exists() and file_path.stat().st_size == len(content):
        raise FileExistsError(f"File with the same content already exists: {file_path}")
    
    document_dir.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)
    print(f"Saved file to: {file_path}")
    return document_id, file_path