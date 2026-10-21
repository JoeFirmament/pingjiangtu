"""合并被拆开的同一标签框，剔除碎屑，重出干净框集。"""
import json, math

L = json.load(open("labels.json"))

def box(p): return (p["x"]-p["w"]/2, p["y"]-p["h"]/2, p["x"]+p["w"]/2, p["y"]+p["h"]/2)

items = [dict(p) for p in L]
changed = True
rounds = 0
while changed and rounds < 4:
    changed = False
    rounds += 1
    out = []
    used = [False]*len(items)
    for i, a in enumerate(items):
        if used[i]:
            continue
        ax0, ay0, ax1, ay1 = box(a)
        for j in range(i+1, len(items)):
            if used[j]:
                continue
            b = items[j]
            bx0, by0, bx1, by1 = box(b)
            oy = min(ay1, by1) - max(ay0, by0)
            if oy < 0.62 * min(ay1-ay0, by1-by0):
                continue
            gap = max(bx0 - ax1, ax0 - bx1)
            if gap > 9 or gap < -0.35 * min(ax1-ax0, bx1-bx0):
                continue
            nx0, ny0 = min(ax0, bx0), min(ay0, by0)
            nx1, ny1 = max(ax1, bx1), max(ay1, by1)
            a = {"x": round((nx0+nx1)/2, 1), "y": round((ny0+ny1)/2, 1),
                 "w": round(nx1-nx0, 1), "h": round(ny1-ny0, 1)}
            ax0, ay0, ax1, ay1 = nx0, ny0, nx1, ny1
            used[j] = True
            changed = True
        out.append(a)
        used[i] = True
    items = out

items = [p for p in items if p["w"] >= 26 and 11 <= p["h"] <= 30]
items.sort(key=lambda p: (p["y"], p["x"]))
json.dump(items, open("labels2.json", "w"), ensure_ascii=False)
print("合并后框数:", len(items))
