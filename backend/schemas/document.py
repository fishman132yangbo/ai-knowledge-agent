

from typing import Literal, Any
from pathlib import Path
from pydantic import BaseModel

class DocumentBlock(BaseModel):
    type: Literal["text", "table", "image"]
    page: int
    content: str
    metadata: dict[str, Any] = {}
    
class DocumentUploadResonse(BaseModel):
    document_id: str | None = None
    file_path: Path | None = None
    code: int | None = None
    message: str | None = None