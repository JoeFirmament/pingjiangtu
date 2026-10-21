"""按 700×700 网格切块，供逐块直读命名。"""
import json, subprocess, sys, os

XS = [900, 1600, 2300, 3000]
YS = [1300, 2000, 2700, 3400, 4100, 4800]
SIZE, ZOOM = 700, 1.7

L = json.load(open("labels2.json"))
index = {}
k = 0
for row, y in enumerate(YS):
    for col, x in enumerate(XS):
        n = sum(1 for p in L if x <= p["x"] < x+SIZE and y <= p["y"] < y+SIZE)
        if n < 3:
            continue
        k += 1
        name = f"n{k:02d}"
        index[name] = {"x": x, "y": y, "boxes": n}
        if not os.path.exists(f"tiles/{name}.json") or "--force" in sys.argv:
            subprocess.run([sys.executable, "annotate.py", str(x), str(y), str(SIZE), str(SIZE), str(ZOOM), f"tiles/{name}.png"],
                           check=True, capture_output=True)
json.dump(index, open("tiles/index.json", "w"), ensure_ascii=False, indent=1)
for name, d in index.items():
    print(name, d["x"], d["y"], d["boxes"])
print("块数", len(index), "框数", sum(d["boxes"] for d in index.values()))
