"""
src/retrieval/search.py
BGE-M3 기반 코사인 유사도 문서 검색

CLI:
    python -m src.retrieval.search --query "Nasdaq-100 편출 기준은 무엇인가?" --top-k 3

모듈:
    from src.retrieval.search import search_documents, load_index
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np

from src.retrieval.chunker import build_embedding_input
from src.retrieval.config import (
    EMBEDDINGS_FILE,
    MANIFEST_FILE,
    MAX_QUERY_CHARS,
    METADATA_FILE,
    PRIMARY_SOURCE_TYPES,
)
from src.retrieval.embedding_model import encode_texts, get_device
from src.retrieval.schemas import DocumentChunk, SearchResult

logger = logging.getLogger(__name__)

# ── 인덱스 메모리 캐시 ────────────────────────────────────────────────────────
_cache: dict = {}


def _index_ready() -> bool:
    return EMBEDDINGS_FILE.exists() and METADATA_FILE.exists()


def load_index(force_reload: bool = False) -> tuple[np.ndarray, list[dict]]:
    """
    저장된 임베딩 배열과 메타데이터를 로드한다.
    반복 호출 시 메모리 캐시를 사용한다.

    Raises:
        FileNotFoundError: 인덱스 파일이 없는 경우.
    """
    global _cache

    if not _index_ready():
        raise FileNotFoundError(
            "Index not found. Run: python -m src.retrieval.indexer --refresh"
        )

    if not force_reload and "embeddings" in _cache:
        return _cache["embeddings"], _cache["metadata"]

    embeddings = np.load(str(EMBEDDINGS_FILE)).astype(np.float32)
    metadata   = json.loads(METADATA_FILE.read_text(encoding="utf-8"))

    assert len(embeddings) == len(metadata), (
        f"Embedding rows ({len(embeddings)}) ≠ metadata rows ({len(metadata)})"
    )

    _cache["embeddings"] = embeddings
    _cache["metadata"]   = metadata
    logger.info("Index loaded: %d chunks, dim=%d", len(metadata), embeddings.shape[1])
    return embeddings, metadata


def search_documents(
    query: str,
    top_k: int = 3,
    source_types: Optional[list[str]] = None,
    min_score: Optional[float] = None,
) -> list[SearchResult]:
    """
    질문과 가장 관련성 높은 문서 청크를 반환한다.

    Args:
        query: 검색 질문. 비어 있으면 ValueError.
        top_k: 반환할 최대 결과 수 (1–10).
        source_types: 필터링할 source_type 목록. None이면 PRIMARY_SOURCE_TYPES.
        min_score: 이 값 미만의 유사도는 결과에서 제외.

    Returns:
        SearchResult 리스트 (유사도 내림차순, 최대 top_k 개).

    Raises:
        ValueError: 검색어가 비어 있거나 top_k가 범위 밖인 경우.
        FileNotFoundError: 인덱스가 없는 경우.
    """
    query = query.strip()
    if not query:
        raise ValueError("검색어가 비어 있습니다.")
    if not (1 <= top_k <= 10):
        raise ValueError(f"top_k는 1~10 사이여야 합니다. (받은 값: {top_k})")

    # 쿼리 길이 제한
    if len(query) > MAX_QUERY_CHARS:
        query = query[:MAX_QUERY_CHARS]
        logger.warning("Query truncated to %d chars.", MAX_QUERY_CHARS)

    # source_type 기본값
    if source_types is None:
        source_types = PRIMARY_SOURCE_TYPES

    # 인덱스 로드
    embeddings, metadata = load_index()

    # source_type 필터링
    valid_indices = [
        i for i, m in enumerate(metadata)
        if m["source_type"] in source_types
    ]
    if not valid_indices:
        logger.warning("No chunks match source_types: %s", source_types)
        return []

    filtered_embs = embeddings[valid_indices]
    filtered_meta = [metadata[i] for i in valid_indices]

    # 쿼리 임베딩 (정규화)
    query_vec = encode_texts([query], batch_size=1, normalize=True)[0]

    # 코사인 유사도 = 내적 (양쪽 L2 정규화 상태)
    scores = filtered_embs @ query_vec  # shape: (n,)

    # 정렬
    sorted_indices = np.argsort(-scores)

    results: list[SearchResult] = []
    rank = 0
    for idx in sorted_indices:
        score = float(scores[idx])
        if min_score is not None and score < min_score:
            continue
        meta = filtered_meta[idx]
        rank += 1
        results.append(
            SearchResult(
                rank=rank,
                score=score,
                chunk_id=meta["chunk_id"],
                document_id=meta["document_id"],
                title=meta["title"],
                section=meta["section"],
                source_type=meta["source_type"],
                source_url=meta.get("source_url") or "",
                published_at=meta.get("published_at"),
                page=meta.get("page"),
                item_number=meta.get("item_number"),
                text=meta["text"],
            )
        )
        if rank >= top_k:
            break

    return results


def _print_results(query: str, results: list[SearchResult]) -> None:
    """CLI 출력 포매터."""
    manifest: dict = {}
    if MANIFEST_FILE.exists():
        manifest = json.loads(MANIFEST_FILE.read_text())

    print()
    print("=" * 60)
    print("  BGE-M3 Official Document Search")
    print("=" * 60)
    print(f"  Query : {query}")
    print(f"  Model : {manifest.get('model_name', 'BAAI/bge-m3')}")
    print(f"  Device: {manifest.get('device', get_device())}")
    print(f"  Index : {manifest.get('chunk_count', '?')} chunks  "
          f"(built {(manifest.get('built_at') or '')[:10]})")
    print("=" * 60)

    if not results:
        print("\n  검색 결과 없음: 현재 저장된 공식 문서에서 관련 근거를 찾지 못했습니다.\n")
        return

    for r in results:
        print(f"\n{r.rank}. score={r.score:.4f}")
        print(f"   title  : {r.title}")
        print(f"   section: {r.section}")
        print(f"   source : {r.source_type}")
        if r.source_url:
            print(f"   url    : {r.source_url}")
        if r.published_at:
            print(f"   date   : {r.published_at}")
        preview = r.text[:300].replace("\n", " ")
        print(f"   text   : {preview}...")
    print()


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="BGE-M3 document search CLI")
    p.add_argument("--query", "-q", required=True, help="검색 질문")
    p.add_argument("--top-k", "-k", type=int, default=3, help="반환 결과 수 (1~10)")
    p.add_argument(
        "--source-types",
        nargs="*",
        default=None,
        help="필터링할 source_type 목록 (예: nasdaq_official sec_official)",
    )
    return p.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    args = _parse_args()

    try:
        results = search_documents(
            query=args.query,
            top_k=args.top_k,
            source_types=args.source_types,
        )
        _print_results(args.query, results)
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("Run: python -m src.retrieval.indexer --refresh\n")
        raise SystemExit(1)
    except ValueError as e:
        print(f"\n[ERROR] {e}\n")
        raise SystemExit(1)
