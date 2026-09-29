#!/usr/bin/env python3
"""문서 정합성 대조. 차이가 0이어야 한다 (harness/verification.md 4절).

1. rules.json의 모든 체크 id에 tests/fixtures/{id}/pass, fail* 이 있다
2. DESIGN.md 2.2–2.4, 2.6절(역할별 색상, HOWPET 보조색)의 HEX ⊆ rules.json allowed.colors
   (2.1 팔레트는 직접 사용 금지, 2.5 그라데이션 stop은 단색 fill이 아니라 제외)
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEX = re.compile(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?\b")


def norm(h):
    h = h.lower()
    return h[:7] if len(h) == 9 and h.endswith("ff") else h


def section(text, start, end):
    s = text.index(start)
    e = text.index(end, s)
    return text[s:e]


def main():
    rules = json.load(open(os.path.join(REPO, "harness", "rules.json"), encoding="utf-8"))
    diffs = []
    fx = os.path.join(REPO, "tests", "fixtures")
    for g in rules["gates"].values():
        for c in g["checks"]:
            d = os.path.join(fx, c["id"])
            has_pass = os.path.isdir(os.path.join(d, "pass"))
            has_fail = os.path.isdir(d) and any(n.startswith("fail") for n in os.listdir(d))
            if not (has_pass and has_fail):
                diffs.append("fixtures missing for %s" % c["id"])

    design = open(os.path.join(REPO, "docs", "DESIGN.md"), encoding="utf-8").read()
    text = section(design, "### 2.2", "### 2.5") + section(design, "### 2.6", "### 2.7")
    allowed = {norm(x) for t in rules["allowed"]["colors"].values() for x in t.values()}
    allowed |= {norm(x) for x in rules["allowed"]["colors_extra"]}
    for h in sorted({norm(h) for h in HEX.findall(text)}):
        if h not in allowed:
            diffs.append("DESIGN.md color %s not in rules.json allowed.colors" % h)

    print(json.dumps({"diff_count": len(diffs), "diffs": diffs}, ensure_ascii=False, indent=2))
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
