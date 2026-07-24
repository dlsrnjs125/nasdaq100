"""
src/retrieval/indexer.py
BGE-M3 임베딩 인덱스 생성기

실행:
    python -m src.retrieval.indexer [--refresh]

출력:
    outputs/retrieval/document_embeddings.npy
    outputs/retrieval/document_metadata.json
    outputs/retrieval/index_manifest.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from src.retrieval.chunker import build_embedding_input, chunk_documents
from src.retrieval.config import (
    BATCH_SIZE,
    EMBEDDINGS_FILE,
    MANIFEST_FILE,
    METADATA_FILE,
    MODEL_NAME,
    PRIMARY_SOURCE_TYPES,
    RETRIEVAL_OUT_DIR,
)
from src.retrieval.document_loader import compute_snapshot_hash, load_all_documents
from src.retrieval.embedding_model import encode_texts, get_device, get_embedding_model
from src.retrieval.schemas import DocumentChunk

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def build_index(refresh: bool = False) -> dict:
    """
    전체 인덱스 생성 파이프라인.

    Args:
        refresh: True이면 기존 인덱스를 무시하고 재생성.

    Returns:
        index_manifest dict
    """
    RETRIEVAL_OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 기존 인덱스 확인
    if not refresh and MANIFEST_FILE.exists() and EMBEDDINGS_FILE.exists():
        logger.info("Index already exists. Use --refresh to rebuild.")
        return json.loads(MANIFEST_FILE.read_text())

    t0 = time.time()

    # 1) 문서 로딩
    logger.info("=== Step 1: Loading documents ===")
    all_chunks = load_all_documents(include_source_types=PRIMARY_SOURCE_TYPES)
    if not all_chunks:
        logger.error(
            "No documents loaded. Add .txt files to data/documents/ "
            "or run 'python run_poc.py --refresh' to collect raw data."
        )
        sys.exit(1)

    # 2) 청킹
    logger.info("=== Step 2: Chunking ===")
    chunks, excluded_count = chunk_documents(all_chunks)
    if not chunks:
        logger.error("No valid chunks after filtering. Check MIN_CHUNK_CHARS setting.")
        sys.exit(1)

    # 3) 스냅숏 해시 (재현성)
    input_hash = compute_snapshot_hash(all_chunks)
    logger.info("Input snapshot hash: %s", input_hash[:16])

    # 4) 임베딩 입력 텍스트 생성
    logger.info("=== Step 3: Building embedding inputs ===")
    texts = [build_embedding_input(c) for c in chunks]

    # 5) BGE-M3 임베딩 생성
    logger.info("=== Step 4: Generating embeddings (n=%d) ===", len(texts))
    model = get_embedding_model()
    device = get_device()
    embeddings = encode_texts(texts, batch_size=BATCH_SIZE)
    dim = embeddings.shape[1]
    logger.info("Embeddings shape: %s, device: %s", embeddings.shape, device)

    # 임베딩 배열 해시
    index_hash = hashlib.sha256(embeddings.tobytes()).hexdigest()

    # 6) 저장
    logger.info("=== Step 5: Saving index ===")
    np.save(str(EMBEDDINGS_FILE), embeddings)

    metadata = [
        {
            "chunk_id":    c.chunk_id,
            "document_id": c.document_id,
            "title":       c.title,
            "section":     c.section,
            "source_type": c.source_type,
            "source_url":  c.source_url,
            "published_at": c.published_at,
            "page":        c.page,
            "item_number": c.item_number,
            "text":        c.text,
        }
        for c in chunks
    ]
    METADATA_FILE.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # source_type 별 카운트
    source_counts: dict[str, int] = {}
    for c in chunks:
        source_counts[c.source_type] = source_counts.get(c.source_type, 0) + 1

    manifest = {
        "model_name":          MODEL_NAME,
        "device":              device,
        "embedding_dimension": dim,
        "document_count":      len({c.document_id for c in chunks}),
        "chunk_count":         len(chunks),
        "excluded_chunk_count": excluded_count,
        "source_type_counts":  source_counts,
        "built_at":            datetime.now(timezone.utc).isoformat(),
        "input_snapshot_hash": input_hash,
        "index_snapshot_hash": index_hash,
        "elapsed_seconds":     round(time.time() - t0, 2),
    }
    MANIFEST_FILE.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    logger.info("=== Index build complete ===")
    logger.info("  chunks   : %d", len(chunks))
    logger.info("  excluded : %d", excluded_count)
    logger.info("  dim      : %d", dim)
    logger.info("  device   : %s", device)
    logger.info("  elapsed  : %.1f s", manifest["elapsed_seconds"])
    logger.info("  saved to : %s", RETRIEVAL_OUT_DIR)

    return manifest


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build BGE-M3 retrieval index")
    p.add_argument("--refresh", action="store_true", help="Rebuild even if index exists")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    manifest = build_index(refresh=args.refresh)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
