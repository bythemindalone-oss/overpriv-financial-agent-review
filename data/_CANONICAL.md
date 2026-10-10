# 데이터 정본(canonical) 표기

이 폴더(`02_재현번들/data/`)의 데이터가 **정본**이다.

| 파일 | 역할 |
|------|------|
| `corpus.json` (232 KB) | **정본 코퍼스** (영문, 198 base 태스크). 논문 표3·4를 `run_reference.py`가 정확 재현 |
| `corpus_traps.json` | trap split 18건 (총 216) |
| `corpus.csv` | corpus.json의 표 형식 파생본 |
| `LICENSE` | 데이터 라이선스 |

## corpus.json 변종 주의
프로젝트 이력상 `corpus.json`이 3종 존재하나, **이 파일(232 KB)만 정본**이다. 나머지는 보존용:
- `09_archive/재현번들_0813/corpus.json` (197 KB) — 08-13 중간본
- `09_archive/재현번들_0823_variant/data/corpus.json` (224 KB) — 08-23 재패키지 변종

인용·재채점·표 생성은 반드시 이 폴더 기준으로 수행한다.
