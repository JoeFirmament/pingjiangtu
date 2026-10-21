"""把字卡直读结果（reads.json）写进 names.json。

坐标直接取候选框中心 —— 不再有人眼估坐标，因此零偏移。
同名同地（<160px）视为重复检测，丢弃。
"""
import json, math, os

todo = json.load(open("sheets/todo.json"))
reads = json.load(open("reads.json"))
names = json.load(open("names.json")) if os.path.exists("names.json") else []


def simp(s):
    t = str.maketrans("橋門廟觀廣東華壽興慶雲龍鳳聖賢齊婁閶盤貴榮宮錢紅張靈館濟後慧禪書廳",
                      "桥门庙观广东华寿兴庆云龙凤圣贤齐娄阊盘贵荣宫钱红张灵馆济后慧禅书厅")
    return s.translate(t)


def kind(n):
    if n.endswith(("橋", "桥")):
        return "桥梁"
    if n.endswith("坊"):
        return "坊"
    if n.endswith(("門", "门")):
        return "城门"
    if n.endswith(("廟", "庙", "寺", "觀", "观", "庵", "菴", "院", "祠", "宮", "宫")):
        return "寺观"
    if n.endswith(("廳", "厅", "局", "倉", "仓", "場", "场", "館", "馆")):
        return "衙署"
    return "其他"


added, dup, skipped = [], [], 0
for k, nm in sorted(reads.items(), key=lambda kv: int(kv[0])):
    b = todo[int(k) - 1]
    x, y = b["x"], b["y"]
    hit = False
    for e in names:
        d = math.hypot(e["x"] - x, e["y"] - y)
        if e["n"] == nm and d < 200:
            hit = True
            break
        if d < 26:                      # 同一框已有别的名字
            hit = True
            break
    if hit:
        dup.append(nm)
        continue
    names.append({"n": nm, "s": simp(nm), "t": kind(nm), "x": x, "y": y})
    added.append(nm)

json.dump(names, open("names.json", "w"), ensure_ascii=False, indent=1)
print("新增", len(added), "重复", len(dup), "总计", len(names))
print("重复:", dup)
