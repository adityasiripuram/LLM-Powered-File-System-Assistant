"""
fs_tools.py

Core file system tools for reading, writing, listing,
and searching resume files.
"""

import os
import io
import json
from datetime import datetime
from typing import Dict, List, Optional

import PyPDF2
import docx


# -------------------------------
# Helper Functions
# -------------------------------

def _get_file_metadata(filepath: str) -> Dict:
    """Return metadata for a file."""
    stat = os.stat(filepath)
    return {
        "name": os.path.basename(filepath),
        "size_bytes": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "path": os.path.abspath(filepath)
    }


def _extract_text_from_pdf(filepath: str) -> str:
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join([page.extract_text() or "" for page in reader.pages])


def _extract_text_from_docx(filepath: str) -> str:
    doc = docx.Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])


# -------------------------------
# Tool 1: Read File
# -------------------------------

def read_file(filepath: str) -> Dict:
    """
    Read resume file (PDF, TXT, DOCX).
    Return structured response with content and metadata.
    """
    try:
        if not os.path.exists(filepath):
            return {"success": False, "error": "File not found"}

        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".pdf":
            content = _extract_text_from_pdf(filepath)
        elif ext == ".docx":
            content = _extract_text_from_docx(filepath)
        elif ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            return {"success": False, "error": f"Unsupported file type: {ext}"}

        return {
            "success": True,
            "metadata": _get_file_metadata(filepath),
            "content": content
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# -------------------------------
# Tool 2: List Files
# -------------------------------

def list_files(directory: str, extension: Optional[str] = None) -> List[Dict]:
    """
    List files in directory.
    Optionally filter by extension (.pdf, .txt, etc.)
    """
    results = []

    if not os.path.isdir(directory):
        return []

    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)

        if os.path.isfile(filepath):
            if extension:
                if not file.lower().endswith(extension.lower()):
                    continue

            results.append(_get_file_metadata(filepath))

    return results


# -------------------------------
# Tool 3: Write File
# -------------------------------

def write_file(filepath: str, content: str) -> Dict:
    """
    Write content to file.
    Create directories if needed.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "metadata": _get_file_metadata(filepath)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# -------------------------------
# Tool 4: Search In File
# -------------------------------

def search_in_file(filepath: str, keyword: str) -> Dict:
    """
    Case-insensitive search for keyword in file.
    Return matches with surrounding context.
    """
    try:
        file_data = read_file(filepath)
        if not file_data["success"]:
            return file_data

        content = file_data["content"]
        keyword_lower = keyword.lower()
        content_lower = content.lower()

        matches = []
        index = 0

        while True:
            index = content_lower.find(keyword_lower, index)
            if index == -1:
                break

            start = max(0, index - 40)
            end = min(len(content), index + len(keyword) + 40)

            matches.append(content[start:end])
            index += len(keyword)

        return {
            "success": True,
            "keyword": keyword,
            "match_count": len(matches),
            "matches": matches
        }

    except Exception as e:
        return {"success": False, "error": str(e)}