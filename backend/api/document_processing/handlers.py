from pathlib import Path
from .pdf_processor import handle_pdf


async def process_file(file_path: Path, file_extension: str):
    # 这里可以根据文件类型进行不同的处理，例如保存文件、提取文本等
    handlers = {
        ".pdf": handle_pdf,
        ".txt": handle_text,
        ".doc": handle_doc,
        ".docx": handle_doc,
        ".md": handle_markdown,
        ".csv": handle_csv,
    }
    handler = handlers.get(f".{file_extension}")
    if handler is None:
        raise ValueError(f"No handler for file type: .{file_extension}")
    return await handler(file_path)


async def handle_text(file_path: Path):
    # 这里可以直接读取文本文件内容
    with open(file_path, "r") as f:
        content = f.read()
    return f"Processed text file: {file_path.name}, content length: {len(content)}"

async def handle_doc(file_path: Path):
    # 这里可以使用 DOC 处理库来提取文本，例如 python-docx 等
    return f"Processed DOC file: {file_path.name}"

async def handle_markdown(file_path: Path):
    # 这里可以使用 Markdown 处理库来提取文本，例如 python-markdown 等
    return f"Processed Markdown file: {file_path.name}"

async def handle_csv(file_path: Path):
    # 这里可以使用 CSV 处理库来提取文本，例如 pandas、csv 等
    return f"Processed CSV file: {file_path.name}"

