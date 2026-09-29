# Tests

```
python3 tests/make_fixtures.py            # tests/fixtures/ 재생성 (62개)
python3 -m unittest discover -s tests     # judge 샘플 + state 전이 + guard 8개
python3 scripts/consistency.py            # 문서 정합성, diff_count == 0
```

- fixtures/{check_id}/pass: 위반 0건이어야 한다
- fixtures/{check_id}/fail, fail-2: 해당 rule_id 위반이 1건 이상이어야 한다
- 체크를 추가하면 make_fixtures.py의 CASES에 pass/fail 변형을 추가한다
