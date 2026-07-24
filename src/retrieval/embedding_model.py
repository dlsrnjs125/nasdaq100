"""
src/retrieval/embedding_model.py
BAAI/bge-m3 모델 로더 (MPS → CPU fallback, 싱글턴)

사용:
    model = get_embedding_model()
    vecs = encode_texts(["질문 텍스트"])
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

import numpy as np

from src.retrieval.config import BATCH_SIZE, MODEL_NAME

logger = logging.getLogger(__name__)


def _select_device() -> str:
    """MPS → CUDA → CPU 순서로 가용 device를 선택한다."""
    try:
        import torch
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    return "cpu"


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    BAAI/bge-m3 SentenceTransformer 모델을 한 번만 로드하고 캐싱한다.

    로드 우선순위:
      1. BGE_MODEL_PATH 환경변수에 로컬 경로가 지정된 경우 → 해당 디렉터리에서 로드
      2. HuggingFace 캐시에 이미 다운로드된 경우 → 캐시에서 로드
      3. 없으면 HuggingFace Hub에서 다운로드

    MPS 로딩 실패 시 CPU 로 재시도한다.

    Returns:
        SentenceTransformer 인스턴스
    Raises:
        RuntimeError: 모델 로딩 자체가 실패한 경우
    """
    from sentence_transformers import SentenceTransformer  # type: ignore

    from src.retrieval.config import LOCAL_MODEL_PATH

    model_source = LOCAL_MODEL_PATH if LOCAL_MODEL_PATH else MODEL_NAME
    device = _select_device()

    if LOCAL_MODEL_PATH:
        logger.info("Loading model from LOCAL path: %s (device=%s)", LOCAL_MODEL_PATH, device)
    else:
        logger.info("Loading %s from HuggingFace Hub (device=%s) ...", MODEL_NAME, device)

    try:
        model = SentenceTransformer(model_source, device=device)
        logger.info("Model loaded. source=%s device=%s", model_source, device)
        return model
    except Exception as e:
        if device != "cpu":
            logger.warning(
                "Failed to load on %s (%s). Falling back to cpu.", device, e
            )
            try:
                model = SentenceTransformer(model_source, device="cpu")
                logger.info("Model loaded on cpu (fallback). source=%s", model_source)
                return model
            except Exception as e2:
                raise RuntimeError(
                    f"Failed to load model '{model_source}' on cpu: {e2}\n"
                    f"  → HuggingFace Hub에 접속하거나 BGE_MODEL_PATH 환경변수를 설정하세요."
                ) from e2
        raise RuntimeError(
            f"Failed to load model '{model_source}': {e}\n"
            f"  → 해결 방법: BGE_MODEL_PATH=/path/to/bge-m3 python -m src.retrieval.indexer"
        ) from e



def get_device() -> str:
    """현재 로드된 모델의 device 문자열을 반환한다. 미로드 시 선택만 반환."""
    try:
        m = get_embedding_model()
        dev = str(m.device)
        return dev
    except Exception:
        return _select_device()


def encode_texts(
    texts: list[str],
    batch_size: int = BATCH_SIZE,
    normalize: bool = True,
) -> np.ndarray:
    """
    텍스트 리스트를 BGE-M3 임베딩 행렬로 변환한다.

    Args:
        texts: 임베딩할 텍스트 목록. 빈 문자열은 사전 제거된다고 가정.
        batch_size: 배치 크기 (M1 Pro 기본 4).
        normalize: L2 정규화 여부. True이면 cosine sim = 내적.

    Returns:
        shape (n, embedding_dim) 의 float32 numpy 배열.

    Raises:
        ValueError: texts 가 비어 있는 경우.
        RuntimeError: 모델 로딩 실패 시.
    """
    if not texts:
        raise ValueError("encode_texts: texts must not be empty.")

    model = get_embedding_model()
    embeddings: np.ndarray = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=normalize,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return embeddings.astype(np.float32)


def embedding_dim() -> int:
    """모델의 실제 임베딩 차원을 반환한다. 하드코딩하지 않음."""
    vecs = encode_texts(["dimension probe"], batch_size=1)
    return vecs.shape[1]
