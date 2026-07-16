from __future__ import annotations

import os
from pathlib import Path

from agents import function_tool

# Maximum file size allowed for reading (bytes) — default 1 MB
_MAX_READ_BYTES = int(os.getenv("FILE_TOOL_MAX_BYTES", 1_048_576))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_path(path: str) -> Path:
    """Resolve and return a Path object (no traversal guard — agent-internal)."""
    return Path(path).expanduser().resolve()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@function_tool
def scan_directory(path: str, recursive: bool = False) -> str:
    """
    List files and subdirectories inside a directory.

    Args:
        path:      Absolute or relative path to the directory to scan.
        recursive: If True, scan all subdirectories as well.
                   If False (default), only the top-level contents are listed.

    Returns:
        A formatted text listing of entries with their type (file/dir) and
        size in bytes (for files). Returns an error message if the path does
        not exist or is not a directory.
    """
    target = _safe_path(path)

    if not target.exists():
        return f"❌ ไม่พบ path: {target}"
    if not target.is_dir():
        return f"❌ '{target}' ไม่ใช่ directory"

    entries = list(target.rglob("*")) if recursive else list(target.iterdir())
    entries.sort(key=lambda p: (p.is_file(), p.name.lower()))

    if not entries:
        return f"📁 '{target}' ว่างเปล่า ไม่มีไฟล์หรือ directory"

    lines: list[str] = [f"📁 {target}"]
    for entry in entries:
        rel = entry.relative_to(target)
        if entry.is_dir():
            lines.append(f"  📂 {rel}/")
        else:
            try:
                size = entry.stat().st_size
                size_str = f"{size:,} bytes"
            except OSError:
                size_str = "unknown size"
            lines.append(f"  📄 {rel}  ({size_str})")

    lines.append(f"\nรวม {len(entries)} รายการ")
    return "\n".join(lines)


@function_tool
def read_file(path: str) -> str:
    """
    Read and return the text content of a file.

    Args:
        path: Absolute or relative path to the file to read.

    Returns:
        The text content of the file, or an error message if the file cannot
        be read (not found, too large, or binary/undecodable content).
    """
    target = _safe_path(path)

    if not target.exists():
        return f"❌ ไม่พบไฟล์: {target}"
    if not target.is_file():
        return f"❌ '{target}' ไม่ใช่ไฟล์"

    size = target.stat().st_size
    if size > _MAX_READ_BYTES:
        return (
            f"❌ ไฟล์ '{target.name}' ใหญ่เกินไป ({size:,} bytes). "
            f"จำกัดไว้ที่ {_MAX_READ_BYTES:,} bytes"
        )

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = target.read_text(encoding="cp874")  # Thai fallback
        except UnicodeDecodeError:
            return f"❌ ไม่สามารถอ่านไฟล์ '{target.name}' ได้ (binary หรือ encoding ไม่รองรับ)"

    return f"📄 {target}\n{'─' * 40}\n{content}"


@function_tool
def write_file(path: str, content: str, overwrite: bool = False) -> str:
    """
    Write text content to a file, creating it (and any parent directories)
    if it does not exist.

    Args:
        path:      Absolute or relative path of the file to write.
        content:   The text content to write.
        overwrite: If True, overwrite an existing file.
                   If False (default), refuse to overwrite to prevent
                   accidental data loss.

    Returns:
        A success message, or an error message if the write fails.
    """
    target = _safe_path(path)

    if target.exists() and not overwrite:
        return (
            f"❌ ไฟล์ '{target}' มีอยู่แล้ว หากต้องการเขียนทับ ให้ตั้ง overwrite=True"
        )

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except OSError as exc:
        return f"❌ เขียนไฟล์ไม่สำเร็จ: {exc}"

    action = "เขียนทับ" if target.exists() else "สร้าง"
    return f"✅ {action}ไฟล์เรียบร้อย: {target}  ({len(content.encode()):,} bytes)"
