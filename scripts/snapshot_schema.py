"""figma-snapshot.json 스키마 확인.

judge.py가 G3·G4 판정 전에 호출한다. 덤프 형식 오류를 디자인 위반으로 오판하지 않기 위해
형식이 틀리면 판정 대신 error로 돌려준다.

스키마 (harness/artifacts.md):
{
  "pages": [
    {"page": "04_Screens",
     "frames": [{"name", "width", "height",
                 "nodes": [{"id", "type", "name"?, "characters"?, "fills": [hex],
                            "radius"?, "fontSize"?, "fontWeight"?, "padding"?: [n], "gap"?}]}]}
  ]
}
"""
import json
import re
import sys

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")
NUM = (int, float)


def _is_num(v):
    return isinstance(v, NUM) and not isinstance(v, bool)


def validate(snapshot, allowed_pages):
    """오류 문자열 목록을 돌려준다. 빈 목록이면 통과."""
    errors = []
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("pages"), list):
        return ["root must be an object with a 'pages' list"]
    for pi, page in enumerate(snapshot["pages"]):
        where = "pages[%d]" % pi
        if not isinstance(page, dict):
            errors.append("%s must be an object" % where)
            continue
        name = page.get("page")
        if name not in allowed_pages:
            errors.append("%s.page %r not in allowed pages %s" % (where, name, sorted(allowed_pages)))
        frames = page.get("frames")
        if not isinstance(frames, list):
            errors.append("%s.frames must be a list" % where)
            continue
        for fi, frame in enumerate(frames):
            fw = "%s.frames[%d]" % (where, fi)
            if not isinstance(frame, dict):
                errors.append("%s must be an object" % fw)
                continue
            if not isinstance(frame.get("name"), str):
                errors.append("%s.name must be a string" % fw)
            for k in ("width", "height"):
                if not _is_num(frame.get(k)):
                    errors.append("%s.%s must be a number" % (fw, k))
            nodes = frame.get("nodes")
            if not isinstance(nodes, list):
                errors.append("%s.nodes must be a list" % fw)
                continue
            for ni, node in enumerate(nodes):
                nw = "%s.nodes[%d]" % (fw, ni)
                if not isinstance(node, dict):
                    errors.append("%s must be an object" % nw)
                    continue
                for k in ("id", "type"):
                    if not isinstance(node.get(k), str):
                        errors.append("%s.%s must be a string" % (nw, k))
                fills = node.get("fills", [])
                if not isinstance(fills, list) or not all(isinstance(f, str) and HEX_RE.match(f) for f in fills):
                    errors.append("%s.fills must be a list of #RRGGBB[AA]" % nw)
                for k in ("radius", "fontSize", "fontWeight", "gap"):
                    if node.get(k) is not None and not _is_num(node[k]):
                        errors.append("%s.%s must be a number" % (nw, k))
                pad = node.get("padding")
                if pad is not None and (not isinstance(pad, list) or not all(_is_num(p) for p in pad)):
                    errors.append("%s.padding must be a list of numbers" % nw)
                for k in ("name", "characters"):
                    if node.get(k) is not None and not isinstance(node[k], str):
                        errors.append("%s.%s must be a string" % (nw, k))
    return errors


def main():
    if len(sys.argv) < 3:
        print("usage: snapshot_schema.py <snapshot.json> <page> [<page> ...]", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        errors = validate(json.load(f), set(sys.argv[2:]))
    print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
