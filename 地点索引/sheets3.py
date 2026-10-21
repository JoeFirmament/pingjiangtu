"""第二轮字卡：只取「墨度像字、边框半干净」这一带，按边框升序。

上一轮已清掉最干净的一批（边框<0.30），本轮针对被建筑线条擦边的标签。
输出到 sheets2/，编号从 1 开始，配 sheets2/todo.json。
"""
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = "../平江图高清/平江图_苏州网_增强锐化版_4414x7064.png"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
OUT = "sheets3"
COLS, ROWS = 5, 3
CW, CH = 246, 330
MARGIN = 16
PAD = 6


def build(boxes, tag="s", per=COLS * ROWS):
    im = Image.open(SRC).convert("L")
    sheets = []
    for si in range(0, len(boxes), per):
        chunk = boxes[si:si + per]
        canvas = Image.new("RGB", (COLS * CW, ROWS * CH), (255, 255, 255))
        d = ImageDraw.Draw(canvas)
        f = ImageFont.truetype(FONT, 26)
        items = []
        for k, b in enumerate(chunk):
            x, y, w, h = b["x"], b["y"], b["w"], b["h"]
            x0 = max(0, int(x - w / 2 - MARGIN)); x1 = min(im.width, int(x + w / 2 + MARGIN))
            y0 = max(0, int(y - h / 2 - MARGIN)); y1 = min(im.height, int(y + h / 2 + MARGIN))
            crop = im.crop((x0, y0, x1, y1))
            aw, ah = CW - PAD * 2, CH - PAD * 2 - 30
            z = max(1.0, min(min(aw / crop.width, ah / crop.height), 9.0))
            crop = crop.resize((max(1, int(crop.width * z)), max(1, int(crop.height * z))), Image.LANCZOS)
            cx0, cy0 = (k % COLS) * CW, (k // COLS) * CH
            canvas.paste(crop, (cx0 + PAD, cy0 + 30))
            d.rectangle([cx0 + PAD + (x - w / 2 - x0) * z, cy0 + 30 + (y - h / 2 - y0) * z,
                         cx0 + PAD + (x + w / 2 - x0) * z, cy0 + 30 + (y + h / 2 - y0) * z],
                        outline=(40, 90, 200))
            idx = 1 + si + k
            d.rectangle([cx0 + PAD, cy0 + 2, cx0 + PAD + 46, cy0 + 26], fill=(20, 20, 20))
            d.text((cx0 + PAD + 6, cy0 + 3), str(idx), font=f, fill=(255, 240, 110))
            d.rectangle([cx0, cy0, cx0 + CW - 1, cy0 + CH - 1], outline=(210, 205, 190))
            items.append({"i": idx, "x": x, "y": y, "w": w, "h": h, "src": b["src"]})
        name = f"{OUT}/{tag}{len(sheets)+1:02d}"
        canvas.save(name + ".png")
        json.dump(items, open(name + ".json", "w"), ensure_ascii=False)
        sheets.append(name)
    return sheets


def near(x, y, pts, r):
    return any(abs(p.get("x", 0) - x) <= r and abs(p.get("y", 0) - y) <= r for p in pts)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    H = json.load(open("labels2.json"))
    V = [{"x": b[0], "y": b[1], "w": b[2], "h": b[3], "src": "V"} for b in json.load(open("vboxes.json"))]
    for b in H:
        b["src"] = "H"
    box = H + V
    names = json.load(open("names.json"))
    ig = json.load(open("ig.json")) if os.path.exists("ig.json") else []
    todo = [b for b in box if not near(b["x"], b["y"], names, 26) and not near(b["x"], b["y"], ig, 20)]

    A = np.array(Image.open(SRC).convert("L"))

    def feat(b):
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        c = A[max(0, int(y - h / 2)):int(y + h / 2), max(0, int(x - w / 2)):int(x + w / 2)] < 128
        if c.size == 0:
            return 9, 0
        bd = np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]])
        return round(bd.mean(), 3), round(c.mean(), 3)

    def aspect(b):
        w, h = b["w"], b["h"]
        return max(w, h) / max(1, min(w, h))
    # 平江图标签是 2–4 个等大的方块字，字高 14–18px：竖排 1.7–4.2，横排 2–5
    vert = [b for b in todo if b["h"] >= b["w"] and 1.7 <= aspect(b) <= 4.2 and 14 <= b["w"] <= 34 and 30 <= b["h"] <= 90]
    horz = [b for b in todo if b["w"] > b["h"] and 2.0 <= aspect(b) <= 5.0 and 12 <= b["h"] <= 26 and 40 <= b["w"] <= 110]
    sc = {id(b): feat(b) for b in todo}
    vert = [b for b in vert if sc[id(b)][1] >= 0.26]
    horz = [b for b in horz if sc[id(b)][1] >= 0.26]
    todo = vert + horz
    todo.sort(key=lambda b: (round(b["y"] / 80), b["x"]))
    print("候选", len(box), "已命名", len(names), "本轮待读", len(todo))
    sh = build(todo)
    print("字卡", len(sh))
    json.dump(todo, open(f"{OUT}/todo.json", "w"), ensure_ascii=False)
