"""把第三轮字卡（sheets3）直读结果写进 names.json。

坐标直接取候选框中心 —— 零偏移。
"""
import json, math, os


def simp(s):
    t = str.maketrans("橋門廟觀廣東華壽興慶雲龍鳳聖賢齊婁閶盤貴榮宮錢紅張靈館濟後慧禪書廳萬閣灣帶專諸鴨蝦蟆醋單義縣營軍齋果園波詔杉板頭條",
                      "桥门庙观广东华寿兴庆云龙凤圣贤齐娄阊盘贵荣宫钱红张灵馆济后慧禅书厅万阁湾带专诸鸭虾蟆醋单义县营军斋果园波诏杉板头条")
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
    if n.endswith(("廳", "厅", "局", "倉", "仓", "場", "场", "館", "馆", "縣", "县")):
        return "衙署"
    return "其他"

READ = {
    "s01": {11: "法華院"},
    "s02": {23: "文殊院", 26: "單家橋", 27: "立義坊", 29: "東石塘橋"},
    "s03": {35: "周通橋"},
    "s04": {56: "高麗亭"},
    "s05": {62: "廟橋", 65: "垂雲館", 74: "澄清院", 75: "郭使橋"},
    "s06": {86: "安民橋", 88: "通濟橋"},
    "s07": {94: "長洲縣", 100: "南軍營橋"},
    "s08": {113: "縣東橋", 116: "清嘉坊"},
    "s10": {138: "保橋"},
    "s11": {154: "蝦蟆橋", 158: "醋坊橋"},
    "s12": {168: "鴨舍橋", 177: "永定寺"},
    "s13": {186: "烏盆橋"},
    "s14": {200: "閣橋", 204: "馬津橋", 205: "南橋"},
    "s16": {230: "萬壽院"},
    "s17": {241: "東齋", 246: "果子行", 251: "金母橋"},
    "s19": {278: "府院", 282: "明澤橋"},
    "s20": {289: "張澤坊", 291: "館娃坊", 299: "晉寧坊", 300: "和令坊"},
    "s21": {301: "天平山", 304: "披雲庵", 305: "通波坊", 308: "宣詔亭", 314: "杉板橋"},
    "s22": {318: "孔聖坊"},
    "s23": {345: "帶城橋"},
    "s25": {367: "船航橋"},
    "s26": {385: "專諸巷"},
    "s27": {391: "新橋"},
}

names = json.load(open("names.json"))
todo = json.load(open("sheets3/todo.json"))
added, dup = [], []
for sh, items in READ.items():
    for gidx, nm in items.items():
        b = todo[gidx - 1]
        x, y = b["x"], b["y"]
        hit = False
        for e in names:
            d = math.hypot(e["x"] - x, e["y"] - y)
            if (e["n"] == nm and d < 200) or d < 26:
                hit = True
                break
        if hit:
            dup.append(f"#{gidx} {nm}")
            continue
        names.append({"n": nm, "s": simp(nm), "t": kind(nm), "x": x, "y": y})
        added.append(nm)

json.dump(names, open("names.json", "w"), ensure_ascii=False, indent=1)
print("新增", len(added), "重复", len(dup), "总计", len(names))
print("新增:", added)
if dup:
    print("重复:", dup)
