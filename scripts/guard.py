#!/usr/bin/env python3
"""PreToolUse 훅: 에이전트가 현재 stage 폴더에만 쓰게 한다.

- Write/Edit/MultiEdit/NotebookEdit: 저장소 안 경로는 runs/us{N}/{현재 stage 폴더}/ 만 허용.
  approval.json, report.json, state.json 은 항상 차단.
- Bash: 승인 기록·보호 파일을 건드리는 명령을 차단.
- 저장소 밖 경로(스크래치패드 등)는 관여하지 않는다.
- 사람이 `! touch .harness-maintenance` 로 만든 파일이 있으면 유지보수 모드로 모두 허용한다.

차단 시 exit 2 + stderr 메시지 (Claude Code 훅 규약).
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE_DIRS = {"S1": "s1-research", "S2": "s2-spec", "S3": "s3-keyscreen", "S4": "s4-design"}
ALWAYS_BLOCKED_NAMES = {"approval.json", "report.json", "state.json"}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
MAINT_FLAG = ".harness-maintenance"

# Bash: 이름만 나와도 차단
BASH_FORBIDDEN = [r"approval\.json", r"approve\.py", r"\.harness-maintenance"]
# Bash: 보호 경로 + 쓰기 연산이 함께 나오면 차단
BASH_PROTECTED = [r"docs/", r"harness/", r"scripts/", r"\.claude/", r"CLAUDE\.md",
                  r"rules\.json", r"report\.json", r"state\.json"]
BASH_WRITE_OPS = [r">", r"\btee\b", r"\bsed\s+-i", r"\brm\b", r"\bmv\b", r"\bcp\b", r"\btruncate\b",
                  r"\bchmod\b", r"\bln\b", r"open\([^)]*['\"][wa]", r"write_text", r"\bperl\s+-p?i"]


def decide(payload, repo=REPO):
    """(allowed: bool, reason: str)"""
    if os.path.exists(os.path.join(repo, MAINT_FLAG)):
        return True, "maintenance mode"
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input", {}) or {}

    if tool == "Bash":
        cmd = ti.get("command", "")
        for pat in BASH_FORBIDDEN:
            if re.search(pat, cmd):
                return False, "승인 기록/유지보수 플래그는 사람만 다룬다 (`! python3 scripts/approve.py ...`)"
        if re.match(r"^\s*python3?\s+scripts/judge\.py\s", cmd):
            return True, "judge"
        if any(re.search(p, cmd) for p in BASH_PROTECTED) and any(re.search(o, cmd) for o in BASH_WRITE_OPS):
            return False, "보호 경로를 수정하는 Bash 명령은 차단된다"
        return True, "bash ok"

    if tool not in WRITE_TOOLS:
        return True, "not a write"

    path = ti.get("file_path") or ti.get("notebook_path") or ""
    if not path:
        return True, "no path"
    cwd = payload.get("cwd") or repo
    ap = os.path.realpath(path if os.path.isabs(path) else os.path.join(cwd, path))
    repo_real = os.path.realpath(repo)
    if not (ap == repo_real or ap.startswith(repo_real + os.sep)):
        return True, "outside repo"
    rel = os.path.relpath(ap, repo_real).replace(os.sep, "/")

    if os.path.basename(rel) in ALWAYS_BLOCKED_NAMES:
        return False, "%s 은(는) 스크립트/사람만 쓴다" % os.path.basename(rel)
    m = re.match(r"^runs/(us[1-6])/([^/]+)/", rel)
    if not m:
        return False, "runs/us{N}/{현재 stage 폴더}/ 밖에는 쓸 수 없다: %s" % rel
    state_file = os.path.join(repo_real, "runs", m.group(1), "state.json")
    if not os.path.isfile(state_file):
        return False, "state.json이 없다. 먼저 `python3 scripts/judge.py %s init`" % m.group(1)
    with open(state_file, encoding="utf-8") as f:
        stage = json.load(f).get("stage")
    allowed_dir = STAGE_DIRS.get(stage)
    if m.group(2) != allowed_dir:
        return False, "현재 stage=%s: runs/%s/%s/ 에만 쓸 수 있다" % (stage, m.group(1), allowed_dir)
    return True, "stage folder"


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    ok, reason = decide(payload)
    if ok:
        return 0
    print("[guard] 차단: %s" % reason, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
