# HOWPET Design Harness

유저스토리 1개를 입력하면 **레퍼런스 → 화면설계서 → 키스크린 → 본 디자인**까지 Claude Code 에이전트가 단계별로 만들고, 스크립트가 각 단계를 판정하는 디자인 하네스입니다.

대상 서비스는 [HOWPET](https://notefolio.net/dongpang1717/329570) — 산책하면서 펫티켓을 배우고 실천하는 반려견 산책 앱(iOS)입니다.

## 동작 방식

```
S1 리서치 ─G1→ S2 설계 ─G2→ S3 키스크린 ─G3(사람 승인)→ S4 본 디자인 ─G4→ 완료
```

| 단계 | 에이전트 | 출력 | 게이트 |
|---|---|---|---|
| S1 리서치 | `researcher` | UIBowl 레퍼런스 5–10장, 반영할 점 3–5개 | G1 |
| S2 설계 | `spec-writer` | 화면설계서 md 2–3개 | G2 |
| S3 키스크린 | `keyscreen-designer` | Figma `01_Keyscreen` 프레임 2–3개 | G3 (사람 승인 필요) |
| S4 본 디자인 | `ui-designer` | Figma `02_Tokens`·`03_Components`·`04_Screens` | G4 |

- 메인 세션은 **오케스트레이터**입니다. 직접 디자인하지 않고, 에이전트를 부르고 판정 결과를 따릅니다.
- 게이트 판정은 `scripts/judge.py`가 `harness/rules.json` 기준으로 합니다. Figma는 직접 읽지 않고 각 단계가 남긴 `figma-snapshot.json`만 봅니다.
- 게이트에서 떨어지면 같은 단계를 다시 하고, 계속 떨어지면 멈추고 사람에게 알립니다. S3에서 반려하면 사유에 따라 S1 또는 S2로 돌아갑니다.
- 사람이 승인하지 않으면 S4로 넘어가지 않습니다.

## 완료 기준

유저스토리 1개에 대해 다음을 모두 만족하면 완료입니다.

- Figma `04_Screens` 페이지에 390×844 프레임이 2–3개 있다
- 판정 스크립트의 위반이 0건이다
- 사람 승인 기록이 1건 있다

## 사용법

Claude Code에서 이 폴더를 열고:

| 말 / 명령 | 동작 |
|---|---|
| "유저스토리 2번 디자인해줘" · `/run us2` | 처음부터 시작하거나 멈춘 단계부터 이어서 진행 |
| "us2 어디까지 했어?" · `/status us2` | 현재 단계와 마지막 판정 결과 |
| "us2 다시 검사해줘" · `/judge us2` | G4만 다시 판정 |

키스크린 승인과 반려는 사람이 셸에서 직접 합니다 (Claude가 대신 실행할 수 없습니다).

```bash
! python3 scripts/approve.py us2                                   # 승인
! python3 scripts/approve.py us2 --reject design "사유"            # 반려 → S2로
! python3 scripts/approve.py us2 --reject reference "사유"         # 반려 → S1로
```

### 필요한 것
- Claude Code
- Python 3
- Figma MCP (Figma 작업 전에는 `figma-use` 스킬을 먼저 불러옵니다)

## 폴더 구조

```
.
├─ CLAUDE.md          오케스트레이터 지시문
├─ docs/              판정 기준·작업 재료 (읽기 전용)
│  ├─ howpet-prd.md     PRD
│  ├─ story-service.md  유저스토리와 "어기면 안 되는 것" (판정 기준)
│  ├─ story-work.md     디자인 작업 절차 (작업 재료)
│  └─ DESIGN.md         디자인 가이드
├─ harness/           하네스 설계 문서
│  ├─ context-check.md  문서 역할, 도구, 양식
│  ├─ harness-goal.md   입력, 완료 기준
│  ├─ pipeline.md       S1–S4, 되돌아가는 지점
│  ├─ artifacts.md      runs/ 구조, 스키마, 재개 규칙
│  ├─ rules.json        허용값과 게이트 G1–G4 (SSOT)
│  ├─ roles.md          에이전트, 권한, 트리거
│  └─ verification.md
├─ scripts/
│  ├─ judge.py          게이트 판정, state.json·report.json 갱신
│  ├─ approve.py        사람 승인 기록 (approval.json)
│  ├─ guard.py          PreToolUse 훅: 현재 단계 폴더 밖 쓰기 차단
│  ├─ snapshot_schema.py
│  └─ consistency.py    문서 정합성 검사
├─ .claude/
│  ├─ agents/           researcher · spec-writer · keyscreen-designer · ui-designer · judge
│  ├─ commands/         /run · /status · /judge
│  └─ settings.json     guard 훅 등록
├─ runs/us{N}/        실행 결과 (s1-research · s2-spec · s3-keyscreen · s4-design · state.json)
└─ tests/             판정·가드 테스트와 fixture
```

## 권한과 보호

- 각 에이전트는 `runs/us{N}/` 아래 **자기 단계 폴더에만** 쓸 수 있습니다. `scripts/guard.py` 훅이 `state.json`의 현재 단계를 보고 막습니다.
- `state.json`, `report.json`은 `judge.py`만, `approval.json`은 사람만 씁니다.
- `docs/`, `harness/`, `scripts/`, `.claude/`, `CLAUDE.md`는 Claude가 고칠 수 없습니다.

## 하네스 유지보수

하네스 자체를 고칠 때:

```bash
! touch .harness-maintenance        # guard 끄기
# ... 수정 ...
! rm .harness-maintenance           # guard 켜기
python3 -m unittest discover -s tests
python3 scripts/consistency.py      # diff_count == 0 이어야 함
```

fixture를 다시 만들려면 `python3 tests/make_fixtures.py`를 실행합니다. 자세한 내용은 [tests/README.md](tests/README.md)를 보세요.
