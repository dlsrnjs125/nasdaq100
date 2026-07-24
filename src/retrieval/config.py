"""
src/retrieval/config.py
BGE-M3 검색 모듈 설정 상수
"""
from __future__ import annotations

import os
from pathlib import Path

# ── Model ──────────────────────────────────────────────────────────────────────
MODEL_NAME  = "BAAI/bge-m3"

# 로컬 모델 경로 (환경 변수로 지정 가능)
# 예: export BGE_MODEL_PATH=/Users/yourname/models/bge-m3
# 설정되면 HuggingFace 허브 대신 로컬 디렉터리에서 로드
LOCAL_MODEL_PATH: str | None = os.environ.get("BGE_MODEL_PATH", None)
BATCH_SIZE  = 4           # M1 Pro MPS / CPU 기본값
MAX_QUERY_CHARS = 2048    # 검색어 최대 길이 (문자 수)

# ── Chunking ───────────────────────────────────────────────────────────────────
CHUNK_SIZE    = 2000   # 청크 최대 길이 (문자 수)
CHUNK_OVERLAP = 200    # 청크 간 오버랩 (문자 수)
MIN_CHUNK_CHARS = 80   # 이 길이 미만 청크는 인덱스에서 제외

# ── Source type 필터 ─────────────────────────────────────────────────────────
PRIMARY_SOURCE_TYPES = ["nasdaq_official", "sec_official", "company_ir"]

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT      = Path(__file__).parent.parent.parent
RAW_DATA_DIR      = PROJECT_ROOT / "data" / "raw"
DOCUMENTS_DIR     = PROJECT_ROOT / "data" / "documents"
RETRIEVAL_OUT_DIR = PROJECT_ROOT / "outputs" / "retrieval"

EMBEDDINGS_FILE  = RETRIEVAL_OUT_DIR / "document_embeddings.npy"
METADATA_FILE    = RETRIEVAL_OUT_DIR / "document_metadata.json"
MANIFEST_FILE    = RETRIEVAL_OUT_DIR / "index_manifest.json"
