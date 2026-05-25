
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from services.document_service import process_upload_file
from schemas.document import DocumentUploadResponse


router = APIRouter(prefix="/documents", tags=["documents"])

ALLOW_EXTENSIONS = [".pdf", ".txt", ".doc", ".docx", ".md", ".csv"]

MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB



@router.post("/upload", response_model= DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}, content type: {file.content_type}")
    file_extension = Path(file.filename).suffix.lower() if file.filename else ""
    if not file_extension:
        return DocumentUploadResponse(message="File extension is missing", code=400)
    if file_extension not in ALLOW_EXTENSIONS:
        return DocumentUploadResponse(message=f"Unsupported file type: {file_extension}", code=400)
    content = await file.read()
    await file.seek(0)  # 重置文件指针，以便后续处理
    if not content:
        return DocumentUploadResponse(message="File is empty", code=400)
    if len(content) > MAX_UPLOAD_SIZE:
        return DocumentUploadResponse(message=f"File size exceeds the maximum limit of {MAX_UPLOAD_SIZE} bytes", code=400)
    try:
        document_id,file_path,blocks = await process_upload_file(file, file_extension)
    except FileExistsError as e:
        print(f"File already exists: {e}")
        return DocumentUploadResponse(message=str(e), code=409)
    print(f"Saved file to11111: {file_path}")
    # 这里可以添加文件处理逻辑，例如保存文件、提取文本等
    return DocumentUploadResponse(document_id=document_id, file_path=file_path, message="File uploaded and processed successfully", code=200)

