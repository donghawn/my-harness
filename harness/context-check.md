# Context Check (R0)

작성일: 2026-09-30

## 컨텍스트 문서

| 문서 | 역할 | 사용 규칙 |
|---|---|---|
| howpet-prd.md | 서비스 맥락의 원본 | PRD에 없는 요구사항은 만들지 않는다 |
| story-service.md | 판정 기준 | 게이트와 판정자만 참조한다. 파이프라인 설계의 재료로 쓰지 않는다 |
| story-work.md | 파이프라인 재료 | 단계, 산출물, 게이트 위치의 근거로만 쓴다 |
| DESIGN.md | 우리 가이드 (토큰·컴포넌트 규칙) | story-work 7단계 검토와 "어기면 안 되는 것" 1번의 판정 기준 |

## 도구

| 단계 | 도구 | 전제 조건 |
|---|---|---|
| 1. 레퍼런스 수집 | UIBowl + 브라우저 조작 (Playwright 또는 Chrome) | UIBowl 로그인은 사람이 한 번 한다 |
| 4. 키스크린 · 6. 본 디자인 | Figma 공식 플러그인 + `figma-use` 스킬 (use_figma) | Figma 로그인이 필요하다. use_figma를 호출하기 전에 항상 figma-use 스킬을 먼저 불러온다 |

## Figma 작업 파일

- 파일: TBD (URL 확정 후 기입)
- 페이지: `01_Keyscreen` / `02_Tokens` / `03_Components` / `04_Screens`
- 프레임 크기: 390×844 (story-work "어기면 안 되는 것" 3번)

## 산출물 양식

### 레퍼런스 (1단계)
화면 1개마다 스크린샷, UIBowl URL, 한 줄 메모를 남긴다.

### 화면설계서 (3단계), 화면 1개당 마크다운 1개
- 목적
- 대응 유저스토리 번호 (story-service #)
- 섹션 목록 (위→아래)
- 쓰는 컴포넌트 (DESIGN.md 8장 이름 기준)
- 상태: 기본 / 빈 화면 / 오류

## 남은 확인 사항
- [ ] Figma 로그인
- [ ] Figma 파일 URL
- [ ] UIBowl 로그인
