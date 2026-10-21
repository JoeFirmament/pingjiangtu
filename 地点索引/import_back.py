"""把页面导出的 JSON 回填进 names.json，然后重建页面。

用法：
    python import_back.py ~/Downloads/平江图_地点数据_2026-10-20.json

规则：
- 有名字的点 → 写回 names.json（按 40px 内最近的同名/同名点覆盖，否则新增）
- 标了「不是地名」(ig) 的点 → 写进 ig.json，以后重建不再当候选
- 用户自己新增的点 (src=manual) → 一并收进 names.json
运行后自动调用 build.py。
"""
import json, math, os, subprocess, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else None
if not SRC or not os.path.exists(SRC):
    sys.exit("请给出导出的 JSON 路径")

data = json.load(open(SRC, encoding="utf-8"))
arr = data["places"] if isinstance(data, dict) else data

names = json.load(open("names.json", encoding="utf-8")) if os.path.exists("names.json") else []
ig = json.load(open("ig.json", encoding="utf-8")) if os.path.exists("ig.json") else []


def near(lst, x, y, r=40):
    best, bd = None, 1e9
    for it in lst:
        d = math.hypot(it["x"] - x, it["y"] - y)
        if d < bd:
            best, bd = it, d
    return best if bd <= r else None


def simp(k):
    tbl = dict(zip("橋門廟觀廣東華壽興慶雲龍鳳聖賢齊婁閶盤貴榮宮錢紅張靈館鄒廬廈濟後慧壇驛書廳禪積陳陸陽陰寶嚴覺報師園墳顧範莊潛瀋",
                   "桥门庙观广东华寿兴庆云龙凤圣贤齐娄阊盘贵荣宫钱红张灵馆邹庐厦济后慧坛驿书厅禅积陈陆阳阴宝严觉报师园坟顾范庄潜沈"))
    return "".join(tbl.get(c, c) for c in k)


def kind(n):
    for suf, t in (("橋", "桥梁"), ("桥", "桥梁"), ("坊", "坊"), ("門", "城门"), ("门", "城门")):
        if n.endswith(suf):
            return t
    if any(n.endswith(x) for x in "廟寺觀庵院祠宫殿廳堂"):
        return "寺观"
    return "其他"


add_n, add_ig = 0, 0
for p in arr:
    x, y = round(float(p["x"])), round(float(p["y"]))
    n = (p.get("n") or "").strip()
    if p.get("ig") and not n:
        if not near(ig, x, y):
            ig.append({"x": x, "y": y})
            add_ig += 1
        continue
    if not n:
        continue
    hit = near(names, x, y)
    if hit:
        if hit["n"] != n:
            hit.update({"n": n, "s": simp(n), "t": kind(n)})
    else:
        names.append({"n": n, "s": simp(n), "t": kind(n), "x": x, "y": y,
                      "src": "user", "note": p.get("note", "") or "页面录入"})
        add_n += 1

json.dump(names, open("names.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(ig, open("ig.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"新增命名 {add_n} · 新增「不是地名」 {add_ig} · 名称库共 {len(names)} 条")
subprocess.run([sys.executable, "build.py"], check=True)
