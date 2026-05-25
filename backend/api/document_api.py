
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from services.document_service import process_upload_file
from schemas.document import DocumentUploadResponse


router = APIRouter(prefix="/documents", tags=["documents"])

ALLOW_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx", ".md", ".csv"}
PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}

MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB



@router.post("/upload", response_model= DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    file_extension = Path(file.filename).suffix.lower() if file.filename else ""
    if not file_extension:
        raise HTTPException(status_code=400, detail="File extension is missing")
    if file_extension not in ALLOW_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
    content = await file.read()
    await file.seek(0)  # 重置文件指针，以便后续处理
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large; maximum size is {MAX_UPLOAD_SIZE} bytes",
        )

    if file_extension == ".pdf":
        if file.content_type not in PDF_CONTENT_TYPES:
            raise HTTPException(status_code=422, detail="Invalid PDF content-type")
        if not content.startswith(b"%PDF-"):
            raise HTTPException(status_code=422, detail="Invalid PDF file")

    try:
        document_id,file_path,blocks = await process_upload_file(file, file_extension)
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    # 这里可以添加文件处理逻辑，例如保存文件、提取文本等
    return DocumentUploadResponse(document_id=document_id, file_path=file_path, message="File uploaded and processed successfully", code=200)
