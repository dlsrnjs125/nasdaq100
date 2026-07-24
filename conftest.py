# conftest.py — 프로젝트 루트를 sys.path에 추가
import sys
from pathlib import Path

# 프로젝트 루트 (이 파일의 부모)를 path에 등록
sys.path.insert(0, str(Path(__file__).parent.parent))
