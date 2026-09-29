# Verification (R8)

## 1. judge.py 샘플 테스트
- 위치: `tests/fixtures/{check_id}/pass/`, `tests/fixtures/{check_id}/fail/`
- 체크마다 통과 샘플 1개 + 실패 샘플 1개를 둔다. 체크 28개(G1 5 · G2 8 · G3 4 · G4 11) × 2 = 56개
- 서비스 규칙 체크 6개(SVC-01, 02, 03, 04a, 04b, 05)는 실패 샘플을 2개씩 둔다 (+6개, 합계 62개)
- 합격 기준
  - pass 샘플: violations == 0
  - fail 샘플: 해당 rule_id 위반 >= 1
  - 62개 모두 맞아야 한다

## 2. guard.py 훅 테스트 (8개, 모두 통과)

| # | 동작 | 기대 결과 |
|---|---|---|
| 1 | 현재 stage 폴더에 Write | 허용 |
| 2 | 읽기 전용 파일 Read | 허용 |
| 3 | `python scripts/judge.py` 실행 | 허용 |
| 4 | 다른 stage 폴더에 Write | 차단 |
| 5 | `approval.json` Write | 차단 |
| 6 | `harness/rules.json` Edit | 차단 |
| 7 | `docs/` 아래 파일 Write | 차단 |
| 8 | Bash로 `approval.json` 조작 | 차단 |

## 3. e2e 시나리오: 유저스토리 #2
- 전제 조건: Figma 로그인, Figma 파일 URL, UIBowl 로그인 (context-check.md)
- 순서
  1. `/run us2` → S1 → G1 → S2 → G2 → S3 → G3 대기
  2. `! python scripts/approve.py us2 --reject design "테스트 반려"` → S2로 복귀하는지 확인
  3. S2 도중 세션 종료 → 다시 `/run us2` → S2부터 이어서 하는지 확인
  4. 승인 → S4 → G4
- 합격 기준: harness-goal.md 완료 기준 4개 모두 충족, 반려 복귀 1회와 재개 1회를 확인

## 4. 리뷰
- `scripts/*.py` 3개: `/code-review` medium, 발견 사항 모두 처리
- 문서 정합성 스크립트 (`scripts/consistency.py`), 차이 0이어야 한다
  - rules.json의 체크 id ⊆ verification.md의 fixtures 목록
  - DESIGN.md 2.2–2.6절(역할별 색상, HOWPET 보조색)의 HEX ⊆ rules.json allowed.colors (2.1 팔레트는 직접 사용 금지라 대상에서 제외)
- 최종 판단: 본인이 e2e 결과 Figma를 보고 승인
