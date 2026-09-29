#!/usr/bin/env python3
"""사람 승인 기록. Claude가 아니라 사람이 `!` 로 직접 실행한다.

  ! python3 scripts/approve.py us2
  ! python3 scripts/approve.py us2 --reject design "사유"
  ! python3 scripts/approve.py us2 --reject reference "사유"

기록 후 `python3 scripts/judge.py us{N} G3` 로 판정하면 state.json이 갱신된다.
"""
import argparse
import datetime
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("us")
    ap.add_argument("--reject", nargs=2, metavar=("REASON_TYPE", "REASON"))
    ap.add_argument("--root", default=REPO)
    a = ap.parse_args(argv)
    m = re.match(r"^us([1-6])$", a.us)
    if not m:
        print("us must be us1..us6", file=sys.stderr)
        return 2
    us = int(m.group(1))
    run = os.path.join(a.root, "runs", "us%d" % us)
    st_path = os.path.join(run, "state.json")
    if not os.path.isfile(st_path):
        print("runs/us%d/state.json not found" % us, file=sys.stderr)
        return 2
    with open(st_path, encoding="utf-8") as f:
        stage = json.load(f).get("stage")
    if stage != "S3":
        print("approval is only recorded at stage S3 (now %s)" % stage, file=sys.stderr)
        return 2
    if a.reject and a.reject[0] not in ("design", "reference"):
        print("REASON_TYPE must be design or reference", file=sys.stderr)
        return 2
    rec = {
        "us": us,
        "status": "rejected" if a.reject else "approved",
        "reason": a.reject[1] if a.reject else "",
        "reason_type": a.reject[0] if a.reject else None,
        "date": datetime.date.today().isoformat(),
    }
    out = os.path.join(run, "s3-keyscreen", "approval.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    print("다음: python3 scripts/judge.py us%d G3" % us)
    return 0


if __name__ == "__main__":
    sys.exit(main())
