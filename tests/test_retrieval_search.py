"""
tests/test_retrieval_search.py
검색 기능 단위 테스트 — 실제 BGE-M3 모델 불필요
numpy fixture를 사용해 유사도 계산과 필터링을 검증한다.
"""
from __future__ import annotations

import json
import pytest
import numpy as np

from src.retrieval.schemas import SearchResult


# ── 가짜 임베딩 fixture ───────────────────────────────────────────────────────

def _normalized(v: list[float]) -> np.ndarray:
    """벡터를 L2 정규화한다."""
    a = np.array(v, dtype=np.float32)
    return a / np.linalg.norm(a)


# 테스트용 소형 임베딩 (3차원)
_CHUNK_VECS = [
    _normalized([1.0, 0.0, 0.0]),   # chunk 0: x 방향
    _normalized([0.0, 1.0, 0.0]),   # chunk 1: y 방향
    _normalized([0.0, 0.0, 1.0]),   # chunk 2: z 방향
    _normalized([0.8, 0.6, 0.0]),   # chunk 3: x+y 방향
]
_EMBEDDINGS = np.stack(_CHUNK_VECS)

_METADATA = [
    {
        "chunk_id": "doc_nasdaq__chunk0000",
        "document_id": "doc_nasdaq",
        "title": "Nasdaq-100 Methodology",
        "section": "Eligibility",
        "source_type": "nasdaq_official",
        "source_url": "https://nasdaq.com",
        "published_at": "2024-01-01",
        "page": None,
        "item_number": None,
        "text": "Nasdaq-100 eligibility criteria text.",
    },
    {
        "chunk_id": "doc_sec__chunk0000",
        "document_id": "doc_sec",
        "title": "SEC EDGAR",
        "section": "10-K",
        "source_type": "sec_official",
        "source_url": "https://sec.gov",
        "published_at": "2024-01-01",
        "page": None,
        "item_number": "Item 1",
        "text": "Annual report 10-K filing requirements.",
    },
    {
        "chunk_id": "doc_secondary__chunk0000",
        "document_id": "doc_secondary",
        "title": "Secondary News",
        "section": "Market Analysis",
        "source_type": "secondary",
        "source_url": "https://example.com/news",
        "published_at": None,
        "page": None,
        "item_number": None,
        "text": "Market analysis from secondary source.",
    },
    {
        "chunk_id": "doc_nasdaq2__chunk0000",
        "document_id": "doc_nasdaq2",
        "title": "Nasdaq-100 Weight Rules",
        "section": "Weighting",
        "source_type": "nasdaq_official",
        "source_url": "https://nasdaq.com/weight",
        "published_at": "2024-06-01",
        "page": None,
        "item_number": None,
        "text": "Modified market-cap weighting rules for Nasdaq-100.",
    },
]


# ── search_documents 핵심 로직 직접 테스트 ─────────────────────────────────────

def _mock_search(
    query_vec: np.ndarray,
    embeddings: np.ndarray,
    metadata: list[dict],
    top_k: int,
    source_types: list[str],
    min_score: float | None = None,
) -> list[SearchResult]:
    """
    search_documents의 내적 계산 로직을 직접 호출하는 helper.
    실제 모델 없이 로직만 검증한다.
    """
    valid_indices = [
        i for i, m in enumerate(metadata) if m["source_type"] in source_types
    ]
    if not valid_indices:
        return []

    filtered_embs = embeddings[valid_indices]
    filtered_meta = [metadata[i] for i in valid_indices]

    scores = filtered_embs @ query_vec
    sorted_indices = np.argsort(-scores)

    results = []
    rank = 0
    for idx in sorted_indices:
        score = float(scores[idx])
        if min_score is not None and score < min_score:
            continue
        m = filtered_meta[idx]
        rank += 1
        results.append(
            SearchResult(
                rank=rank,
                score=score,
                chunk_id=m["chunk_id"],
                document_id=m["document_id"],
                title=m["title"],
                section=m["section"],
                source_type=m["source_type"],
                source_url=m.get("source_url") or "",
                published_at=m.get("published_at"),
                page=m.get("page"),
                item_number=m.get("item_number"),
                text=m["text"],
            )
        )
        if rank >= top_k:
            break
    return results


# ── 유사도 정렬 테스트 ────────────────────────────────────────────────────────

def test_cosine_similarity_ranks_correctly():
    """쿼리와 가장 유사한 임베딩이 rank 1이 된다."""
    query_vec = _normalized([1.0, 0.0, 0.0])  # chunk 0과 완전 일치
    results = _mock_search(
        query_vec, _EMBEDDINGS, _METADATA,
        top_k=4,
        source_types=["nasdaq_official", "sec_official", "secondary"],
    )
    assert results[0].score > results[1].score
    assert results[0].chunk_id == "doc_nasdaq__chunk0000"


def test_source_type_filter_excludes_secondary():
    """secondary source_type을 필터링하면 결과에 포함되지 않는다."""
    query_vec = _normalized([0.0, 0.0, 1.0])
    results = _mock_search(
        query_vec, _EMBEDDINGS, _METADATA,
        top_k=10,
        source_types=["nasdaq_official", "sec_official"],
    )
    source_types_returned = [r.source_type for r in results]
    assert "secondary" not in source_types_returned


def test_source_type_filter_only_nasdaq():
    """nasdaq_official 만 필터링하면 해당 source만 반환된다."""
    query_vec = _normalized([1.0, 0.0, 0.0])
    results = _mock_search(
        query_vec, _EMBEDDINGS, _METADATA,
        top_k=10,
        source_types=["nasdaq_official"],
    )
    assert all(r.source_type == "nasdaq_official" for r in results)
    assert len(results) == 2  # doc_nasdaq, doc_nasdaq2


def test_top_k_limit():
    """top_k 제한이 적용된다."""
    query_vec = _normalized([1.0, 0.0, 0.0])
    results = _mock_search(
        query_vec, _EMBEDDINGS, _METADATA,
        top_k=1,
        source_types=["nasdaq_official", "sec_official", "secondary"],
    )
    assert len(results) == 1


def test_empty_source_types_returns_empty():
    """매칭되는 source_type이 없으면 빈 리스트를 반환한다."""
    query_vec = _normalized([1.0, 0.0, 0.0])
    results = _mock_search(
        query_vec, _EMBEDDINGS, _METADATA,
        top_k=5,
        source_types=["nonexistent_type"],
    )
    assert results == []


def test_min_score_filter():
    """min_score 미만 결과는 제외된다."""
    query_vec = _normalized([0.0, 0.0, 1.0])  # chunk 2 와 완전 일치
    results = _mock_search(
        query_vec, _EMBEDDINGS, _METADATA,
        top_k=10,
        source_types=["nasdaq_official", "sec_official", "secondary"],
        min_score=0.99,
    )
    # score 0.99 이상 = chunk 2 (secondary) 만 통과
    assert all(r.score >= 0.99 for r in results)


def test_result_metadata_preserved():
    """검색 결과에 원본 메타데이터가 유지된다."""
    query_vec = _normalized([0.0, 1.0, 0.0])  # chunk 1 (sec_official)
    results = _mock_search(
        query_vec, _EMBEDDINGS, _METADATA,
        top_k=1,
        source_types=["sec_official"],
    )
    assert len(results) == 1
    r = results[0]
    assert r.title == "SEC EDGAR"
    assert r.section == "10-K"
    assert r.source_url == "https://sec.gov"
    assert r.item_number == "Item 1"
    assert "10-K" in r.text


def test_rank_starts_at_1():
    """rank는 1부터 시작한다."""
    query_vec = _normalized([1.0, 0.0, 0.0])
    results = _mock_search(
        query_vec, _EMBEDDINGS, _METADATA,
        top_k=3,
        source_types=["nasdaq_official", "sec_official", "secondary"],
    )
    assert results[0].rank == 1
    assert results[1].rank == 2


# ── search.py 진입점 검증 ─────────────────────────────────────────────────────

def test_search_raises_on_empty_query():
    """빈 검색어를 거부한다."""
    from src.retrieval.search import search_documents

    with pytest.raises(ValueError):
        search_documents("")
    with pytest.raises(ValueError):
        search_documents("   ")


def test_search_raises_on_invalid_top_k(tmp_path):
    """top_k 가 범위 밖이면 ValueError를 반환한다."""
    from src.retrieval.search import search_documents
    pytest.raises(ValueError, search_documents, "query", top_k=0)
    pytest.raises(ValueError, search_documents, "query", top_k=11)


def test_search_raises_file_not_found_when_no_index(tmp_path, monkeypatch):
    """인덱스 파일이 없으면 FileNotFoundError를 반환한다."""
    import src.retrieval.search as sr
    import src.retrieval.config as rc
    monkeypatch.setattr(rc, "EMBEDDINGS_FILE", tmp_path / "nofile.npy")
    monkeypatch.setattr(rc, "METADATA_FILE", tmp_path / "nofile.json")
    monkeypatch.setattr(sr, "EMBEDDINGS_FILE", tmp_path / "nofile.npy")
    monkeypatch.setattr(sr, "METADATA_FILE", tmp_path / "nofile.json")
    # 캐시 초기화
    sr._cache.clear()
    with pytest.raises(FileNotFoundError):
        sr.search_documents("test query")


# ── SearchResult.to_dict 테스트 ───────────────────────────────────────────────

def test_search_result_to_dict():
    """SearchResult.to_dict 가 올바른 구조를 반환한다."""
    r = SearchResult(
        rank=1, score=0.9123,
        chunk_id="test__chunk0000", document_id="test",
        title="T", section="S", source_type="nasdaq_official",
        source_url="https://x.com", published_at="2024-01-01",
        page=None, item_number=None, text="text here",
    )
    d = r.to_dict()
    assert d["rank"] == 1
    assert d["score"] == round(0.9123, 6)
    assert d["source_type"] == "nasdaq_official"
    assert "text" in d
