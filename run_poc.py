#!/usr/bin/env python3
"""
run_poc.py — Nasdaq-100 편입·편출 관찰 후보 PoC 진입점

사용법:
  python run_poc.py           # 기존 raw 스냅숏 사용
  python run_poc.py --refresh # 외부 데이터 재수집
"""
import argparse
import sys

from src.pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Nasdaq-100 편입·편출 관찰 후보 PoC"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="외부 데이터를 새로 수집하여 raw 스냅숏을 갱신한다.",
    )
    args = parser.parse_args()

    try:
        result = run(refresh=args.refresh)
        sys.exit(0 if result["overall_result"] in ("PASS", "CONDITIONAL_PASS") else 1)
    except Exception as exc:
        print(f"\n[ERROR] 파이프라인 실패: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
