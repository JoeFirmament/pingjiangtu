"""按 700×700 网格切「竖排标签」块，块号 v01… 与横排 n01… 分开，便于逐块直读。"""
import json, os, subprocess, sys

XS = [900, 1600, 2300, 3000]
YS = [1300, 2000, 2700, 3400, 4100, 4800]
SIZE, ZOOM = 700, 1.7

V = [{"x": b[0], "y": b[1], "w": b[2], "h": b[3]} for b in json.load(open("vboxes.json"))]
index = {}
k = 0
for y in YS:
    for x in XS:
        n = sum(1 for p in V if x <= p["x"] < x + SIZE and y <= p["y"] < y + SIZE)
        if n < 3:
            continue
        k += 1
        name = f"v{k:02d}"
        index[name] = {"x": x, "y": y, "boxes": n}
        if not os.path.exists(f"tiles/{name}.json") or "--force" in sys.argv:
            subprocess.run([sys.executable, "annotate.py", str(x), str(y), str(SIZE), str(SIZE),
                            str(ZOOM), f"tiles/{name}.png", "--v"], check=True, capture_output=True)
json.dump(index, open("tiles/index_v.json", "w"), ensure_ascii=False, indent=1)
for name, d in index.items():
    print(name, d["x"], d["y"], d["boxes"])
print("竖排块数", len(index), "框数", sum(d["boxes"] for d in index.values()))
