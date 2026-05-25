

from pathlib import Path
import shutil

from fastapi import UploadFile
from schemas.document import DocumentBlock
from api.document_processing.handlers import process_file
from storage.local_storage import save_file
from .document_cleaner import clean_document_blocks


async def process_upload_file(file: UploadFile, file_extension: str) -> tuple[str, Path, list[DocumentBlock]]:
    """处理上传的文件，保存到本地，并返回文件的 MD5 哈希和保存路径。"""

    # 这里可以根据文件类型进行不同的处理，例如提取文本、清洗内容等
    # 目前先直接保存文件，后续可以在这里添加更多处理逻辑
    document_id, file_path = await save_file(file)
    try:
        blocks = await process_file(file_path, file_extension)
        blocks = clean_document_blocks(blocks)
    except Exception as exc:
        shutil.rmtree(file_path.parent, ignore_errors=True)
        raise ValueError(f"Failed to process uploaded file: {exc}") from exc
    return document_id, file_path, blocks
