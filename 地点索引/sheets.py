"""把候选框裁成「字卡」，每张 15 个，逐个直读。

为什么不用大块：大块 700px 缩到显示宽 777，等效只有 1.1 倍，字太小。
字卡只裁框本体 + 边距，放到 4x 以上，等效 3 倍，字高约 42px，可读。
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

SRC = "../平江图高清/平江图_苏州网_增强锐化版_4414x7064.png"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

COLS, ROWS = 5, 3
CW, CH = 246, 330          # 每个格子
MARGIN = 16                 # 框外留多少像素看上下文
PAD = 6


def build(boxes, tag, start=1, per=COLS * ROWS):
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
            z = min(aw / crop.width, ah / crop.height)
            z = max(1.0, min(z, 9.0))
            crop = crop.resize((max(1, int(crop.width * z)), max(1, int(crop.height * z))), Image.LANCZOS)
            col, row = k % COLS, k // COLS
            cx0, cy0 = col * CW, row * CH
            canvas.paste(crop, (cx0 + PAD, cy0 + 30))
            # 标出检测框本体（蓝细线），便于判断检测是否偏移
            d.rectangle([cx0 + PAD + (x - w/2 - x0) * z, cy0 + 30 + (y - h/2 - y0) * z,
                         cx0 + PAD + (x + w/2 - x0) * z, cy0 + 30 + (y + h/2 - y0) * z],
                        outline=(40, 90, 200))
            # 编号
            idx = start + si + k
            d.rectangle([cx0 + PAD, cy0 + 2, cx0 + PAD + 46, cy0 + 26], fill=(20, 20, 20))
            d.text((cx0 + PAD + 6, cy0 + 3), str(idx), font=f, fill=(255, 240, 110))
            # 格子边框
            d.rectangle([cx0, cy0, cx0 + CW - 1, cy0 + CH - 1], outline=(210, 205, 190))
            items.append({"i": idx, "x": x, "y": y, "w": w, "h": h, "src": b["src"]})
        name = f"sheets/{tag}{len(sheets)+1:02d}"
        canvas.save(name + ".png")
        json.dump(items, open(name + ".json", "w"), ensure_ascii=False)
        sheets.append(name)
    return sheets


def load():
    H = json.load(open("labels2.json"))
    V = [{"x": b[0], "y": b[1], "w": b[2], "h": b[3], "src": "V"} for b in json.load(open("vboxes.json"))]
    for b in H:
        b["src"] = "H"
    return H + V


def done_sets():
    names = json.load(open("names.json")) if os.path.exists("names.json") else []
    ig = json.load(open("ig.json")) if os.path.exists("ig.json") else []
    return names, ig


def near(x, y, pts, r=26):
    for p in pts:
        if abs(p.get("x", 0) - x) <= r and abs(p.get("y", 0) - y) <= r:
            return True
    return False


if __name__ == "__main__":
    os.makedirs("sheets", exist_ok=True)
    box = load()
    names, ig = done_sets()
    todo = [b for b in box if not near(b["x"], b["y"], names) and not near(b["x"], b["y"], ig, 20)]
    # 按「像文字」的程度排序：边框墨水少 + 内部墨度中等 → 更可能是字
    import numpy as np
    A = np.array(Image.open(SRC).convert("L"))
    def score(b):
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        c = A[max(0, int(y - h/2)):int(y + h/2), max(0, int(x - w/2)):int(x + w/2)] < 128
        if c.size == 0:
            return 9, 0
        bd = np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]])
        return round(bd.mean(), 3), round(c.mean(), 3)
    sc = {id(b): score(b) for b in todo}
    todo = [b for b in todo if sc[id(b)][1] >= 0.28]
    todo.sort(key=lambda b: sc[id(b)][0])
    print("候选", len(box), "已命名", len(names), "已弃", len(ig), "待读", len(todo))
    sh = build(todo, "s")
    print("字卡", len(sh))
    json.dump(todo, open("sheets/todo.json", "w"), ensure_ascii=False)
