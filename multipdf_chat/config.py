from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parent
BASE_DIR = PACKAGE_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGE_DIR = ASSETS_DIR / "images"
INDEX_DIR = BASE_DIR / "faiss_index"
MANIFEST_PATH = INDEX_DIR / "manifest.json"
ROBOT_IMAGE_PATH = IMAGE_DIR / "Robot.jpg"

load_dotenv(BASE_DIR / ".env")

DEFAULT_CHAT_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
DEFAULT_EMBEDDING_MODEL = os.getenv(
    "GOOGLE_EMBEDDING_MODEL",
    "models/gemini-embedding-001",
)
INDEX_FILES = ("index.faiss", "index.pkl")
LOCAL_RETRIEVAL_LIMIT = 4
MAX_LOCAL_ANSWER_CHARS = 1800

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}
