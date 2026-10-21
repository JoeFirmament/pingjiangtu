"""第三轮直读结果：按 (名称, x, y) 直接追加进 names.json。

坐标取自「框中心」或「按 300px 读数块换算的标签中心」，误差 ~±8px，
build.py 会吸附到最近的候选框，吸附不到就单独建点。
"""
import json, os

SIMP = dict(zip(
 "橋門廟觀廣東華壽興慶雲龍鳳聖賢齊婁閶盤貴榮宮錢紅張靈館鄒廬廈濟後慧壇驛書廳禪"
 "積陳陸陽陰寶嚴覺報師園墳顧範莊潛瀋",
 "桥门庙观广东华寿兴庆云龙凤圣贤齐娄阊盘贵荣宫钱红张灵馆邹庐厦济后慧坛驿书厅禅"
 "积陈陆阳阴宝严觉报师园坟顾范庄潜沈"))

EXTRA = {"鶿":"鹚","葑":"葑","讀":"读","瀆":"渎","蔣":"蒋","樂":"乐","飲":"饮","鶴":"鹤","麗":"丽"}
SIMP.update(EXTRA)


def simp(s):
    return "".join(SIMP.get(ch, ch) for ch in s)


def kind(n):
    if n.endswith(("橋", "桥")):
        return "桥梁"
    if n.endswith("坊"):
        return "坊"
    if n.endswith(("門", "门")):
        return "城门"
    if any(n.endswith(x) for x in "廟寺觀庵院祠宫殿廳堂"):
        return "寺观"
    return "其他"


# (名称, x, y)  —— 直读自 600px 读数块，块号见 names2 注释
NEW = [
    # c1 (1780,2760) / t1 (1650,2700)：报恩寺—普济桥一带
    ("香積寺橋", 1967, 2776),
    ("張思橋", 1780, 2784),
    ("寺西橋", 1784, 2961),
    ("廣通廟", 1987, 2939),
    ("主簿廳", 1957, 3049),
    # c2 (1780,3060)：吴殿—丁家桥一带
    ("東四橋", 1822, 3177),
    ("丁家橋", 1837, 3292),
    ("靈王廟", 1992, 3147),
    # c5 (1480,2760)：郎家桥—席家桥
    ("郎家橋", 1582, 2857),
    ("沈家橋", 1707, 2867),
    ("席家橋", 1719, 2965),
    # c6 (1480,3060)：朱明寺桥—广书桥
    ("朱明寺橋", 1580, 3107),
    ("廣書橋", 1719, 3090),
    # v03 (2300,1300)：城东北角 洋澳桥、华家桥、北禅寺
    ("洋澳橋", 2932, 1658),
    ("華家橋", 2938, 1954),
    ("北禪寺", 2744, 1730),
]

names = json.load(open("names.json")) if os.path.exists("names.json") else []
have = {n["n"] for n in names}
added = 0
for nm, x, y in NEW:
    if nm in have:
        continue
    names.append({"n": nm, "s": simp(nm), "t": kind(nm), "x": x, "y": y,
                  "src": "read3", "note": "图上注字直读 · 待校"})
    have.add(nm)
    added += 1
json.dump(names, open("names.json", "w"), ensure_ascii=False, indent=1)
print("新增", added, "总计", len(names))
