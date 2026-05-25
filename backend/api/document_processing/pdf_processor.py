

from typing import Literal, Any

from fastapi import UploadFile
from pydantic import BaseModel
import fitz
from pathlib import Path
import pandas as pd
import pdfplumber
from schemas.document import DocumentBlock



async def handle_pdf(file_path: Path)-> list[DocumentBlock]:
    # 这里可以使用 PDF 处理库来提取文本，例如 PyPDF2、pdfminer 等
    blocks:list[DocumentBlock] = []

    blocks.extend(extract_text_from_pdf(file_path))
    blocks.extend(extract_tables_from_pdf(file_path))
    blocks.extend(extract_images_from_pdf(file_path))
    return blocks

def extract_text_from_pdf(file_path: Path) -> list[DocumentBlock]:
    blocks:list[DocumentBlock] = []

    with pdfplumber.open(file_path) as pdf:
        for page_index, page in enumerate(pdf.pages,start=1):
            text = page.extract_text()
            blocks.append(DocumentBlock(type="text", page=page_index, content=text or "", metadata={}))
    # 这里可以使用 PDF 处理库来提取文本，例如 PyPDF2、pdfminer 等
    return blocks

def extract_tables_from_pdf(file_path: Path) -> list[DocumentBlock]:
    blocks:list[DocumentBlock] = []

    with pdfplumber.open(file_path) as pdf:
        for page_index, page in enumerate(pdf.pages,start=1):
            tables = page.extract_tables()
            for table_index, table in enumerate(tables, start=1):
                if not table:
                    continue
                df = pd.DataFrame(table[1:], columns=table[0])
                markdown_table = df.to_markdown(index=False)
                blocks.append(DocumentBlock(type="table", page=page_index, content=markdown_table, metadata={
                    "table_index": table_index,
                    "rows": len(df),
                    "columns": len(df.columns),
                }))
    # 这里可以使用 PDF 处理库来提取表格，例如 Camelot、Tabula 等
    return blocks

def extract_images_from_pdf(file_path: Path) -> list[DocumentBlock]:
    blocks:list[DocumentBlock] = []
    image_dir = Path("extracted_images")
    image_dir.mkdir(exist_ok=True)
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            images = page.get_images(full=True)
            for image_index, image in enumerate(images, start=1):
                xref = image[0]
                image_data = doc.extract_image(xref)
                image_bytes = image_data["image"]
                image_ext = image_data["ext"]
                image_path = image_dir/f"{file_path.name}_page{page_index+1}_image{image_index}.{image_ext}"
                image_path.write_bytes(image_bytes)
                blocks.append(DocumentBlock(type="image", page=page_index+1, content=str(image_path), metadata={
                    "image_index": image_index,
                    "extension": image_ext,
                }))
    finally:        doc.close()
            
    # 这里可以使用 PDF 处理库来提取图片，例如 PyMuPDF、pdf2image 等
    return blocks