"""给候选框画编号后裁块，供人工直读命名；编号与坐标一一对应，杜绝手写坐标出错。"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

SRC = "../平江图高清/平江图_苏州网_增强锐化版_4414x7064.png"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def make(x0, y0, w, h, zoom, out, places):
    im = Image.open(SRC).convert("RGB")
    c = im.crop((x0, y0, x0 + w, y0 + h)).resize((int(w * zoom), int(h * zoom)), Image.LANCZOS)
    ov = Image.new("RGBA", c.size, (0, 0, 0, 0))
    dv = ImageDraw.Draw(ov)
    rows = []
    for gi, p in enumerate(places, 1):
        if not (x0 <= p["x"] <= x0 + w and y0 <= p["y"] <= y0 + h):
            continue
        bx = (p["x"] - p["w"] / 2 - x0) * zoom
        by = (p["y"] - p["h"] / 2 - y0) * zoom
        bw, bh = p["w"] * zoom, p["h"] * zoom
        dv.rectangle([bx - 1, by - 1, bx + bw + 1, by + bh + 1],
                     fill=(255, 210, 50, 30), outline=(210, 30, 50, 255), width=2)
        rows.append(["C%04d" % gi, round(p["x"], 1), round(p["y"], 1), bx, by, bw, bh])
    c = Image.alpha_composite(c.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(c)
    rows.sort(key=lambda r: (int(r[4] // 26), r[3]))
    for i, r in enumerate(rows, 1):
        r.append(i)
        bx, by, bw, bh = r[3], r[4], r[5], r[6]
        s = str(i)
        fs = 20 if bh >= 40 else 16
        f = ImageFont.truetype(FONT, fs)
        bb = d.textbbox((0, 0), s, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        if bw >= tw + 8 and bh >= th + 4:
            # 编号画在框内正中，杜绝与相邻标签混淆
            tx, ty = bx + bw / 2 - tw / 2, by + bh / 2 - th / 2 - bb[1]
            d.rectangle([tx - 3, ty + bb[1] - 1, tx + tw + 3, ty + bb[3] + 1], fill=(20, 20, 20))
            d.text((tx, ty), s, font=f, fill=(255, 240, 120))
        else:
            tx, ty = bx + bw + 2, by + bh / 2 - th / 2 - bb[1]
            d.rectangle([tx - 3, ty + bb[1] - 1, tx + tw + 3, ty + bb[3] + 1], fill=(255, 252, 240))
            d.text((tx, ty), s, font=f, fill=(190, 20, 40))
    c.save(out)
    json.dump({"region": [x0, y0, w, h, zoom], "items": rows},
              open(out.replace(".png", ".json"), "w"), ensure_ascii=False)
    print(out, "boxes:", len(rows))


if __name__ == "__main__":
    if "--all" in sys.argv:
        places = json.load(open("labels2.json"))
        places += [{"x": b[0], "y": b[1], "w": b[2], "h": b[3]} for b in json.load(open("vboxes.json"))]
    elif "--v" in sys.argv:
        places = [{"x": b[0], "y": b[1], "w": b[2], "h": b[3]} for b in json.load(open("vboxes.json"))]
    else:
        places = json.load(open("labels2.json"))
    x0, y0, w, h, zoom, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
    make(x0, y0, w, h, zoom, out, places)
