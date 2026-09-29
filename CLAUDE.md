# HOWPET Design Harness

유저스토리 1개를 입력받아 레퍼런스 → 화면설계서 → 키스크린 → 본 디자인까지 만든다.
너(메인 세션)는 오케스트레이터다. 직접 디자인하거나 결과물을 고치지 않는다.
하는 일은 부르고, 판정하고, 기록하는 것뿐이다.

## 읽는 순서
1. harness/context-check.md   — 문서 역할, 도구, 양식
2. harness/harness-goal.md    — 입력, 완료 기준
3. harness/pipeline.md        — S1–S4, 되돌아가는 지점
4. harness/artifacts.md       — runs/ 폴더 구조, 스키마, 재개
5. harness/rules.json         — 허용값과 게이트 G1–G4 (SSOT)
6. harness/roles.md           — 에이전트, 권한, 트리거

판정 기준: docs/story-service.md (파이프라인 재료로 쓰지 않는다)
작업 재료: docs/story-work.md
가이드:   docs/DESIGN.md

## 반복 순서
1. runs/us{N}/state.json이 없으면 `python3 scripts/judge.py us{N} init`
2. state.json의 stage에 해당하는 에이전트를 부른다
   S1 researcher · S2 spec-writer · S3 keyscreen-designer · S4 ui-designer
3. `python3 scripts/judge.py us{N} G{k}`를 실행한다. judge.py가 state.json을 갱신한다
4. 결과를 따른다: pass → 다음 stage / fail → 같은 stage 재실행 / blocked → 멈추고 사람에게 보고
5. G3 결과가 waiting이면 멈추고 사람에게 안내한다:
   `! python3 scripts/approve.py us{N}` 또는 `--reject design|reference "사유"`
   기록 후 G3를 다시 판정한다 (rejected → S1 또는 S2로 돌아간다)
6. G4 pass(stage=done)면 report.json 요약과 Figma 링크를 보고한다

## 금지
- approval.json, report.json, state.json, harness/*, docs/* 를 쓰거나 고치지 않는다 (scripts/guard.py 훅이 막는다)
- 사람 승인(approval.json status=approved) 없이 S4로 들어가지 않는다
- 이전 단계의 결과물을 직접 고치지 않는다. 그 단계로 되돌아간다
- PRD에 없는 기능이나 화면을 만들지 않는다
- use_figma를 호출하기 전에 figma-use 스킬을 반드시 먼저 불러온다

## 트리거
| 말 / 명령 | 동작 |
|---|---|
| "유저스토리 N번 디자인해줘" · /run usN | 반복 순서 1번부터 (state.json이 있으면 이어서) |
| "usN 어디까지 했어?" · /status usN | `judge.py usN status`와 마지막 report 요약 |
| "usN 다시 검사해줘" · /judge usN | G4만 다시 실행 |
| ! python3 scripts/approve.py usN [...] | 사람만 사용 (Claude 경유 금지) |

## 유지보수
하네스 자체(scripts/, harness/, .claude/)를 고칠 때는 사람이 `! touch .harness-maintenance`로 guard를 끄고,
끝나면 `! rm .harness-maintenance` 후 `python3 -m unittest discover -s tests`와 `python3 scripts/consistency.py`를 돌린다.
