"""把逐块直读得到的「块号→编号→名称」落到具体点位 ID 上。"""
import json

READ = {
 "b1": {1:("六通橋","桥梁"), 3:("張馬步橋","桥梁"), 6:("芝軍營橋","桥梁")},
 "b2": {4:("黃土塔橋","桥梁"), 6:("建盤橋","桥梁"), 11:("馬黃橋","桥梁"), 14:("利市橋","桥梁")},
 "b3": {1:("寺後橋","桥梁"), 3:("廣化寺","寺观"), 7:("傳化寺橋","桥梁"), 8:("天慶觀","寺观")},
 "b4": {6:("天心橋","桥梁")},
}

named = {}
for tile, items in READ.items():
    d = json.load(open(f"tiles/{tile}.json"))
    for row in d["items"]:
        idx = row[-1]
        if idx in items:
            n, t = items[idx]
            named[row[0]] = {"n": n, "t": t,
                             "note": f"编号框直读（{tile} #{idx}）· 位置经检测框校准，字迹待校"}
json.dump(named, open("named.json", "w"), ensure_ascii=False, indent=1)
print("named", len(named))
for k, v in named.items():
    print(k, v["n"])
