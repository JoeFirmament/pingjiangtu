"""由干净框集 + 坐标锚定名称，生成最终页面。"""
import json, os, math, base64, datetime

# 版本号与构建时间：写进页面的「说明」里，方便对着一版说问题
VER = open("VERSION", encoding="utf-8").read().strip() if os.path.exists("VERSION") else "0.0.0"
BUILD = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

LAB = [dict(L, id="C%04d" % i) for i, L in enumerate(json.load(open("labels2.json")), 1)]
VLAB = [{"id":"V%04d" % i, "x":b[0], "y":b[1], "w":b[2], "h":b[3]} for i, b in enumerate(json.load(open("vboxes.json")), 1)]
LAB = LAB + VLAB
NAMES = json.load(open("names.json"))
T2S = json.load(open("t2s.json", encoding="utf-8")) if os.path.exists("t2s.json") else {}
def to_simp(n):
    return "".join(T2S.get(c, c) for c in (n or ""))

places = []
for L in LAB:
    places.append({"id":L["id"], "n":"", "t":"", "x":L["x"], "y":L["y"],
                   "w":L["w"], "h":L["h"], "note":"", "src":"auto"})

assigned, missed = 0, []
def boxdist(p, px, py):
    x0, y0 = p["x"]-p["w"]/2, p["y"]-p["h"]/2
    x1, y1 = p["x"]+p["w"]/2, p["y"]+p["h"]/2
    dx = max(x0-px, px-x1, 0); dy = max(y0-py, py-y1, 0)
    return math.hypot(dx, dy)

for e in NAMES:
    best, bd = None, 1e9
    for p in places:
        if p["n"]:
            continue
        d = min(boxdist(p, e["x"], e["y"]), math.hypot(p["x"]-e["x"], p["y"]-e["y"]) * 0.6)
        if d < bd:
            best, bd = p, d
    if best is not None and bd <= 65:
        best.update({"n":e["n"], "s":e.get("s", e["n"]), "t":e.get("t",""), "note":e.get("note",""), "src":"read"})
        assigned += 1
    else:
        places.append({"id":"M%03d" % (len(places)+1), "n":e["n"], "s":e.get("s", e["n"]),
                       "t":e.get("t",""), "x":e["x"], "y":e["y"], "note":e.get("note",""),
                       "src":"read", "w":0, "h":0})
        assigned += 1
        missed.append((e["n"], round(bd,1)))

IG = json.load(open("ig.json")) if os.path.exists("ig.json") else []
igged = 0
for p in places:
    for g in IG:
        if math.hypot(p["x"] - g["x"], p["y"] - g["y"]) <= 26:
            p["ig"] = 1
            igged += 1
            break

nn = sum(1 for p in places if p["n"])
json.dump({"v":2, "image":{"w":4414,"h":7064},
           "counts":{"named":nn, "auto":len(places)-nn}, "places":places},
          open("places.json","w"), ensure_ascii=False, indent=1)

tpl = open("app_template.html", encoding="utf-8").read()
slim = []
for p in places:
    o = {"id":p["id"],"n":p["n"],"t":p["t"],"x":p["x"],"y":p["y"],"src":p["src"]}
    if p.get("s"): o["s"] = p["s"]
    if p.get("note"): o["note"] = p["note"]
    if p.get("w"): o["w"] = p["w"]; o["h"] = p["h"]
    if p.get("ig"): o["ig"] = 1
    slim.append(o)
# 每个已命名点位补一份简体写法，搜索时繁简都能命中
for o in slim:
    if o.get("n"):
        o["s"] = to_simp(o["n"])
    else:
        o.pop("s", None)

html = tpl.replace("/*__DATA__*/[]", json.dumps(slim, ensure_ascii=False, separators=(",",":")))
html = html.replace("/*__T2S__*/{}", json.dumps(T2S, ensure_ascii=False, separators=(",",":")))
html = html.replace("__VERSION__", VER).replace("__BUILD__", BUILD)
# 构建产物里删掉「这是模板文件」的提示：CSS 块 + HTML div
import re as _re
html = _re.sub(r"/\*==TPLWARN-START==.*?/\*==TPLWARN-END== \*/\s*", "", html, flags=_re.S)
html = _re.sub(r"[ \t]*<!--\s*═══ 模板提示.*?-->\s*<div id=\"tplWarn\">.*?</div>\s*", "", html, flags=_re.S)

# 分块进度（页面左侧格子）：与 tiles.py 同一套网格
XS, YS, SZ = [900, 1600, 2300, 3000], [1300, 2000, 2700, 3400, 4100, 4800], 700
blocks = []
for by in YS:
    for bx in XS:
        n = sum(1 for p in places if p.get("w") and bx <= p["x"] < bx + SZ and by <= p["y"] < by + SZ)
        if n >= 3:
            blocks.append({"x": bx, "y": by, "n": n})
html = html.replace("/*__BLOCKS__*/[]", json.dumps(blocks, separators=(",", ":")))

out = "../平江图高清/平江图_地点数据库.html"
# 离线版：底图内嵌成 data URI —— 单文件，拷到哪、双击、丢进任何预览服务都能显示
MAPFULL = "../平江图在线/map/full.jpg"
_b64 = base64.b64encode(open(MAPFULL, "rb").read()).decode()
MAPURI = "data:image/jpeg;base64," + _b64
# 三档缩略图都指向同一份内嵌图：TIERS 会自动回落到 src，不再重复嵌三次
html_local = (html.replace("__MAPPREVIEW__", MAPURI)
                  .replace("__MAPMID__", "")
                  .replace("__MAPFULL__", "")
                  .replace("/*__CLOUD__*/null", "null"))
open(out, "w", encoding="utf-8").write(html_local)

# 线上版：中图内嵌（单文件单独打开也有底图，不依赖同级 map/ 目录）+ 原图外链按需升级
# 只把 mid 内嵌：2207px 在 0.55 默认视图下已是 1:1，约 2.5MB；full 仍放在 map/ 里，放大时才拉。
# 云端配置来自 workbuddy_cloud_service 的 publicConfig（endpoint 与发布域名一致）
CLOUD = {
    "endpoint": "https://pingjiang-map.app.workbuddy.host",
    "oauthRelayBaseUrl": "https://www.workbuddy.cn/v2/as/genie-baas/oauth",
    "publishableKey": "wbpk_9BZG7uwQvZB1jsXTux0EMB_4ChRTb0pfE0oXpjSxa9Rp54RW45ZGlOO",
}
os.makedirs("../平江图在线", exist_ok=True)
_b64mid = base64.b64encode(open("../平江图在线/map/mid.jpg", "rb").read()).decode()
MIDURI = "data:image/jpeg;base64," + _b64mid
html_web = (html.replace("__MAPPREVIEW__", MIDURI)
                .replace("__MAPMID__", "")
                .replace("__MAPFULL__", "map/full.jpg")
                .replace("/*__CLOUD__*/null", json.dumps(CLOUD, ensure_ascii=False)))
open("../平江图在线/index.html", "w", encoding="utf-8").write(html_web)
print("index.html %.2f MB（中图内嵌）" % (os.path.getsize("../平江图在线/index.html") / 1e6))
print(f"v{VER} · {BUILD}")
print(f"框 {len(places)} · 已命名 {nn} · 已弃 {igged} · 待命名 {len(places)-nn} · 落名 {assigned}/{len(NAMES)} · 块 {len(blocks)}")
if missed: print("未落位:", missed)
