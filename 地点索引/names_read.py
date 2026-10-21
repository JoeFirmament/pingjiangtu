"""逐块直读结果 → 坐标锚定名称库（names.json）。块号见 tiles/index.json。"""
import json, os

# tile: {局部编号: 名称}
READ = {
 "n05": {3:"至德廟", 7:"張廣橋", 8:"紅橋"},
 "n06": {2:"西石塘橋", 4:"寺後橋", 5:"香花橋", 13:"章家橋", 15:"宮橋",
         22:"富家橋", 24:"榮利橋", 25:"祥符寺橋", 26:"艾家橋"},
 "n08": {24:"壽聖橋"},
 "n09": {3:"方廣橋", 13:"普濟橋", 14:"亭後橋", 18:"廣慧廟", 27:"聖王廟", 28:"同太保橋"},
 "n10": {13:"北倉橋", 1:"寺後橋", 12:"宮橋", 4:"天慶觀"},
 "n14": {8:"建善坊", 5:"真慶坊"},
}

SIMP = dict(zip(
 "橋門廟觀廣東華壽興慶雲龍鳳聖賢齊婁閶盤貴榮宮錢紅張靈館鄒廬廈濟後慧壇驛橋",
 "桥门庙观广东华寿兴庆云龙凤圣贤齐娄阊盘贵荣宫钱红张灵馆邹庐厦济后慧坛驿桥"))
EXTRA = {"鶿":"鹚","葑":"葑","讀":"读","瀆":"渎","蔣":"蒋","樂":"乐","飲":"饮","鶴":"鹤","麗":"丽",
         "寶":"宝","積":"积","嚴":"严","覺":"觉","報":"报","恩":"恩","師":"师","園":"园","墳":"坟",
         "顧":"顾","範":"范","莊":"庄","陸":"陆","陽":"阳","陰":"阴","潛":"潜","瀋":"沈"}
SIMP.update(EXTRA)


def simp(s):
    return "".join(SIMP.get(ch, ch) for ch in s)


def kind(n):
    if n.endswith("橋") or n.endswith("桥"):
        return "桥梁"
    if n.endswith("坊"):
        return "坊"
    if n.endswith("門") or n.endswith("门"):
        return "城门"
    if any(n.endswith(x) for x in "廟寺觀庵院祠宫"):
        return "寺观"
    return "其他"


names = json.load(open("names.json")) if os.path.exists("names.json") else []
have = {n["n"] for n in names}
added = 0
for tile, items in READ.items():
    d = json.load(open(f"tiles/{tile}.json"))
    for row in d["items"]:
        idx = row[-1]
        if idx not in items:
            continue
        nm = items[idx]
        if nm in have:
            continue
        names.append({"n": nm, "s": simp(nm), "t": kind(nm),
                      "x": row[1], "y": row[2], "src": tile + "#" + str(idx),
                      "note": f"图上注字直读（{tile} 块 #{idx}）· 待校"})
        have.add(nm)
        added += 1

for n in names:
    n.setdefault("s", simp(n["n"]))
    n.setdefault("t", kind(n["n"]))
json.dump(names, open("names.json", "w"), ensure_ascii=False, indent=1)
print("新增", added, "总计", len(names))
