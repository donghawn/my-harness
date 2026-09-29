# Roles (R6)

## 에이전트

| 에이전트 | 단계 | 편집 가능 폴더 (이 폴더만) | 읽기만 가능 |
|---|---|---|---|
| `researcher` | S1 | `runs/us{N}/s1-research/` | howpet-prd.md, story-service.md |
| `spec-writer` | S2 | `runs/us{N}/s2-spec/` | S1 결과물, howpet-prd.md, DESIGN.md, context-check.md |
| `keyscreen-designer` | S3 | `runs/us{N}/s3-keyscreen/` (단 `approval.json` 제외) + Figma `01_Keyscreen` | S2 결과물, DESIGN.md |
| `ui-designer` | S4 | `runs/us{N}/s4-design/` (단 `report.json` 제외) + Figma `02_Tokens`·`03_Components`·`04_Screens` | 승인된 S3 결과물, DESIGN.md, rules.json |
| `judge` | G1–G4 판정 | 없음 (읽기 전용) | 모든 파일 |

- Figma 페이지 제한은 로컬 경로로 막을 수 없다. 에이전트 지시문에 적고, 판정 스크립트가 허용되지 않은 페이지의 변경을 확인한다.
- Figma 작업 전에는 항상 `figma-use` 스킬을 먼저 불러온다.

## 판정자 권한
- `judge` 도구: `Read`, `Bash(python scripts/judge.py *)` 두 가지뿐이다.
- `report.json`은 `scripts/judge.py`만 쓴다.
- `approval.json`은 사람이 `! python scripts/approve.py`로만 쓴다. 훅이 Claude의 쓰기를 막는다.
- `rules.json`, `DESIGN.md`, `story-service.md`, `story-work.md`, `howpet-prd.md`는 모든 에이전트가 읽기만 한다. 훅이 쓰기를 막는다.

## 트리거

| 트리거 (자연어 / 명령) | 동작 |
|---|---|
| "유저스토리 2번 디자인해줘" / `/run us2` | `runs/us2/`를 만들거나 이어서 하고 state.json의 단계부터 진행 |
| "us2 어디까지 했어?" / `/status us2` | state.json과 마지막 게이트 결과를 보여줌 |
| `! python scripts/approve.py us2` · `! python scripts/approve.py us2 --reject design\|reference "사유"` | approval.json 작성. 사람이 `!`로 셸에서 직접 실행한다 (Claude 경유 금지) |
| "us2 다시 검사해줘" / `/judge us2` | G4만 다시 실행 |

## 넘김 규칙
- 에이전트끼리는 파일로만 결과를 넘긴다. 직접 대화하지 않는다.
- 오케스트레이터(메인 세션)가 게이트 통과를 확인한 뒤 다음 에이전트를 부른다.
- 폴더 제한은 `scripts/guard.py` (PreToolUse 훅)가 state.json의 stage 기준으로 강제한다.
