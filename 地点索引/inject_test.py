"""把 test3.js 注入当前构建产物，生成自测页。"""
import sys
html = open("../平江图高清/平江图_地点数据库.html", encoding="utf-8").read()
js = open(sys.argv[1] if len(sys.argv) > 1 else "test3.js", encoding="utf-8").read()
out = "../平江图高清/_t3.html"
open(out, "w", encoding="utf-8").write(html.replace("</body>", "<script>\n" + js + "\n</script></body>"))
print("wrote", out, len(html))
