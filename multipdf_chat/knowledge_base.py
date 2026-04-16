from __future__ import annotations

import json
import os
import socket

import streamlit as st
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from multipdf_chat.config import (
    DEFAULT_EMBEDDING_MODEL,
    INDEX_DIR,
    INDEX_FILES,
    MANIFEST_PATH,
)
from multipdf_chat.text_utils import normalize_text


def get_google_api_key() -> str:
    return os.getenv("GOOGLE_API_KEY", "").strip()


def is_google_api_key_configured() -> bool:
    return bool(get_google_api_key())


def has_vector_index() -> bool:
    return all((INDEX_DIR / filename).exists() for filename in INDEX_FILES)


def resolve_embedding_model() -> str:
    configured_model = DEFAULT_EMBEDDING_MODEL.strip()
    legacy_aliases = {
        "embedding-001": "models/gemini-embedding-001",
        "models/embedding-001": "models/gemini-embedding-001",
        "gemini-embedding-001": "models/gemini-embedding-001",
    }
    return legacy_aliases.get(configured_model, configured_model)


def extract_pdf_pages(pdf_docs):
    pages = []
    for pdf in pdf_docs:
        source_name = getattr(pdf, "name", "Uploaded PDF")
        reader = PdfReader(pdf)
        for page_number, page in enumerate(reader.pages, start=1):
            text = normalize_text(page.extract_text() or "")
            if text:
                pages.append(
                    {
                        "source": source_name,
                        "page_number": page_number,
                        "text": text,
                    }
                )
    return pages


def get_chunk_records(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=50000,
        chunk_overlap=1000,
    )

    chunks = []
    for page in pages:
        for chunk in splitter.split_text(page["text"]):
            chunk = chunk.strip()
            if not chunk:
                continue
            chunks.append(
                {
                    "text": chunk,
                    "source": page["source"],
                    "page_number": page["page_number"],
                }
            )
    return chunks


def get_text_chunks(pages):
    chunks = get_chunk_records(pages)
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "source": chunk["source"],
            "page_number": chunk["page_number"],
        }
        for chunk in chunks
    ]
    return texts, metadatas, chunks


@st.cache_resource(show_spinner=False)
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model=resolve_embedding_model())


def clear_vector_index():
    INDEX_DIR.mkdir(exist_ok=True)
    for filename in INDEX_FILES:
        path = INDEX_DIR / filename
        if path.exists():
            path.unlink()


def save_manifest(pages, chunks, retrieval_mode, build_warning=None):
    INDEX_DIR.mkdir(exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as manifest_file:
        json.dump(
            {
                "pages": pages,
                "chunks": chunks,
                "chunk_count": len(chunks),
                "retrieval_mode": retrieval_mode,
                "build_warning": build_warning,
            },
            manifest_file,
            ensure_ascii=False,
            indent=2,
        )


def explain_runtime_error(exc: Exception, phase: str) -> str:
    message = normalize_text(str(exc) or exc.__class__.__name__)
    lowered = message.lower()

    if (
        isinstance(exc, socket.gaierror)
        or "getaddrinfo failed" in lowered
        or "name resolution" in lowered
        or "nodename nor servname provided" in lowered
    ):
        return (
            f"network or DNS lookup failed while contacting Gemini during {phase}. "
            "Check your internet connection, VPN, proxy, firewall, or DNS settings."
        )

    if "api key" in lowered or "permission denied" in lowered or "403" in lowered:
        return (
            f"Gemini rejected the request during {phase}. Verify that GOOGLE_API_KEY is "
            "present and valid, then try again."
        )

    if "429" in lowered or "quota" in lowered or "rate limit" in lowered:
        return (
            f"Gemini rate limited the request during {phase}. Wait a bit and try again."
        )

    if "timeout" in lowered or "timed out" in lowered or "deadline exceeded" in lowered:
        return f"Gemini timed out during {phase}. Try again when the network is stable."

    return f"Gemini was unavailable during {phase}: {message}"


def build_knowledge_base(pages):
    texts, metadatas, chunks = get_text_chunks(pages)
    if not texts:
        raise ValueError("No extractable text was found in the uploaded PDFs.")

    retrieval_mode = "keyword"
    build_warning = None

    if is_google_api_key_configured():
        try:
            embeddings = get_embeddings()
            vector_store = FAISS.from_texts(texts, embedding=embeddings, metadatas=metadatas)
            INDEX_DIR.mkdir(exist_ok=True)
            vector_store.save_local(str(INDEX_DIR))
            retrieval_mode = "semantic"
        except Exception as exc:
            clear_vector_index()
            build_warning = explain_runtime_error(exc, "knowledge-base creation")
    else:
        clear_vector_index()
        build_warning = (
            "GOOGLE_API_KEY is not configured. The app created a local keyword index "
            "instead of Gemini-powered semantic search."
        )

    save_manifest(pages, chunks, retrieval_mode, build_warning)
    return {
        "page_count": len(pages),
        "chunk_count": len(chunks),
        "retrieval_mode": retrieval_mode,
        "build_warning": build_warning,
    }


def get_knowledge_signature():
    if not MANIFEST_PATH.exists():
        return None

    signature = [MANIFEST_PATH.stat().st_mtime]
    for filename in INDEX_FILES:
        path = INDEX_DIR / filename
        signature.append(path.stat().st_mtime if path.exists() else 0)
    return tuple(signature)


@st.cache_resource(show_spinner=False)
def load_vector_store(signature):
    embeddings = get_embeddings()
    return FAISS.load_local(
        str(INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


@st.cache_data(show_spinner=False)
def load_manifest(signature):
    if not MANIFEST_PATH.exists():
        return {"pages": []}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)
    manifest.setdefault("chunks", [])
    manifest.setdefault("retrieval_mode", "keyword")
    manifest.setdefault("build_warning", None)
    return manifest
