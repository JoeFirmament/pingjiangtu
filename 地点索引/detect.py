"""平江图地名标签自动检测：找出图上所有文字标签的候选框（不识别字，只定位）。"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

SRC = "../平江图高清/平江图_苏州网_增强锐化版_4414x7064.png"

def detect(gray, long_kill=45):
    ink = gray < 110
    # 干掉长直线（街道/河道双线、城墙、图框），保留短笔画
    h_open = ndi.binary_opening(ink, structure=np.ones((1, long_kill)))
    v_open = ndi.binary_opening(ink, structure=np.ones((long_kill, 1)))
    txt = ink & ~h_open & ~v_open
    txt = ndi.binary_closing(txt, structure=np.ones((3, 3)))
    txt = ndi.binary_opening(txt, structure=np.ones((2, 2)))
    lab, n = ndi.label(txt)
    objs = ndi.find_objects(lab)
    boxes = []
    for i, sl in enumerate(objs, 1):
        if sl is None:
            continue
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if not (7 <= h <= 34 and 6 <= w <= 150):
            continue
        comp = lab[sl] == i
        area = int(comp.sum())
        fill = area / (h * w)
        if fill < 0.18 or fill > 0.92:
            continue
        boxes.append((sl[1].start, sl[0].start, w, h, area))
    return boxes

def merge_lines(boxes, gap_x=9, ov=0.55):
    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
    used = [False] * len(boxes)
    lines = []
    for i, b in enumerate(boxes):
        if used[i]:
            continue
        cur = list(b)
        used[i] = True
        changed = True
        while changed:
            changed = False
            for j, c in enumerate(boxes):
                if used[j]:
                    continue
                y0 = max(cur[1], c[1]); y1 = min(cur[1] + cur[3], c[1] + c[3])
                ovl = (y1 - y0) / min(cur[3], c[3])
                if ovl < ov:
                    continue
                cg = max(c[0] - (cur[0] + cur[2]), cur[0] - (c[0] + c[2]))
                if cg <= gap_x:
                    x0 = min(cur[0], c[0]); x1 = max(cur[0] + cur[2], c[0] + c[2])
                    y0n = min(cur[1], c[1]); y1n = max(cur[1] + cur[3], c[1] + c[3])
                    cur = [x0, y0n, x1 - x0, y1n - y0n]
                    used[j] = True
                    changed = True
        lines.append(cur)
    return lines

def filter_glyphs(lines):
    """要求 2-5 个等宽方字，剔除建筑栏杆/瓦楞"""
    out = []
    for x, y, w, h, *_ in lines:
        if not (12 <= h <= 26):
            continue
        k = w / h
        if not (1.5 <= k <= 6.2):
            continue
        g = max(2, round(k))          # 估计字数
        per = w / g
        if not (0.55 * h <= per <= 1.35 * h):
            continue
        out.append((x, y, w, h))
    return out


if __name__ == "__main__":
    gray = np.array(Image.open(SRC).convert("L"))
    b = detect(gray)
    print("raw comps:", len(b))
    lines = filter_glyphs(merge_lines(b))
    print("label lines:", len(lines))
    lm = np.array([[l[0] + l[2] / 2, l[1] + l[3] / 2, l[2], l[3]] for l in lines])
    np.save("labels_raw.npy", lm)
    im = Image.open(SRC).convert("RGB")
    d = ImageDraw.Draw(im)
    for x, y, w, h, *_ in lines:
        d.rectangle([x, y, x + w, y + h], outline=(220, 30, 40), width=2)
    im.crop((1750, 3050, 2650, 3950)).save("tiles/check_zic.png")
    im.resize((1100, 1760)).save("tiles/check_all.png")
