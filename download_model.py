"""
download_model.py
BGE-M3 모델을 프로젝트 내 models/bge-m3/ 폴더에 다운로드하고
.env 파일에 BGE_MODEL_PATH를 자동으로 등록합니다.

사용법:
    .venv/bin/python download_model.py

다운로드 완료 후에는 .env에 BGE_MODEL_PATH가 설정되어
인터넷 없이도 로컬 모델을 사용할 수 있습니다.
"""
import os
import sys
import time
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
LOCAL_MODEL_DIR = PROJECT_ROOT / "models" / "bge-m3"
ENV_FILE = PROJECT_ROOT / ".env"
MODEL_NAME = "BAAI/bge-m3"

# !! 반드시 다른 HuggingFace 라이브러리 임포트 전에 설정해야 합니다 !!
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import huggingface_hub.constants as _hf_const
_hf_const.ENDPOINT = "https://hf-mirror.com"


def update_env_file(key: str, value: str) -> None:
    """
    .env 파일에서 key=value 항목을 추가하거나 업데이트한다.
    이미 같은 key가 있으면 덮어쓰고, 없으면 마지막에 추가한다.
    """
    lines: list[str] = []
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines(keepends=True)

    updated = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
            lines[i] = f'{key}="{value}"\n'
            updated = True
            break

    if not updated:
        # 파일 끝에 빈 줄 없으면 추가
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        lines.append(f'{key}="{value}"\n')

    ENV_FILE.write_text("".join(lines), encoding="utf-8")


def is_model_complete(path: Path) -> bool:
    """
    모델 디렉터리가 유효한지 확인한다.
    sentence_transformers 로드에 필요한 최소 파일을 체크.
    """
    required = ["config.json", "tokenizer_config.json"]
    has_weights = any(
        path.glob("*.safetensors")
    ) or any(path.glob("pytorch_model*.bin"))
    return all((path / f).exists() for f in required) and has_weights


def main() -> None:
    print("\n" + "=" * 60)
    print("  BGE-M3 로컬 다운로드")
    print(f"  저장 경로   : {LOCAL_MODEL_DIR}")
    print(f"  엔드포인트  : {_hf_const.ENDPOINT}")
    print("=" * 60)

    # ── 이미 다운로드된 경우 확인 ────────────────────────────────────────────
    if LOCAL_MODEL_DIR.exists() and is_model_complete(LOCAL_MODEL_DIR):
        print(f"\n✅ 모델이 이미 존재합니다: {LOCAL_MODEL_DIR}")
        print("   재다운로드 없이 .env 경로만 확인합니다.\n")
        update_env_file("BGE_MODEL_PATH", str(LOCAL_MODEL_DIR))
        print(f"✅ .env 파일 확인 완료: BGE_MODEL_PATH={LOCAL_MODEL_DIR}\n")
        _verify_load()
        return

    # ── 폴더 생성 ────────────────────────────────────────────────────────────
    LOCAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 저장 폴더: {LOCAL_MODEL_DIR}")
    print("⏳ 다운로드 중... (최초 실행 시 약 2.3 GB, 시간이 걸릴 수 있습니다)\n")

    try:
        from huggingface_hub import snapshot_download

        t0 = time.time()
        snapshot_download(
            repo_id=MODEL_NAME,
            local_dir=str(LOCAL_MODEL_DIR),
            # 불필요한 대용량 파일 제외 (ONNX, gguf 등)
            ignore_patterns=["*.onnx", "*.gguf", "flax_model*", "tf_model*", "rust_model*"],
        )
        elapsed = time.time() - t0
        print(f"\n✅ 다운로드 완료! (소요 시간: {elapsed:.1f}초)")

    except Exception as e:
        print(f"\n❌ 다운로드 실패: {e}")
        print("\n해결 방법:")
        print("  1. 네트워크 연결 상태를 확인하세요.")
        print("  2. VPN 연결 후 재시도하세요.")
        print("  3. 수동 다운로드: https://huggingface.co/BAAI/bge-m3/tree/main")
        print(f"     → 파일을 {LOCAL_MODEL_DIR} 에 저장 후 다시 실행하세요.")
        sys.exit(1)

    # ── .env 업데이트 ────────────────────────────────────────────────────────
    update_env_file("BGE_MODEL_PATH", str(LOCAL_MODEL_DIR))
    print(f"\n✅ .env 업데이트 완료:")
    print(f"   BGE_MODEL_PATH={LOCAL_MODEL_DIR}")

    # ── 로드 검증 ────────────────────────────────────────────────────────────
    _verify_load()


def _verify_load() -> None:
    """다운로드된 모델을 실제로 로드하고 인코딩까지 검증한다."""
    print("\n🔍 모델 로드 검증 중...\n")
    try:
        from sentence_transformers import SentenceTransformer

        t0 = time.time()
        model = SentenceTransformer(str(LOCAL_MODEL_DIR), device="cpu")
        elapsed = time.time() - t0

        dim = model.get_sentence_embedding_dimension()
        print(f"✅ 모델 로드 성공!")
        print(f"   임베딩 차원 : {dim}")
        print(f"   소요 시간   : {elapsed:.1f}초")

        # 유사도 테스트
        sentences = [
            "That is a happy person",
            "That is a happy dog",
            "That is a very happy person",
            "Today is a sunny day",
        ]
        embeddings = model.encode(sentences)
        similarities = model.similarity(embeddings, embeddings)
        print(f"\n   유사도 행렬 shape : {similarities.shape}")
        print("✅ 동작 확인 완료\n")

        print("=" * 60)
        print("  이제 로컬 모델을 사용할 수 있습니다!")
        print("  .env 파일에 BGE_MODEL_PATH가 설정되었으므로")
        print("  인터넷 없이도 자동으로 로컬 모델이 로드됩니다.")
        print("=" * 60 + "\n")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ 모델 로드 실패: {e}")
        print(f"   모델 파일이 올바른지 확인하세요: {LOCAL_MODEL_DIR}")
        sys.exit(1)


if __name__ == "__main__":
    main()
