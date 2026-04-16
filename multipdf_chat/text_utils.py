from __future__ import annotations

import re

from multipdf_chat.config import STOPWORDS


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def response_content_to_text(content) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part)

    return str(content)


def finalize_answer(answer: str) -> str:
    cleaned = answer.strip()
    if not cleaned:
        return "answer is not available in the context"
    if cleaned.lower() == "answer is not available in the context":
        return cleaned
    return cleaned


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(token) > 1 and token not in STOPWORDS
    }


def extract_requested_page_numbers(question: str) -> set[int]:
    return {int(match) for match in re.findall(r"\bpage\s+(\d+)\b", question.lower())}


def sentence_split(text: str) -> list[str]:
    sentences = [normalize_text(part) for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    return sentences or [normalize_text(text)]


def select_best_sentences(question: str, text: str, limit: int) -> list[str]:
    question_tokens = tokenize(question)
    sentences = sentence_split(text)
    ranked_sentences = []

    for index, sentence in enumerate(sentences):
        sentence_tokens = tokenize(sentence)
        score = len(question_tokens & sentence_tokens) * 10
        if question_tokens and question.lower() in sentence.lower():
            score += 8
        if index == 0:
            score += 1
        ranked_sentences.append((score, index, sentence))

    best = sorted(ranked_sentences, key=lambda item: (-item[0], item[1]))[:limit]
    best_indexes = {index for _, index, _ in best}
    return [sentence for index, sentence in enumerate(sentences) if index in best_indexes]
