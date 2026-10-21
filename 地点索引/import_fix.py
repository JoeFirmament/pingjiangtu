"""把页面「导出修正」得到的 JSON 回填进 names.json。

用法：
    python import_fix.py ~/Downloads/平江图_修正_2026-10-21.json

原理：修正记录带框 id（C0001 / V0123 / M004）。用上一次构建的 places.json
反查该框在库里原来的名字，再据此改写 names.json 中同名条目；原来没名字的
框则新增一条。这样即使页面上的名字被彻底改写，也不会写成重复条目。
"""
import json, json as J, math, os, subprocess, sys


def simp(s):
    t = str.maketrans(
        "橋門廟觀廣東華壽興慶雲龍鳳聖賢齊婁閶盤貴榮宮錢紅張靈館濟後慧禪書廳廳"
        "萬閣灣帶專諸鴨蝦蟆醋單義縣營軍齋果園波詔杉板頭條蘇臺娃豐鐘鐘樓門",
        "桥门庙观广东华寿兴庆云龙凤圣贤齐娄阊盘贵荣宫钱红张灵馆济后慧禅书厅厅"
        "万阁湾带专诸鸭虾蟆醋单义县营军斋果园波诏杉板头条苏台娃丰钟钟楼门")
    return s.translate(t)


def main(path):
    fix = J.load(open(path, encoding="utf-8"))
    recs = fix.get("places") if isinstance(fix, dict) else fix
    if not isinstance(recs, list):
        sys.exit("格式不符：需要 {'places':[...]}")

    places = J.load(open("places.json"))["places"]
    by_id = {p["id"]: p for p in places}
    names = J.load(open("names.json"))
    by_name = {e["n"]: e for e in names}

    upd, add, miss = [], [], []
    for r in recs:
        old = by_id.get(r.get("id"))
        nm = (r.get("n") or "").strip()
        if not nm:
            continue
        target = None
        if old and old.get("n"):
            target = by_name.get(old["n"])
        if target is None:                       # 库里没这条名字 → 新增
            target = {"n": nm}
            names.append(target)
            by_name[nm] = target
            add.append(nm)
        else:
            upd.append(f'{target["n"]}→{nm}' if target["n"] != nm else f'{nm}(位置)')
            target["n"] = nm
        target["s"] = simp(nm)
        target["x"] = r["x"]
        target["y"] = r["y"]
        if r.get("t"):
            target["t"] = r["t"]
        if r.get("note"):
            target["note"] = r["note"]
        target.setdefault("t", "")
        target.setdefault("note", "")

    # 去掉空类型/空备注，保持文件干净
    for e in names:
        if not e.get("t"):
            e["t"] = "其他"
        if not e.get("note"):
            e.pop("note", None)

    J.dump(names, open("names.json", "w"), ensure_ascii=False, indent=1)
    print(f"回填 {len(upd)} 条、新增 {len(add)} 条 → names.json 共 {len(names)} 条")
    if upd:
        print("修改:", "，".join(upd[:12]) + ("…" if len(upd) > 12 else ""))
    if add:
        print("新增:", "，".join(add[:12]) + ("…" if len(add) > 12 else ""))

    print("重新构建页面…")
    subprocess.run([sys.executable, "build.py"], check=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
