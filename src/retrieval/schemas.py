"""
src/retrieval/schemas.py
검색 파이프라인 공유 데이터 타입
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DocumentChunk:
    """인덱스에 저장되는 문서 청크 단위."""
    chunk_id: str          # 결정적 고유 ID: f"{document_id}__chunk{n:04d}"
    document_id: str       # 원본 문서 식별자
    title: str             # 문서 제목
    section: str           # 섹션 또는 항목명
    source_type: str       # nasdaq_official | sec_official | company_ir | secondary
    source_url: str        # 원본 URL (없으면 빈 문자열)
    published_at: Optional[str]   # ISO 8601 날짜 또는 None
    page: Optional[int]           # PDF 페이지 번호 또는 None
    item_number: Optional[str]    # SEC 8-K Item 번호 등 또는 None
    text: str              # 임베딩에 사용되는 실제 텍스트


@dataclass
class SearchResult:
    """검색 반환 결과 단위."""
    rank: int
    score: float
    chunk_id: str
    document_id: str
    title: str
    section: str
    source_type: str
    source_url: str
    published_at: Optional[str]
    page: Optional[int]
    item_number: Optional[str]
    text: str

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "score": round(self.score, 6),
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "title": self.title,
            "section": self.section,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "published_at": self.published_at,
            "page": self.page,
            "item_number": self.item_number,
            "text": self.text,
        }
