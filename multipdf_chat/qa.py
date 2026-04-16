from __future__ import annotations

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

from multipdf_chat.config import (
    DEFAULT_CHAT_MODEL,
    LOCAL_RETRIEVAL_LIMIT,
    MAX_LOCAL_ANSWER_CHARS,
)
from multipdf_chat.knowledge_base import (
    explain_runtime_error,
    get_knowledge_signature,
    has_vector_index,
    load_manifest,
    load_vector_store,
)
from multipdf_chat.text_utils import (
    extract_requested_page_numbers,
    finalize_answer,
    response_content_to_text,
    select_best_sentences,
    tokenize,
)


@st.cache_resource(show_spinner=False)
def get_conversational_model():
    return ChatGoogleGenerativeAI(
        model=DEFAULT_CHAT_MODEL,
        temperature=0.3,
    )


def format_docs_for_prompt(docs) -> str:
    return "\n\n".join(
        (
            f"Source: {doc.metadata.get('source', 'Uploaded PDF')} | "
            f"Page: {doc.metadata.get('page_number', '?')}\n"
            f"{doc.page_content}"
        )
        for doc in docs
    )


def answer_with_gemini(question: str, docs) -> str:
    prompt = f"""
    Answer the question as detailed as possible from the provided context. If the answer is not in the
    provided context, say "answer is not available in the context" and do not make up information.

    Context:
    {format_docs_for_prompt(docs)}

    Question:
    {question}

    Answer:
    """
    response = get_conversational_model().invoke(prompt)
    return finalize_answer(response_content_to_text(response.content))


def retrieve_local_matches(question: str, signature, limit: int = LOCAL_RETRIEVAL_LIMIT) -> list[dict]:
    manifest = load_manifest(signature)
    chunks = manifest.get("chunks") or manifest.get("pages", [])
    if not chunks:
        return []

    question_lower = question.lower()
    question_tokens = tokenize(question)
    requested_pages = extract_requested_page_numbers(question)
    ranked = []

    for index, chunk in enumerate(chunks):
        chunk_tokens = tokenize(chunk["text"])
        score = len(question_tokens & chunk_tokens) * 5

        if question_lower and question_lower in chunk["text"].lower():
            score += 10

        if requested_pages and chunk["page_number"] in requested_pages:
            score += 25

        ranked.append((score, index, chunk))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    matches = [chunk for score, _, chunk in ranked if score > 0][:limit]

    if not matches and requested_pages:
        matches = [chunk for chunk in chunks if chunk["page_number"] in requested_pages][:limit]

    if not matches:
        matches = [chunk for _, _, chunk in ranked[:limit]]

    return matches


def docs_to_chunk_records(docs) -> list[dict]:
    return [
        {
            "text": doc.page_content,
            "source": doc.metadata.get("source", "Uploaded PDF"),
            "page_number": doc.metadata.get("page_number", "?"),
        }
        for doc in docs
    ]


def build_local_fallback_answer(question: str, matches: list[dict], reason: str | None = None) -> str:
    if not matches:
        return "answer is not available in the context"

    wants_summary = any(word in question.lower() for word in ("summary", "summarize", "overview", "gist"))
    selected_sentences = []
    seen_sentences = set()

    for index, chunk in enumerate(matches):
        limit = 2 if wants_summary or index == 0 else 1
        for sentence in select_best_sentences(question, chunk["text"], limit=limit):
            if sentence not in seen_sentences:
                selected_sentences.append(sentence)
                seen_sentences.add(sentence)

    answer_text = " ".join(selected_sentences).strip() or matches[0]["text"].strip()
    if len(answer_text) > MAX_LOCAL_ANSWER_CHARS:
        answer_text = answer_text[: MAX_LOCAL_ANSWER_CHARS - 3].rstrip() + "..."

    sources = "\n".join(
        f"- {match['source']} (page {match['page_number']})" for match in matches[:3]
    )

    if reason:
        note = f"\n\n_Local fallback used because {reason}._"
    else:
        note = "\n\n_Local keyword retrieval mode._"

    return f"{answer_text}\n\n**Sources**\n{sources}{note}"


@st.cache_data(show_spinner=False, ttl=600)
def get_answer_for_question(signature, question: str) -> str:
    local_matches = retrieve_local_matches(question, signature)

    if has_vector_index():
        try:
            vector_store = load_vector_store(signature)
            docs = vector_store.similarity_search(question)
            if docs:
                try:
                    return answer_with_gemini(question, docs)
                except Exception as exc:
                    reason = explain_runtime_error(exc, "answer generation").lower()
                    return build_local_fallback_answer(question, docs_to_chunk_records(docs), reason)
        except Exception as exc:
            reason = explain_runtime_error(exc, "vector search").lower()
            return build_local_fallback_answer(question, local_matches, reason)

    return build_local_fallback_answer(question, local_matches)


def ask_question(question: str) -> str:
    signature = get_knowledge_signature()
    if signature is None:
        raise FileNotFoundError("Knowledge base not found. Build it from the sidebar first.")
    return get_answer_for_question(signature, question)
