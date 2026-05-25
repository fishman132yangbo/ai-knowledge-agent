import re

from schemas.document import DocumentBlock
from collections import Counter
from math import ceil


HEADER_FOOTER_SCAN_LINES = 3
REPEATED_LINE_MIN_RATO = 0.4

def clean_document_blocks(blocks:list[DocumentBlock]) -> list[DocumentBlock]:
    """清洗文档块，去除页眉页脚等无用内容。"""
    repeated_lines = _detect_repeated_header_footer_lines(blocks)
    cleaned_blocks: list[DocumentBlock] = []

    for block in blocks:
        if block.type == "image":
            cleaned_blocks.append(block)
            continue
        if block.type == "text":
            content = clean_text_block(block.content, repeated_lines)
        elif block.type == "table":
            content = clean_table_block(block.content, repeated_lines)
        else:
            content = block.content

        if not content.strip():
            continue
        cleaned_blocks.append(
            DocumentBlock(
                type=block.type,
                page=block.page,
                content=content,
                metadata=block.metadata,
            )
        )
    return cleaned_blocks

def clean_text_block(text: str, repeated_lines: set[str]) -> str:
    content = _normalize_newlines(text)
    lines = [_clean_line(line) for line in content.split("\n")]

    cleaned_lines: list[str] = []
    for line in lines:
        if not line:
            cleaned_lines.append("")
            continue
        line_key = _line_key(line)
        if line_key in repeated_lines:
            continue
        if _is_page_number_line(line):
            continue
        cleaned_lines.append(line)

    content = "\n".join(cleaned_lines)
    content = _merge_pdf_broken_lines(content)
    content = _collapse_blank_lines(content)
    return content.strip()

def _merge_pdf_broken_lines(text: str) -> str:

    lines = text.split("\n")
    merged: list[str] = []
    for line in lines:
        if not merged:
            merged.append(line)
            continue

        previous = merged[-1]
        if _should_merge_lines(previous, line):
            merged[-1] = f"{previous} {line}".strip()
        else:
            merged.append(line)
    return "\n".join(merged)

def _should_merge_lines(line1: str, line2: str) -> bool:
    if not line1 or not line2:
        return False
    if line1.endswith((".", "。", "!", "！", "?", "？", ":", "：", ";", "；")):
          return False

    if re.match(r"^(\d+\.|[-*•]|\([0-9a-zA-Z]+\))\s+", line2):
          return False

    if len(line1) < 8:
          return False
    return True

def _collapse_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)

def clean_table_block(table_markdown: str, repeated_lines: set[str]) -> str:
    content = _normalize_newlines(table_markdown)
    lines = []

    for line in content.split("\n"):
        if "|" in line:
            cells = [cell.strip() for cell in line.split("|")]
            lines.append(cells)
        else:
            lines.append(_clean_line(line))    
    
    return _collapse_blank_lines("\n".join(lines)).strip()

def _detect_repeated_header_footer_lines(blocks:list[DocumentBlock]) -> set[str]:
    text_blocks = [block for block in blocks if block.type == "text" and block.content.strip()]
    page_count = len({block.page for block in text_blocks})

    if page_count < 2:
        return set() 
    
    candidates: list[str] = []

    for block in text_blocks:
        lines = [_clean_line(line) for line in _normalize_newlines(block.content).split("\n")]
        edge_lines = (lines[:HEADER_FOOTER_SCAN_LINES] + lines[-HEADER_FOOTER_SCAN_LINES:])

    for line in edge_lines:
        if _is_page_number_line(line):
            continue
        key = _line_key(line)
        if _is_repeated_line_candidates(key):
            candidates.append(key)
    
    threshold = max(2, ceil(page_count * REPEATED_LINE_MIN_RATO))
    counts = Counter(candidates)
    return set(line for line, count in counts.items() if count >= threshold)

def _normalize_newlines(text: str) -> str:
    """统一换行符，并去掉会影响重复行判断的不可见字符。"""
    return (
        # PDF/Word 等来源可能混用 Windows、Unix、旧 Mac 换行符，先统一成 \n。
        text.replace("\r\n", "\n")
        .replace("\r", "\n") 
        # 将不间断空格当作普通空格处理，避免视觉相同的行被判断为不同文本。
        .replace("\u00a0", " ")
        # 去除零宽字符，避免它们干扰页眉页脚重复行检测。
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
    )

def _clean_line(line: str) -> str:
    """清理单行文本中的控制空白，并去除首尾空格。"""
    return re.sub(r"[\t\f\v]+", " ", line).strip()

def _is_page_number_line(line: str) -> bool:
    normalized = _line_key(line)

    patterns = [
        r"^\d+$",
        r"^-+\s*\d+\s*-+$",
        r"^第\s*\d+\s*页$",
        r"^第\s*\d+\s*/\s*\d+\s*页$",
        r"^page\s+\d+$",
        r"^page\s+\d+\s+of\s+\d+$",
        r"^\d+\s*/\s*\d+$",  # Page 1 of 10
    ]

    return any(re.fullmatch(pattern, normalized) for pattern in patterns)

def _line_key(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip().lower()

def _is_repeated_line_candidates(line_key: str) -> bool:
    if len(line_key) < 4:
        return False
    if re.fullmatch(r"[\W_]+", line_key):
        return False
    return True
