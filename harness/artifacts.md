# Artifacts (R4)

## 폴더 구조
한 번 실행할 때마다 `runs/us{유저스토리 번호}/` 폴더를 하나 만든다.

```
runs/us{N}/
├─ s1-research/
│  ├─ refs/ref-{01..10}.png
│  ├─ refs.json
│  └─ insights.md
├─ s2-spec/
│  └─ screen-{01..03}.md
├─ s3-keyscreen/
│  ├─ figma-snapshot.json
│  └─ approval.json
├─ s4-design/
│  ├─ figma-snapshot.json
│  └─ report.json
└─ state.json
```

## 파일 스키마

| 파일 | 스키마 |
|---|---|
| refs.json | `[{id, url, app, note}]`, 5–10개. `url`은 uibowl 도메인 |
| insights.md | 반영할 점 3–5개. 각 항목에 근거 ref id를 1개 이상 적는다 |
| screen-NN.md | context-check.md의 화면설계서 양식 (목적 / 유저스토리 # / 섹션 / 컴포넌트 / 상태) |
| figma-snapshot.json | `{pages: [{page, frames: [{name, width, height, nodes: [{id, type, name?, characters?, fills[], radius?, fontSize?, fontWeight?, padding[]?, gap?}]}]}]}`. S3는 01_Keyscreen, S4는 02–04 페이지만 허용 (scripts/snapshot_schema.py) |
| approval.json | `{us, status: "approved" \| "rejected", reason, reason_type: "design" \| "reference", date}` |
| report.json | `{us, count, violations: [{rule_id, node_id, frame, actual, expected}]}` |
| state.json | `{us, stage: "S1" \| "S2" \| "S3" \| "S4" \| "done" \| "blocked", retry: {G1, G2}, s4_retry: {rule_id: n}, last_gate, updated}`. scripts/judge.py만 쓴다 |

## Figma 판정 방식
- S3와 S4가 끝날 때 use_figma로 해당 페이지를 figma-snapshot.json에 덤프한다.
- 판정 스크립트는 Figma를 직접 읽지 않는다. snapshot 파일만 읽는다.

## 규칙 SSOT
- `rules.json` 1개에 모은다. 게이트와 판정자는 이 파일만 참조한다.
- 원본은 DESIGN.md(사람이 읽는 문서)이고, rules.json에는 셀 수 있는 값만 옮긴다.
- 들어갈 항목 (구체 값은 R5에서 확정):
  - colors: DESIGN.md의 역할별 색상 토큰 HEX (Light/Dark)
  - radius: [2,4,6,8,10,12,14,16,20,24,9999]
  - fontSize: [11,12,13,14,16,18,20,22,24,26]
  - fontWeight: [400,500,700]
  - spacing: [2,4,6,8,10,12,14,16,18,20,24,28,32,36,40,48,52,56,64]
  - frame: 390×844
  - service: story-service "어기면 안 되는 것" 관련 조건

## 재개 규칙
- 시작할 때 state.json을 읽고 `stage`부터 이어서 한다.
- 어떤 단계가 끝났다고 보는 조건: 그 단계의 출력 파일이 있고, 그 단계의 게이트를 통과했다.
- S3는 approval.json의 status가 "approved"일 때만 끝난 것으로 본다.
