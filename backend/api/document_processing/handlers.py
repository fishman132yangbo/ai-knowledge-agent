from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

import pandas as pd

from schemas.document import DocumentBlock
from .pdf_processor import handle_pdf


async def process_file(file_path: Path, file_extension: str) -> list[DocumentBlock]:
    # 这里可以根据文件类型进行不同的处理，例如保存文件、提取文本等
    handlers = {
        ".pdf": handle_pdf,
        ".txt": handle_text,
        ".doc": handle_doc,
        ".docx": handle_docx,
        ".md": handle_markdown,
        ".csv": handle_csv,
    }
    normalized_extension = _normalize_file_extension(file_extension)
    handler = handlers.get(normalized_extension)
    if handler is None:
        raise ValueError(f"No handler for file type: {normalized_extension}")
    return await handler(file_path)


async def handle_text(file_path: Path) -> list[DocumentBlock]:
    # 这里可以直接读取文本文件内容
    content = file_path.read_text(encoding="utf-8")
    return [DocumentBlock(type="text", page=1, content=content)]

async def handle_doc(file_path: Path) -> list[DocumentBlock]:
    # 这里可以使用 DOC 处理库来提取文本，例如 python-docx 等
    raise ValueError("Legacy .doc parsing is not implemented")

async def handle_docx(file_path: Path) -> list[DocumentBlock]:
    try:
        with ZipFile(file_path) as docx_file:
            document_xml = docx_file.read("word/document.xml")
    except (BadZipFile, KeyError) as exc:
        raise ValueError("Invalid DOCX file") from exc

    root = ElementTree.fromstring(document_xml)
    text_parts = [
        element.text
        for element in root.iter()
        if element.tag.endswith("}t") and element.text
    ]
    content = "\n".join(text_parts)
    return [DocumentBlock(type="text", page=1, content=content)]

async def handle_markdown(file_path: Path) -> list[DocumentBlock]:
    # 这里可以使用 Markdown 处理库来提取文本，例如 python-markdown 等
    content = file_path.read_text(encoding="utf-8")
    return [DocumentBlock(type="text", page=1, content=content)]

async def handle_csv(file_path: Path) -> list[DocumentBlock]:
    # 这里可以使用 CSV 处理库来提取文本，例如 pandas、csv 等
    dataframe = pd.read_csv(file_path)
    markdown_table = dataframe.to_markdown(index=False)
    return [
        DocumentBlock(
            type="table",
            page=1,
            content=markdown_table,
            metadata={
                "rows": len(dataframe),
                "columns": len(dataframe.columns),
            },
        )
    ]


def _normalize_file_extension(file_extension: str) -> str:
    normalized = file_extension.strip().lower()
    if not normalized.startswith("."):
        normalized = f".{normalized}"
    return normalized
