#!/usr/bin/env python3
"""HOWPET 하네스 판정 스크립트.

usage:
  python3 scripts/judge.py us{N} init      # runs/us{N}/ 와 state.json 생성
  python3 scripts/judge.py us{N} status    # state.json 출력
  python3 scripts/judge.py us{N} G1|G2|G3|G4 [--root DIR] [--rules FILE]

규칙은 harness/rules.json(SSOT)만 읽는다. Figma는 직접 읽지 않고 figma-snapshot.json만 읽는다.
state.json은 이 스크립트만 갱신한다 (에이전트는 guard.py가 막는다).

exit code: 0 pass · 1 fail · 2 입력/사용 오류 · 3 사람 승인 대기
"""
import argparse
import datetime
import json
import os
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_schema  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RULES = os.path.join(REPO, "harness", "rules.json")

STAGE_DIRS = {"S1": "s1-research", "S2": "s2-spec", "S3": "s3-keyscreen", "S4": "s4-design"}
GATE_STAGE = {"G1": "S1", "G2": "S2", "G3": "S3", "G4": "S4"}
NEXT_STAGE = {"G1": "S2", "G2": "S3", "G3": "S4", "G4": "done"}
SPEC_HEADERS = ["목적", "유저스토리", "섹션", "컴포넌트", "상태"]
REQUIRED_STATES = ["기본", "빈 화면", "오류"]
BRAND_HEX = "#10ab7d"
NEUTRAL_PREFIXES = ("fg.neutral", "bg.layer", "bg.neutral", "stroke.neutral", "fg.disabled",
                    "bg.disabled", "fg.placeholder", "bg.overlay", "bg.transparent", "palette.static")


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def norm_hex(h):
    h = h.lower()
    if len(h) == 9 and h.endswith("ff"):
        h = h[:7]
    return h


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def v(rule_id, actual, expected, frame=None, node_id=None, file=None):
    out = {"rule_id": rule_id, "actual": actual, "expected": expected}
    if frame is not None:
        out["frame"] = frame
    if node_id is not None:
        out["node_id"] = node_id
    if file is not None:
        out["file"] = file
    return out


class InputError(Exception):
    pass


# ---------------------------------------------------------------- parsing

def parse_spec(path):
    """## 헤더 기준으로 섹션을 나눈다. {header: {"text": str, "items": [str]}}"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    sections, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1)
            sections[cur] = {"text": "", "items": []}
            continue
        if cur is None:
            continue
        sections[cur]["text"] += line + "\n"
        im = re.match(r"^\s*[-*]\s+(.+?)\s*$", line)
        if im:
            sections[cur]["items"].append(im.group(1))
    return text, sections


def item_name(item):
    return re.split(r"[:：(]", item.replace("`", ""), maxsplit=1)[0].strip()


def spec_files(run):
    d = os.path.join(run, STAGE_DIRS["S2"])
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d) if re.match(r"^screen-\d{2}\.md$", f))


def load_snapshot(run, stage, pages):
    path = os.path.join(run, STAGE_DIRS[stage], "figma-snapshot.json")
    if not os.path.isfile(path):
        raise InputError("missing %s" % os.path.relpath(path, run))
    try:
        snap = load_json(path)
    except ValueError as e:
        raise InputError("invalid JSON in figma-snapshot.json: %s" % e)
    errors = snapshot_schema.validate(snap, set(pages))
    if errors:
        raise InputError("figma-snapshot.json schema: " + "; ".join(errors))
    return {p["page"]: p["frames"] for p in snap["pages"]}


# ---------------------------------------------------------------- gates

def gate_g1(run, us, rules):
    out = []
    d = os.path.join(run, STAGE_DIRS["S1"])
    refs_path = os.path.join(d, "refs.json")
    if not os.path.isfile(refs_path):
        raise InputError("missing s1-research/refs.json")
    refs = load_json(refs_path)
    if not isinstance(refs, list):
        raise InputError("refs.json must be a list")
    if not 5 <= len(refs) <= 10:
        out.append(v("G1-01", len(refs), "5..10", file="refs.json"))
    ids = set()
    for r in refs:
        rid, url = r.get("id"), r.get("url", "")
        ids.add(rid)
        host = urlparse(url).hostname or ""
        if "uibowl" not in host.lower().split("."):
            out.append(v("G1-02", url, "uibowl host", file="refs.json"))
        if not rid or not os.path.isfile(os.path.join(d, "refs", "%s.png" % rid)):
            out.append(v("G1-03", rid, "refs/%s.png exists" % rid, file="refs.json"))
    ins_path = os.path.join(d, "insights.md")
    items = []
    if os.path.isfile(ins_path):
        with open(ins_path, encoding="utf-8") as f:
            items = [m.group(1) for m in (re.match(r"^\s*[-*]\s+(.+)$", l) for l in f) if m]
    if not 3 <= len(items) <= 5:
        out.append(v("G1-04", len(items), "3..5", file="insights.md"))
    for it in items:
        cited = set(re.findall(r"ref-\d{2}", it))
        if not cited & ids:
            out.append(v("G1-05", it[:60], "cites >=1 existing ref id", file="insights.md"))
    return out


def gate_g2(run, us, rules):
    out = []
    specs = spec_files(run)
    if not 2 <= len(specs) <= 3:
        out.append(v("G2-01", len(specs), "2..3", file="s2-spec/"))
    comps = set(rules["allowed"]["components"])
    has_2m = False
    for path in specs:
        fname = os.path.basename(path)
        text, sec = parse_spec(path)
        missing = [h for h in SPEC_HEADERS if h not in sec]
        if missing:
            out.append(v("G2-02", missing, SPEC_HEADERS, file=fname))
        nums = {int(n) for n in re.findall(r"#(\d+)", sec.get("유저스토리", {}).get("text", ""))}
        if nums != {us}:
            out.append(v("G2-03", sorted(nums), [us], file=fname))
        used = [item_name(i) for i in sec.get("컴포넌트", {}).get("items", [])]
        bad = [c for c in used if c not in comps]
        if bad:
            out.append(v("G2-04", bad, sorted(comps), file=fname))
        states = [item_name(i) for i in sec.get("상태", {}).get("items", [])]
        miss_states = [s for s in REQUIRED_STATES if s not in states]
        if miss_states:
            out.append(v("G2-05", states, REQUIRED_STATES, file=fname))
        if ("지도" in text or "경로" in text) and "위치 동의 전" not in states:
            out.append(v("SVC-01", states, "상태 contains '위치 동의 전'", file=fname))
        if "공유" in text and not any("출발·도착 구간 가림" in i for i in sec.get("섹션", {}).get("items", [])):
            out.append(v("SVC-02", sec.get("섹션", {}).get("items", []), "섹션 contains '출발·도착 구간 가림'", file=fname))
        if "2m" in text:
            has_2m = True
    if us == 2 and specs and not has_2m:
        out.append(v("SVC-04a", "no '2m' in specs", "some spec contains '2m'", file="s2-spec/"))
    return out


def check_frame_names(frames, us, run, rule_id, need_spec):
    out = []
    pat = re.compile(RULES_CACHE["allowed"]["frame_naming"]["pattern"])
    for fr in frames:
        m = pat.match(fr["name"])
        if not m or int(m.group("us")) != us:
            out.append(v(rule_id, fr["name"], "us%d-screen-NN[-warning]" % us, frame=fr["name"]))
            continue
        if need_spec:
            spec = os.path.join(run, STAGE_DIRS["S2"], "screen-%s.md" % m.group("nn"))
            if not os.path.isfile(spec):
                out.append(v(rule_id, fr["name"], "s2-spec/screen-%s.md exists" % m.group("nn"), frame=fr["name"]))
    return out


def gate_g3(run, us, rules):
    """(violations, approval) 를 돌려준다. approval은 없으면 None."""
    out = []
    pages = load_snapshot(run, "S3", ["01_Keyscreen"])
    frames = pages.get("01_Keyscreen", [])
    fw = rules["allowed"]["frame"]
    if not 2 <= len(frames) <= 3:
        out.append(v("G3-01", len(frames), "2..3"))
    for fr in frames:
        if fr["width"] != fw["width"] or fr["height"] != fw["height"]:
            out.append(v("G3-02", "%sx%s" % (fr["width"], fr["height"]), "390x844", frame=fr["name"]))
    out += check_frame_names(frames, us, run, "G3-04", need_spec=False)
    ap_path = os.path.join(run, STAGE_DIRS["S3"], "approval.json")
    approval = load_json(ap_path) if os.path.isfile(ap_path) else None
    if approval is not None and approval.get("us") != us:
        out.append(v("G3-03", approval.get("us"), us, file="approval.json"))
    return out, approval


def gate_g4(run, us, rules):
    out = []
    pages = load_snapshot(run, "S4", ["02_Tokens", "03_Components", "04_Screens"])
    allowed = rules["allowed"]
    colors = {norm_hex(x) for t in allowed["colors"].values() for x in t.values()}
    colors |= {norm_hex(x) for x in allowed["colors_extra"]}
    neutral = {norm_hex(x) for k, t in allowed["colors"].items() if k.startswith(NEUTRAL_PREFIXES) for x in t.values()}
    neutral |= {norm_hex(x) for x in allowed["colors_extra"]}
    svc05 = next(c for c in rules["gates"]["G4"]["checks"] if c["id"] == "SVC-05")
    critical = {norm_hex(x) for x in svc05["critical_hex"]}

    for page, frames in pages.items():
        for fr in frames:
            for n in fr["nodes"]:
                for h in n.get("fills", []):
                    if norm_hex(h) not in colors:
                        out.append(v("G4-01", h, "allowed.colors", frame=fr["name"], node_id=n["id"]))
                for key, rid, allow in (("radius", "G4-02", allowed["radius"]),
                                        ("fontSize", "G4-03", allowed["fontSize"]),
                                        ("fontWeight", "G4-04", allowed["fontWeight"]),
                                        ("gap", "G4-05", allowed["spacing"])):
                    if n.get(key) is not None and n[key] not in allow:
                        out.append(v(rid, n[key], "%s ∈ allowed" % key, frame=fr["name"], node_id=n["id"]))
                for p in n.get("padding") or []:
                    if p not in allowed["spacing"]:
                        out.append(v("G4-05", p, "padding ∈ allowed.spacing", frame=fr["name"], node_id=n["id"]))

    screens = pages.get("04_Screens", [])
    fw = allowed["frame"]
    for fr in screens:
        if fr["width"] != fw["width"] or fr["height"] != fw["height"]:
            out.append(v("G4-06", "%sx%s" % (fr["width"], fr["height"]), "390x844", frame=fr["name"]))
        brand_buttons = [n for n in fr["nodes"]
                         if "button" in (n.get("name") or "").lower()
                         and BRAND_HEX in {norm_hex(h) for h in n.get("fills", [])}]
        if len(brand_buttons) > 1:
            out.append(v("G4-07", len(brand_buttons), "<= 1", frame=fr["name"]))
    out += check_frame_names(screens, us, run, "G4-08", need_spec=True)

    pat = re.compile(allowed["frame_naming"]["pattern"])
    warnings = []
    for fr in screens:
        m = pat.match(fr["name"])
        if not m:
            continue
        spec = os.path.join(run, STAGE_DIRS["S2"], "screen-%s.md" % m.group("nn"))
        if os.path.isfile(spec) and "공유" in parse_spec(spec)[0]:
            if not any(n.get("name") == "RouteMask" for n in fr["nodes"]):
                out.append(v("SVC-03", "no RouteMask node", "node named RouteMask", frame=fr["name"]))
        if m.group("warning"):
            warnings.append(fr)
    if us == 2:
        if not any("2m" in (n.get("characters") or "") for fr in warnings for n in fr["nodes"] if n["type"] == "TEXT"):
            out.append(v("SVC-04b", "no TEXT '2m' in -warning frames", "warning frame TEXT contains '2m'"))
    for fr in warnings:
        for n in fr["nodes"]:
            for h in n.get("fills", []):
                hh = norm_hex(h)
                if hh not in neutral and hh not in critical:
                    out.append(v("SVC-05", h, "critical_hex (or neutral)", frame=fr["name"], node_id=n["id"]))

    # harness-goal.md 완료 기준: 04_Screens 프레임 2–3개
    if not 2 <= len(screens) <= 3:
        out.append(v("GOAL-01", len(screens), "04_Screens frames 2..3"))
    return out


# ---------------------------------------------------------------- state

def state_path(run):
    return os.path.join(run, "state.json")


def load_state(run):
    p = state_path(run)
    return load_json(p) if os.path.isfile(p) else None


def save_state(run, st):
    st["updated"] = now()
    with open(state_path(run), "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def init_run(run, us):
    for d in STAGE_DIRS.values():
        os.makedirs(os.path.join(run, d), exist_ok=True)
    os.makedirs(os.path.join(run, STAGE_DIRS["S1"], "refs"), exist_ok=True)
    st = load_state(run)
    if st is None:
        st = {"us": us, "stage": "S1", "retry": {}, "s4_retry": {}, "last_gate": None}
        save_state(run, st)
    return st


def apply_result(run, st, gate, result, violations, rules, approval=None):
    """게이트 결과를 state.json에 반영하고 다음 stage를 돌려준다."""
    on_fail = rules["gates"][gate].get("on_fail", {})
    if result == "pass":
        st["stage"] = NEXT_STAGE[gate]
        st.setdefault("retry", {}).pop(gate, None)
        if gate == "G4":
            st["s4_retry"] = {}
    elif result == "rejected":
        target = on_fail["rejected"][approval.get("reason_type", "design")]
        st["stage"] = target
        k = len([f for f in os.listdir(os.path.join(run, STAGE_DIRS["S3"])) if f.startswith("approval-rejected-")]) + 1
        os.rename(os.path.join(run, STAGE_DIRS["S3"], "approval.json"),
                  os.path.join(run, STAGE_DIRS["S3"], "approval-rejected-%d.json" % k))
    elif result == "fail":
        if gate in ("G1", "G2"):
            n = st.setdefault("retry", {}).get(gate, 0) + 1
            st["retry"][gate] = n
            st["stage"] = "blocked" if n > on_fail.get("max_retry", 2) else GATE_STAGE[gate]
        elif gate == "G4":
            counts = st.setdefault("s4_retry", {})
            for rid in sorted({x["rule_id"] for x in violations}):
                counts[rid] = counts.get(rid, 0) + 1
            limit = on_fail.get("max_retry_per_rule", 3)
            st["stage"] = "blocked" if any(c >= limit for c in counts.values()) else "S4"
        else:
            st["stage"] = GATE_STAGE[gate]
        if st["stage"] == "blocked":
            st["blocked_reason"] = "%s failed too many times" % gate
    st["last_gate"] = {"gate": gate, "result": result, "count": len(violations), "at": now()}
    save_state(run, st)
    return st["stage"]


# ---------------------------------------------------------------- main

RULES_CACHE = {}


def run_gate(root, us, gate, rules):
    RULES_CACHE.clear()
    RULES_CACHE.update(rules)
    run = os.path.join(root, "runs", "us%d" % us)
    if not os.path.isdir(run):
        raise InputError("runs/us%d not found (run init first)" % us)
    st = load_state(run)
    if st is not None and st["stage"] != GATE_STAGE[gate] and not (gate == "G4" and st["stage"] == "done"):
        raise InputError("state.stage is %s; %s runs only at %s" % (st["stage"], gate, GATE_STAGE[gate]))

    approval = None
    if gate == "G1":
        violations = gate_g1(run, us, rules)
    elif gate == "G2":
        violations = gate_g2(run, us, rules)
    elif gate == "G3":
        violations, approval = gate_g3(run, us, rules)
    else:
        violations = gate_g4(run, us, rules)

    if violations:
        result = "fail"
    elif gate == "G3" and approval is None:
        result = "waiting"
    elif gate == "G3" and approval.get("status") == "rejected":
        result = "rejected"
    elif gate == "G3" and approval.get("status") != "approved":
        violations = [v("G3-03", approval.get("status"), "approved", file="approval.json")]
        result = "fail"
    else:
        result = "pass"

    if gate == "G4":
        with open(os.path.join(run, STAGE_DIRS["S4"], "report.json"), "w", encoding="utf-8") as f:
            json.dump({"us": us, "count": len(violations), "violations": violations}, f, ensure_ascii=False, indent=2)

    next_stage = st["stage"] if st else None
    if st is not None and result != "waiting":
        next_stage = apply_result(run, st, gate, result, violations, rules, approval)
    return {"us": us, "gate": gate, "result": result, "count": len(violations),
            "violations": violations, "next_stage": next_stage}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("us")
    ap.add_argument("cmd", choices=["init", "status", "G1", "G2", "G3", "G4"])
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--rules", default=DEFAULT_RULES)
    a = ap.parse_args(argv)
    m = re.match(r"^us([1-6])$", a.us)
    if not m:
        print("us must be us1..us6", file=sys.stderr)
        return 2
    us = int(m.group(1))
    run = os.path.join(a.root, "runs", "us%d" % us)
    try:
        if a.cmd == "init":
            print(json.dumps(init_run(run, us), ensure_ascii=False, indent=2))
            return 0
        if a.cmd == "status":
            st = load_state(run)
            print(json.dumps(st, ensure_ascii=False, indent=2) if st else "no state for us%d" % us)
            return 0 if st else 2
        res = run_gate(a.root, us, a.cmd, load_json(a.rules))
    except InputError as e:
        print(json.dumps({"us": us, "gate": a.cmd, "result": "error", "error": str(e)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return {"pass": 0, "fail": 1, "rejected": 1, "waiting": 3}[res["result"]]


if __name__ == "__main__":
    sys.exit(main())
