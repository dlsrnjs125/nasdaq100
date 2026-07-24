"""
src/retrieval/document_loader.py
공식 문서를 DocumentChunk 리스트로 변환하는 로더

두 개의 어댑터:
  1. _load_from_txt_files()  — data/documents/*.txt
  2. _load_from_raw_json()   — data/raw/*.json (구조화 메타데이터를 텍스트화)

원칙:
  - 실제로 존재하는 데이터만 사용
  - 임의 텍스트·URL·날짜 생성 금지
  - source_url, published_at 등 원본 메타데이터에 없는 값은 None/""
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Optional

from src.retrieval.config import DOCUMENTS_DIR, RAW_DATA_DIR
from src.retrieval.schemas import DocumentChunk

logger = logging.getLogger(__name__)

# TXT 파일 헤더에서 메타데이터를 파싱하는 패턴
_META_PATTERN = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)
_SECTION_PATTERN = re.compile(r"^={3,}\s*SECTION:\s*(.+?)\s*={3,}", re.MULTILINE)


def _parse_txt_metadata(text: str) -> dict:
    """
    TXT 문서 상단 헤더에서 메타데이터를 파싱한다.
    첫 빈 줄(또는 === SECTION) 이전까지를 헤더로 간주.
    """
    meta: dict = {}
    # 첫 번째 === SECTION 이전까지를 헤더로 간주
    header_end = re.search(r"^={3,}", text, re.MULTILINE)
    header = text[: header_end.start()] if header_end else text[:500]
    for m in _META_PATTERN.finditer(header):
        key = m.group(1).strip().lower()
        val = m.group(2).strip()
        meta[key] = val
    return meta


def _load_from_txt_files() -> list[DocumentChunk]:
    """
    data/documents/*.txt 파일을 읽어 섹션 단위 DocumentChunk 리스트를 반환한다.
    """
    chunks: list[DocumentChunk] = []
    txt_files = sorted(DOCUMENTS_DIR.glob("*.txt")) if DOCUMENTS_DIR.exists() else []
    logger.info("TXT files found: %d", len(txt_files))

    for path in txt_files:
        raw = path.read_text(encoding="utf-8")
        meta = _parse_txt_metadata(raw)

        doc_id     = meta.get("document_id") or path.stem
        title      = meta.get("title") or path.stem
        source_type = meta.get("source_type") or "secondary"
        source_url  = meta.get("source_url") or ""
        published_at = meta.get("published_at") or None

        # === SECTION 경계로 분리
        sections = _SECTION_PATTERN.split(raw)
        # split 결과: [before_first_section, section_name, section_body, ...]
        if len(sections) <= 1:
            # 섹션 구분자 없으면 전체를 하나의 청크로
            section_pairs = [("Main", raw)]
        else:
            # sections[0]: 헤더부분(무시), sections[1::2]: 이름, sections[2::2]: 본문
            names  = sections[1::2]
            bodies = sections[2::2]
            section_pairs = list(zip(names, bodies))

        for chunk_n, (sec_name, sec_body) in enumerate(section_pairs):
            body = sec_body.strip()
            if len(body) < 30:
                continue
            chunk_id = f"{doc_id}__chunk{chunk_n:04d}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    title=title,
                    section=sec_name.strip(),
                    source_type=source_type,
                    source_url=source_url,
                    published_at=published_at,
                    page=None,
                    item_number=None,
                    text=body,
                )
            )

    logger.info("Chunks from TXT files: %d", len(chunks))
    return chunks


def _load_from_raw_json() -> list[DocumentChunk]:
    """
    data/raw/*.json 에서 구조화 데이터를 읽어 검색 가능한 텍스트 청크로 변환한다.
    기존 PoC 수집기가 저장한 실제 데이터만 사용한다.
    """
    chunks: list[DocumentChunk] = []

    # ── nasdaq100_constituents.json ──────────────────────────────────────────
    constituents_path = RAW_DATA_DIR / "nasdaq100_constituents.json"
    if constituents_path.exists():
        data = json.loads(constituents_path.read_text(encoding="utf-8"))
        collected_at = data.get("collected_at", "")
        source_url   = data.get("source_url", "")
        items        = data.get("data", [])
        logger.info("Constituents: %d items", len(items))

        # 전체 목록을 하나의 청크로
        lines = [
            f"Nasdaq-100 Index Constituents List (as of {collected_at[:10] if collected_at else 'N/A'})",
            f"Total constituent count: {len(items)}",
            f"Source: {source_url}",
            "",
            "Ticker | Company Name | Sector",
            "---",
        ]
        for item in items:
            ticker = item.get("ticker") or ""
            name   = item.get("company_name") or ""
            sector = item.get("sector") or "N/A"
            lines.append(f"{ticker} | {name} | {sector}")

        text = "\n".join(lines)
        chunks.append(
            DocumentChunk(
                chunk_id="nasdaq100_constituents__chunk0000",
                document_id="nasdaq100_constituents",
                title="Nasdaq-100 Index Constituents",
                section="Full Constituent List",
                source_type="nasdaq_official",
                source_url=source_url,
                published_at=collected_at[:10] if collected_at else None,
                page=None,
                item_number=None,
                text=text,
            )
        )

    # ── sec_company_data.json ─────────────────────────────────────────────────
    sec_path = RAW_DATA_DIR / "sec_company_data.json"
    if sec_path.exists():
        data = json.loads(sec_path.read_text(encoding="utf-8"))
        collected_at = data.get("collected_at", "")
        items        = data.get("data", [])
        logger.info("SEC company data: %d items", len(items))

        # 기업별 청크 (25개씩 묶음 — 너무 세분화하지 않음)
        BATCH = 25
        for i in range(0, len(items), BATCH):
            batch = items[i : i + BATCH]
            lines = [
                f"SEC EDGAR Filing Metadata — Companies {i+1}–{i+len(batch)}",
                f"Collected: {collected_at[:10] if collected_at else 'N/A'}",
                "",
                "Ticker | CIK | Company Name | Latest Filing | Filed Date | Shares Outstanding",
                "---",
            ]
            for item in batch:
                ticker  = item.get("ticker") or ""
                cik     = item.get("cik") or ""
                name    = item.get("entity_name") or ""
                ftype   = item.get("latest_filing_type") or "N/A"
                fdate   = item.get("latest_filing_date") or "N/A"
                shares  = item.get("shares_outstanding")
                shares_str = f"{int(shares):,}" if shares else "N/A"
                lines.append(f"{ticker} | {cik} | {name} | {ftype} | {fdate} | {shares_str}")

            chunk_n = i // BATCH
            src_url = items[i].get("source_url", "") if batch else ""
            chunks.append(
                DocumentChunk(
                    chunk_id=f"sec_company_data__chunk{chunk_n:04d}",
                    document_id="sec_company_data",
                    title="SEC EDGAR Company Filing Data",
                    section=f"Companies {i+1}–{i+len(batch)}",
                    source_type="sec_official",
                    source_url=src_url,
                    published_at=collected_at[:10] if collected_at else None,
                    page=None,
                    item_number=None,
                    text="\n".join(lines),
                )
            )

    logger.info("Chunks from raw JSON: %d", len(chunks))
    return chunks


def load_all_documents(
    include_source_types: Optional[list[str]] = None,
) -> list[DocumentChunk]:
    """
    모든 소스에서 DocumentChunk를 로드하고 정렬된 리스트를 반환한다.

    Args:
        include_source_types: 포함할 source_type 목록. None이면 전체.

    Returns:
        chunk_id 기준 정렬된 DocumentChunk 리스트.
    """
    chunks: list[DocumentChunk] = []
    chunks.extend(_load_from_txt_files())
    chunks.extend(_load_from_raw_json())

    if include_source_types is not None:
        chunks = [c for c in chunks if c.source_type in include_source_types]

    # chunk_id 기준 정렬 → 재현성 보장
    chunks.sort(key=lambda c: c.chunk_id)

    # 중복 chunk_id 경고
    seen: set[str] = set()
    for c in chunks:
        if c.chunk_id in seen:
            logger.warning("Duplicate chunk_id detected: %s", c.chunk_id)
        seen.add(c.chunk_id)

    logger.info("Total chunks loaded: %d", len(chunks))
    return chunks


def compute_snapshot_hash(chunks: list[DocumentChunk]) -> str:
    """
    청크 목록의 결정적 해시를 계산한다.
    동일 입력 → 동일 해시 (재현성 검증용).
    """
    h = hashlib.sha256()
    for c in sorted(chunks, key=lambda x: x.chunk_id):
        h.update(c.chunk_id.encode())
        h.update(c.text.encode())
    return h.hexdigest()
