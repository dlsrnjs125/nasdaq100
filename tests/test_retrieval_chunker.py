"""
tests/test_retrieval_chunker.py
청킹·문서 로더 단위 테스트 — 네트워크·모델 다운로드 불필요
"""
from __future__ import annotations

import pytest

from src.retrieval.chunker import (
    build_embedding_input,
    chunk_documents,
    compute_chunk_id,
)
from src.retrieval.schemas import DocumentChunk


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_chunk(
    chunk_id: str = "doc__chunk0000",
    document_id: str = "doc",
    title: str = "Test Document",
    section: str = "Section A",
    source_type: str = "nasdaq_official",
    source_url: str = "https://example.com",
    text: str = "This is a test chunk with enough content to pass minimum length filters.",
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        title=title,
        section=section,
        source_type=source_type,
        source_url=source_url,
        published_at="2024-01-01",
        page=None,
        item_number=None,
        text=text,
    )


# ── 청크 생성 기본 동작 ────────────────────────────────────────────────────────

def test_short_chunk_excluded():
    """MIN_CHUNK_CHARS 미만 청크는 제외된다."""
    doc = _make_chunk(text="Too short.")
    chunks, excluded = chunk_documents([doc], min_chars=80)
    assert excluded == 1
    assert len(chunks) == 0


def test_valid_chunk_included():
    """충분한 길이의 청크는 포함된다."""
    doc = _make_chunk(text="A" * 200)
    chunks, excluded = chunk_documents([doc], min_chars=80)
    assert excluded == 0
    assert len(chunks) == 1


def test_empty_documents_returns_empty():
    """빈 문서 리스트는 빈 결과를 반환한다."""
    chunks, excluded = chunk_documents([])
    assert chunks == []
    assert excluded == 0


def test_chunk_ids_deterministic():
    """동일 입력에서 동일 chunk_id를 생성한다."""
    doc = _make_chunk(text="B" * 300)
    chunks1, _ = chunk_documents([doc])
    chunks2, _ = chunk_documents([doc])
    ids1 = [c.chunk_id for c in chunks1]
    ids2 = [c.chunk_id for c in chunks2]
    assert ids1 == ids2


def test_long_text_split_into_multiple_chunks():
    """CHUNK_SIZE를 초과하는 텍스트는 여러 청크로 분할된다."""
    long_text = ("This is a sentence. " * 200)  # ~4000 chars
    doc = _make_chunk(text=long_text)
    chunks, _ = chunk_documents([doc], chunk_size=500, overlap=50, min_chars=10)
    assert len(chunks) > 1


def test_metadata_preserved_after_chunking():
    """청킹 후 메타데이터가 유지된다."""
    doc = _make_chunk(
        document_id="myDoc",
        title="My Title",
        section="My Section",
        source_type="sec_official",
        source_url="https://sec.gov/test",
        text="C" * 300,
    )
    chunks, _ = chunk_documents([doc])
    assert len(chunks) >= 1
    c = chunks[0]
    assert c.document_id == "myDoc"
    assert c.title == "My Title"
    assert c.source_type == "sec_official"
    assert c.source_url == "https://sec.gov/test"


def test_chunks_sorted_by_chunk_id():
    """결과 청크는 chunk_id 기준으로 정렬된다."""
    docs = [
        _make_chunk(chunk_id="z__chunk0000", text="Z" * 200),
        _make_chunk(chunk_id="a__chunk0000", text="A" * 200),
    ]
    chunks, _ = chunk_documents(docs)
    ids = [c.chunk_id for c in chunks]
    assert ids == sorted(ids)


# ── build_embedding_input ────────────────────────────────────────────────────

def test_build_embedding_input_includes_title_section_text():
    """임베딩 입력 텍스트에 Title / Section / Text 가 포함된다."""
    doc = _make_chunk(title="My Doc", section="Intro", text="Hello world.")
    result = build_embedding_input(doc)
    assert "Title: My Doc" in result
    assert "Section: Intro" in result
    assert "Text: Hello world." in result


def test_build_embedding_input_includes_source_type():
    """임베딩 입력 텍스트에 Source Type이 포함된다."""
    doc = _make_chunk(source_type="sec_official")
    result = build_embedding_input(doc)
    assert "Source Type: sec_official" in result


# ── compute_chunk_id ─────────────────────────────────────────────────────────

def test_compute_chunk_id_deterministic():
    """동일 입력에서 동일 chunk_id를 반환한다."""
    id1 = compute_chunk_id("docA", "SectionB", 0)
    id2 = compute_chunk_id("docA", "SectionB", 0)
    assert id1 == id2


def test_compute_chunk_id_different_for_different_inputs():
    """다른 입력에서 다른 chunk_id를 반환한다."""
    id1 = compute_chunk_id("docA", "SectionB", 0)
    id2 = compute_chunk_id("docA", "SectionB", 1)
    assert id1 != id2


# ── document_loader 기본 동작 ────────────────────────────────────────────────

def test_no_fake_data_generated_when_no_documents(tmp_path, monkeypatch):
    """문서가 없을 때 빈 리스트를 반환하고 가짜 데이터를 생성하지 않는다."""
    import src.retrieval.document_loader as dl
    monkeypatch.setattr(dl, "DOCUMENTS_DIR", tmp_path / "docs")
    monkeypatch.setattr(dl, "RAW_DATA_DIR", tmp_path / "raw")

    chunks = dl.load_all_documents()
    assert chunks == []


def test_snapshot_hash_deterministic():
    """동일 청크 리스트에서 동일 스냅숏 해시를 반환한다."""
    from src.retrieval.document_loader import compute_snapshot_hash
    chunks = [
        _make_chunk(chunk_id="x", text="Hello"),
        _make_chunk(chunk_id="y", text="World"),
    ]
    h1 = compute_snapshot_hash(chunks)
    h2 = compute_snapshot_hash(chunks)
    assert h1 == h2
    assert len(h1) == 64  # SHA256 hex


def test_snapshot_hash_differs_for_different_content():
    """내용이 다른 청크 리스트는 다른 해시를 반환한다."""
    from src.retrieval.document_loader import compute_snapshot_hash
    chunks_a = [_make_chunk(chunk_id="a", text="Alpha")]
    chunks_b = [_make_chunk(chunk_id="a", text="Beta")]
    assert compute_snapshot_hash(chunks_a) != compute_snapshot_hash(chunks_b)
