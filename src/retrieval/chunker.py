"""
src/retrieval/chunker.py
DocumentChunk 텍스트를 임베딩 입력용으로 준비하는 유틸리티

역할:
  - 긴 청크를 CHUNK_SIZE 단위로 재분할
  - 너무 짧은 청크 필터링
  - 임베딩 입력 텍스트 생성 (Title + Section + Text 결합)
  - chunk_id 결정성 보장
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import replace

from src.retrieval.config import CHUNK_OVERLAP, CHUNK_SIZE, MIN_CHUNK_CHARS
from src.retrieval.schemas import DocumentChunk

logger = logging.getLogger(__name__)


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    텍스트를 chunk_size 문자 단위로 분할한다.
    경계는 가능하면 줄바꿈에서 맞춘다.
    """
    if len(text) <= chunk_size:
        return [text]

    parts: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # 줄바꿈 경계 찾기
            newline = text.rfind("\n", start, end)
            if newline > start + chunk_size // 2:
                end = newline + 1
        part = text[start:end].strip()
        if part:
            parts.append(part)
        start = end - overlap
        if start >= len(text):
            break

    return parts


def chunk_documents(
    documents: list[DocumentChunk],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    min_chars: int = MIN_CHUNK_CHARS,
) -> tuple[list[DocumentChunk], int]:
    """
    DocumentChunk 리스트를 청킹 규칙에 따라 재분할한다.

    Returns:
        (final_chunks, excluded_count)
    """
    output: list[DocumentChunk] = []
    excluded = 0

    for doc in documents:
        parts = _split_text(doc.text, chunk_size, overlap)
        total = len(parts)
        for sub_i, part in enumerate(parts):
            if len(part) < min_chars:
                excluded += 1
                continue

            # 서브청크 ID: 원본 chunk_id + 서브인덱스
            if total == 1:
                new_id = doc.chunk_id
            else:
                new_id = f"{doc.chunk_id}__sub{sub_i:03d}"

            output.append(
                replace(doc, chunk_id=new_id, text=part)
            )

    # chunk_id 기준 정렬 — 재현성 보장
    output.sort(key=lambda c: c.chunk_id)

    logger.info(
        "chunker: %d docs → %d chunks (excluded %d short)",
        len(documents), len(output), excluded,
    )
    return output, excluded


def build_embedding_input(chunk: DocumentChunk) -> str:
    """
    BGE-M3 임베딩 입력 텍스트를 구성한다.
    Title / Section / Source / Text 형식으로 문맥을 포함한다.
    """
    parts = [
        f"Title: {chunk.title}",
        f"Section: {chunk.section}",
        f"Source Type: {chunk.source_type}",
        f"Text: {chunk.text}",
    ]
    return "\n".join(parts)


def compute_chunk_id(document_id: str, section: str, sub_index: int) -> str:
    """
    결정적 chunk_id를 SHA256 기반으로 생성한다.
    (직접 사용보다 f-string 방식 선호; 테스트용으로 노출)
    """
    raw = f"{document_id}__{section}__{sub_index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
