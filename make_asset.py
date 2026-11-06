"""Turn burnbank.html (head-less page format) into a complete HTML document for the app's assets.
Drops any viewer-specific meta tag; nothing else changes."""
import pathlib, re

root = pathlib.Path(__file__).parent
src = (root / "burnbank.html").read_text()
src = re.sub(r'<meta name="[^"]*:[^"]*"[^>]*>\s*', "", src)
src = src.replace("<title>Burnbank</title>", "")
m = re.search(r"<style>.*?</style>", src, re.S)
style = m.group(0)
body = src[m.end():]
doc = ("<!doctype html>\n<html lang=\"en\">\n<head>\n"
       "<meta charset=\"utf-8\">\n"
       "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
       "<title>Burnbank</title>\n" + style + "\n</head>\n<body>" + body + "\n</body>\n</html>\n")
out = root / "android" / "assets" / "index.html"
out.write_text(doc)
print("wrote", out, len(doc), "bytes")
