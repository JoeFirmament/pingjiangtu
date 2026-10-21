"""补充检测竖排标签：把二值图转置后跑同一套横向行检测，再转回原坐标。

平江图大量地名是竖排，前面只做了横排检测，所以漏掉接近一半标签。
转置后竖排变成横排，同一条管线即可复用。
"""
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import detect as D

SRC = "../平江图高清/平江图_苏州网_增强锐化版_4414x7064.png"


def detect_v(gray, long_kill=45):
    ink = (gray < 110).T                      # 关键：转置，竖排->横排
    h_open = ndi.binary_opening(ink, structure=np.ones((1, long_kill)))
    v_open = ndi.binary_opening(ink, structure=np.ones((long_kill, 1)))
    txt = ink & ~h_open & ~v_open
    txt = ndi.binary_closing(txt, structure=np.ones((3, 3)))
    txt = ndi.binary_opening(txt, structure=np.ones((2, 2)))
    lab, n = ndi.label(txt)
    boxes = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
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


def swap(b):
    """转置坐标 -> 原坐标：x<->y，w<->h"""
    return (b[1], b[0], b[3], b[2])


def iou(a, b):
    ax0, ay0, ax1, ay1 = a[0], a[1], a[0] + a[2], a[1] + a[3]
    bx0, by0, bx1, by1 = b[0], b[1], b[0] + b[2], b[1] + b[3]
    ix = max(0, min(ax1, bx1) - max(ax0, bx0))
    iy = max(0, min(ay1, by1) - max(ay0, by0))
    inter = ix * iy
    return inter / (a[2] * a[3] + b[2] * b[3] - inter + 1e-6)


if __name__ == "__main__":
    gray = np.array(Image.open(SRC).convert("L"))
    raw = detect_v(gray)
    print("raw v comps:", len(raw))
    lines = D.filter_glyphs(D.merge_lines(raw))
    print("v label lines:", len(lines))
    vbox = np.array([[l[0] + l[2] / 2, l[1] + l[3] / 2, l[2], l[3]] for l in lines])
    vbox = np.array([[c[1], c[0], c[3], c[2]] for c in vbox])   # 转回原坐标
    # 只保留城内
    vbox = vbox[(vbox[:, 0] > 520) & (vbox[:, 0] < 3450) & (vbox[:, 1] > 1180) & (vbox[:, 1] < 5900)]
    print("v in-city:", len(vbox))

    # 与已检出的横排框去重（同一标签被两路都抓到的情况）
    old = json.load(open("labels2.json"))
    obox = [(p["x"] - p["w"] / 2, p["y"] - p["h"] / 2, p["w"], p["h"]) for p in old]
    keep = []
    for v in vbox:
        r = (v[0] - v[2] / 2, v[1] - v[3] / 2, v[2], v[3])
        if any(iou(r, o) > 0.45 for o in obox):
            continue
        keep.append([round(float(v[0]), 1), round(float(v[1]), 1), round(float(v[2]), 1), round(float(v[3]), 1)])
    # 自身去重
    out = []
    for k in sorted(keep, key=lambda q: -q[2] * q[3]):
        r = (k[0] - k[2] / 2, k[1] - k[3] / 2, k[2], k[3])
        if any(iou(r, (o[0] - o[2] / 2, o[1] - o[3] / 2, o[2], o[3])) > 0.4 for o in out):
            continue
        out.append(k)
    out.sort(key=lambda q: (q[1], q[0]))
    json.dump(out, open("vboxes.json", "w"), ensure_ascii=False)
    print("vertical-only boxes:", len(out))
