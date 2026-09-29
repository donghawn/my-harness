#!/usr/bin/env python3
"""tests/fixtures/{check_id}/{pass,fail,fail-2}/ 생성기.

각 fixture = {meta.json: {us, gate}, runs/us{N}/...}. state.json은 넣지 않는다 (judge는 state 없이 판정만 한다).
기본 run(모든 게이트 통과)을 만들고, 체크마다 한 곳만 바꿔 실패 샘플을 만든다.

  python3 tests/make_fixtures.py
"""
import copy
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fixtures")
US = 2
PNG = b"\x89PNG\r\n\x1a\n"


def spec(purpose, sections, comps, states, extra=""):
    return "\n".join([
        "# 화면설계서", "", "## 목적", purpose, "", "## 유저스토리", "- #%d" % US, "",
        "## 섹션", *["- " + s for s in sections], "",
        "## 컴포넌트", *["- " + c for c in comps], "",
        "## 상태", *["- " + s for s in states], "", extra,
    ])


SPEC1 = spec("산책 중 지도에서 반려견과의 거리를 확인한다.",
             ["TopNavigation", "지도", "거리 표시 카드", "산책 종료 버튼"],
             ["TopNavigation", "ActionButton", "Badge"],
             ["기본", "빈 화면: 산책 기록 없음", "오류: 위치 수신 실패", "위치 동의 전: 동의 안내"])
SPEC2 = spec("리드줄이 2m를 넘으면 경고를 보여준다.",
             ["경고 배너", "현재 거리", "확인 버튼"],
             ["AlertDialog", "ActionButton"],
             ["기본", "빈 화면: 해당 없음", "오류: 에어태그 연결 끊김", "위치 동의 전: 동의 안내"])
SPEC_SHARE = spec("산책 코스를 친구에게 공유한다.",
                  ["코스 지도", "출발·도착 구간 가림", "공유 버튼"],
                  ["TopNavigation", "ActionButton"],
                  ["기본", "빈 화면: 코스 없음", "오류: 공유 실패", "위치 동의 전: 동의 안내"])


def node(id, type="FRAME", **kw):
    n = {"id": id, "type": type, "fills": kw.pop("fills", [])}
    n.update(kw)
    return n


def screen_frames():
    return [
        {"name": "us2-screen-01", "width": 390, "height": 844, "nodes": [
            node("1:1", fills=["#ffffff"]),
            node("1:2", name="TopNavigation", fills=["#ffffff"], padding=[0, 6]),
            node("1:3", "TEXT", characters="오늘의 산책", fontSize=18, fontWeight=700, fills=["#1a1c20"]),
            node("1:4", name="Card", fills=["#f7f8f9"], radius=16, padding=[16, 16], gap=8),
            node("1:5", "INSTANCE", name="Button/BrandSolid", fills=["#10ab7d"], radius=12, padding=[14, 20], gap=8),
            node("1:6", "TEXT", characters="산책 종료", fontSize=18, fontWeight=700, fills=["#ffffff"]),
        ]},
        {"name": "us2-screen-02-warning", "width": 390, "height": 844, "nodes": [
            node("2:1", fills=["#ffffff"]),
            node("2:2", name="WarningBanner", fills=["#fdf0f0"], radius=12, padding=[12, 16]),
            node("2:3", "TEXT", characters="리드줄이 2m를 넘었어요", fontSize=22, fontWeight=700, fills=["#fa342c"]),
            node("2:4", "TEXT", characters="반려견을 가까이 데려와 주세요", fontSize=16, fontWeight=400, fills=["#555d6d"]),
            node("2:5", "INSTANCE", name="Button/CriticalSolid", fills=["#fa342c"], radius=12, padding=[14, 20]),
        ]},
    ]


def base():
    refs = [{"id": "ref-%02d" % i, "url": "https://www.uibowl.io/screens/%d" % i,
             "app": "App%d" % i, "note": "메모 %d" % i} for i in range(1, 6)]
    f = {
        "s1-research/refs.json": refs,
        "s1-research/insights.md": "# 반영할 점\n- 거리 카드 상단 고정 (ref-01)\n- 경고는 전면 배너 (ref-02, ref-03)\n- CTA 하단 고정 (ref-04)\n",
        "s2-spec/screen-01.md": SPEC1,
        "s2-spec/screen-02.md": SPEC2,
        "s3-keyscreen/figma-snapshot.json": {"pages": [{"page": "01_Keyscreen", "frames": [
            {"name": "us2-screen-01", "width": 390, "height": 844, "nodes": []},
            {"name": "us2-screen-02-warning", "width": 390, "height": 844, "nodes": []}]}]},
        "s3-keyscreen/approval.json": {"us": US, "status": "approved", "reason": "", "reason_type": None, "date": "2026-09-30"},
        "s4-design/figma-snapshot.json": {"pages": [
            {"page": "02_Tokens", "frames": [{"name": "Colors", "width": 800, "height": 400, "nodes": [
                node("t:1", fills=["#10ab7d"]), node("t:2", fills=["#fa342c"]), node("t:3", fills=["#1a1c20"])]}]},
            {"page": "03_Components", "frames": [{"name": "ActionButton", "width": 400, "height": 200, "nodes": [
                node("c:1", "COMPONENT", name="Button/BrandSolid", fills=["#10ab7d"], radius=12, padding=[14, 20], gap=8)]}]},
            {"page": "04_Screens", "frames": screen_frames()},
        ]},
    }
    for i in range(1, 6):
        f["s1-research/refs/ref-%02d.png" % i] = PNG
    return f


def s4(f):
    return f["s4-design/figma-snapshot.json"]["pages"]


def screens(f):
    return next(p for p in s4(f) if p["page"] == "04_Screens")["frames"]


def s3frames(f):
    return f["s3-keyscreen/figma-snapshot.json"]["pages"][0]["frames"]


# ---- 변형 함수: f(files) -> None (in place)

def m_share_ok(f):
    f["s2-spec/screen-01.md"] = SPEC_SHARE
    screens(f)[0]["nodes"].append(node("1:9", name="RouteMask", fills=["#f3f4f5"]))


def set_(key, val):
    def m(f):
        f[key] = val
    return m


def g1_urls(f):
    f["s1-research/refs.json"][0]["url"] = "https://mobbin.com/screens/1"


def g1_png(f):
    del f["s1-research/refs/ref-01.png"]


def g1_cite(f):
    f["s1-research/insights.md"] += "- 근거 없는 항목\n"


def g2_one_spec(f):
    del f["s2-spec/screen-02.md"]


def g2_no_header(f):
    f["s2-spec/screen-02.md"] = SPEC2.replace("## 목적", "## 개요")


def g2_wrong_us(f):
    f["s2-spec/screen-02.md"] = SPEC2.replace("- #2", "- #3")


def g2_bad_comp(f):
    f["s2-spec/screen-02.md"] = SPEC2.replace("- AlertDialog", "- Modal")


def g2_no_state(f):
    f["s2-spec/screen-02.md"] = SPEC2.replace("- 빈 화면: 해당 없음\n", "")


def svc01_map(f):
    f["s2-spec/screen-01.md"] = SPEC1.replace("- 위치 동의 전: 동의 안내\n", "")


def svc01_route(f):
    f["s2-spec/screen-02.md"] = SPEC2.replace("현재 거리", "산책 경로").replace("- 위치 동의 전: 동의 안내\n", "")


def svc02_missing(f):
    f["s2-spec/screen-01.md"] = SPEC_SHARE.replace("- 출발·도착 구간 가림\n", "")


def svc02_partial(f):
    f["s2-spec/screen-01.md"] = SPEC_SHARE.replace("출발·도착 구간 가림", "출발 구간 가림")


def svc04a_none(f):
    f["s2-spec/screen-02.md"] = SPEC2.replace("2m", "일정 거리")


def svc04a_unit(f):
    f["s2-spec/screen-02.md"] = SPEC2.replace("2m", "2미터")


def g3_count(f):
    del s3frames(f)[1]


def g3_size(f):
    s3frames(f)[0]["width"] = 375


def g3_approval(f):
    f["s3-keyscreen/approval.json"]["us"] = 3


def g3_name(f):
    s3frames(f)[0]["name"] = "Keyscreen 1"


def g4_color(f):
    screens(f)[0]["nodes"][3]["fills"] = ["#ff6600"]


def g4_radius(f):
    screens(f)[0]["nodes"][3]["radius"] = 15


def g4_fsize(f):
    screens(f)[0]["nodes"][2]["fontSize"] = 17


def g4_fweight(f):
    screens(f)[0]["nodes"][2]["fontWeight"] = 600


def g4_spacing(f):
    screens(f)[0]["nodes"][3]["padding"] = [15, 16]


def g4_frame(f):
    screens(f)[0]["height"] = 812


def g4_two_brand(f):
    screens(f)[0]["nodes"].append(node("1:7", "INSTANCE", name="Button/BrandSolid 2", fills=["#10ab7d"], radius=12))


def g4_name(f):
    screens(f)[0]["name"] = "us2-screen-09"


def svc03_none(f):
    m_share_ok(f)
    screens(f)[0]["nodes"] = [n for n in screens(f)[0]["nodes"] if n.get("name") != "RouteMask"]


def svc03_other_frame(f):
    svc03_none(f)
    screens(f)[1]["nodes"].append(node("2:9", name="RouteMask", fills=["#f3f4f5"]))


def svc04b_text(f):
    screens(f)[1]["nodes"][2]["characters"] = "리드줄이 너무 길어요"


def svc04b_no_warning(f):
    screens(f)[1]["name"] = "us2-screen-02"


def svc05_brand(f):
    screens(f)[1]["nodes"][4]["fills"] = ["#10ab7d"]


def svc05_yellow(f):
    screens(f)[1]["nodes"][1]["fills"] = ["#fbdc65"]


CASES = {
    # id: (gate, pass_mutation or None, [fail mutations])
    "G1-01": ("G1", None, [set_("s1-research/refs.json", base()["s1-research/refs.json"][:4])]),
    "G1-02": ("G1", None, [g1_urls]),
    "G1-03": ("G1", None, [g1_png]),
    "G1-04": ("G1", None, [set_("s1-research/insights.md", "- 하나 (ref-01)\n- 둘 (ref-02)\n")]),
    "G1-05": ("G1", None, [g1_cite]),
    "G2-01": ("G2", None, [g2_one_spec]),
    "G2-02": ("G2", None, [g2_no_header]),
    "G2-03": ("G2", None, [g2_wrong_us]),
    "G2-04": ("G2", None, [g2_bad_comp]),
    "G2-05": ("G2", None, [g2_no_state]),
    "SVC-01": ("G2", None, [svc01_map, svc01_route]),
    "SVC-02": ("G2", m_share_ok, [svc02_missing, svc02_partial]),
    "SVC-04a": ("G2", None, [svc04a_none, svc04a_unit]),
    "G3-01": ("G3", None, [g3_count]),
    "G3-02": ("G3", None, [g3_size]),
    "G3-03": ("G3", None, [g3_approval]),
    "G3-04": ("G3", None, [g3_name]),
    "G4-01": ("G4", None, [g4_color]),
    "G4-02": ("G4", None, [g4_radius]),
    "G4-03": ("G4", None, [g4_fsize]),
    "G4-04": ("G4", None, [g4_fweight]),
    "G4-05": ("G4", None, [g4_spacing]),
    "G4-06": ("G4", None, [g4_frame]),
    "G4-07": ("G4", None, [g4_two_brand]),
    "G4-08": ("G4", None, [g4_name]),
    "SVC-03": ("G4", m_share_ok, [svc03_none, svc03_other_frame]),
    "SVC-04b": ("G4", None, [svc04b_text, svc04b_no_warning]),
    "SVC-05": ("G4", None, [svc05_brand, svc05_yellow]),
}

GATE_PREFIXES = {"G1": ("s1-research/",), "G2": ("s2-spec/",), "G3": ("s3-keyscreen/",),
                 "G4": ("s2-spec/", "s4-design/")}


def write(dirpath, gate, files):
    run = os.path.join(dirpath, "runs", "us%d" % US)
    for rel, content in files.items():
        if not rel.startswith(GATE_PREFIXES[gate]):
            continue
        p = os.path.join(run, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if isinstance(content, bytes):
            open(p, "wb").write(content)
        elif isinstance(content, str):
            open(p, "w", encoding="utf-8").write(content)
        else:
            json.dump(content, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for d in ("s1-research", "s2-spec", "s3-keyscreen", "s4-design"):
        os.makedirs(os.path.join(run, d), exist_ok=True)
    json.dump({"us": US, "gate": gate}, open(os.path.join(dirpath, "meta.json"), "w"), indent=2)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    n = 0
    for cid, (gate, pm, fails) in CASES.items():
        f = copy.deepcopy(base())
        if pm:
            pm(f)
        write(os.path.join(OUT, cid, "pass"), gate, f)
        n += 1
        for i, fm in enumerate(fails, 1):
            f = copy.deepcopy(base())
            fm(f)
            write(os.path.join(OUT, cid, "fail" if i == 1 else "fail-%d" % i), gate, f)
            n += 1
    print("wrote %d fixtures under %s" % (n, OUT))


if __name__ == "__main__":
    main()
