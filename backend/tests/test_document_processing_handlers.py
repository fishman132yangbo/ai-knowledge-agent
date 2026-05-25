import asyncio
from pathlib import Path

from api.document_processing.handlers import handle_csv, handle_markdown, handle_text, process_file
from schemas.document import DocumentBlock


def test_process_file_accepts_suffix_with_dot(tmp_path: Path) -> None:
    file_path = tmp_path / "note.txt"
    file_path.write_text("hello", encoding="utf-8")

    blocks = asyncio.run(process_file(file_path, ".txt"))

    assert isinstance(blocks, list)
    assert blocks == [DocumentBlock(type="text", page=1, content="hello")]


def test_text_and_markdown_handlers_return_document_blocks(tmp_path: Path) -> None:
    text_path = tmp_path / "note.txt"
    markdown_path = tmp_path / "note.md"
    text_path.write_text("hello text", encoding="utf-8")
    markdown_path.write_text("# hello markdown", encoding="utf-8")

    text_blocks = asyncio.run(handle_text(text_path))
    markdown_blocks = asyncio.run(handle_markdown(markdown_path))

    assert text_blocks == [DocumentBlock(type="text", page=1, content="hello text")]
    assert markdown_blocks == [
        DocumentBlock(type="text", page=1, content="# hello markdown")
    ]


def test_csv_handler_returns_table_block(tmp_path: Path) -> None:
    file_path = tmp_path / "data.csv"
    file_path.write_text("name,score\nalice,10\n", encoding="utf-8")

    blocks = asyncio.run(handle_csv(file_path))

    assert len(blocks) == 1
    assert blocks[0].type == "table"
    assert blocks[0].page == 1
    assert "alice" in blocks[0].content
