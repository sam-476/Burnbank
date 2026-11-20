"""Screenshot the Progress tab (top, middle, bottom, and the empty setup state) in each theme with a seeded month,
and compose a preview sheet. Needs test_page.html (test_app.py writes it)."""
import json, pathlib, datetime as dt
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

root = pathlib.Path(__file__).parent
url = "file://" + str(root / "test_page.html")
out = root / "shots"; out.mkdir(exist_ok=True)
THEMES = [("dark", "Dark (default)"), ("white", "Simple white"), ("steam", "Steam")]

# A believable month: TDEE 2,600, eating 1,700-2,400, a few runs, two days skipped, protein on most days.
eats = [1900, 2100, 1750, 2300, 1850, 2000, 2400, 1800, 1950, 2200, 1700, 2050, 1900, 2150, 1800, 2250, 1950, 1850, 2000, 2350, 1750, 1900, 2100, 1800, 2000]
hist = []
d0 = dt.date(2026, 10, 26)
for i, eat in enumerate(eats):
    k = (d0 + dt.timedelta(days=i)).isoformat()
    if k in ("2026-11-01", "2026-11-08"): continue
    es = [{"id": "f" + k, "type": "food", "kcal": eat, "label": "Food", "time": "13:00", "p": 120 + (i * 7) % 60, "c": None, "f": None}]
    if i % 4 == 1: es.append({"id": "r" + k, "type": "burn", "kcal": 300, "label": "Run 30 min", "time": "18:00", "p": None, "c": None, "f": None})
    hist.append({"date": k, "tdee": 2600, "entries": es, "supp": {"vit": True, "other": False}})
seed = {"tdee": 2600, "unit": "kg", "goalKg": 5, "startDate": "2026-10-26", "todayKey": "2026-11-20",
        "today": {"entries": [], "supp": {"vit": False, "other": False}}, "history": hist, "favs": [], "recap": None,
        "notif": True, "theme": "dark", "adv": False, "moveSeen": True, "calc": None,
        "startWeight": {"date": "2026-10-26", "kg": 84.0},
        "weighIns": [{"date": "2026-10-30", "kg": 83.9}, {"date": "2026-11-03", "kg": 83.1}, {"date": "2026-11-07", "kg": 83.4},
                     {"date": "2026-11-11", "kg": 82.6}, {"date": "2026-11-15", "kg": 82.4}, {"date": "2026-11-19", "kg": 82.0}]}

with sync_playwright() as p:
    b = p.chromium.launch()
    for key, name in THEMES:
        ctx = b.new_context(viewport={"width": 390, "height": 760}, device_scale_factor=2, color_scheme="dark")
        pg = ctx.new_page()
        pg.clock.install(time="2026-11-20T10:00:00")
        pg.goto(url)
        s = dict(seed, theme=key)
        pg.evaluate("v => {localStorage.clear(); localStorage.setItem('burnbank.v2', v)}", json.dumps(s))
        pg.wait_for_function("localStorage.getItem('burnbank.v2') !== null")
        pg.reload(); pg.wait_for_timeout(400)
        pg.click("nav button[data-view=progress]"); pg.wait_for_timeout(150)
        pg.screenshot(path=str(out / f"{key}-progress1.png"))
        pg.evaluate("document.getElementById('p-acccard').scrollIntoView({block:'start'})"); pg.wait_for_timeout(150)
        pg.screenshot(path=str(out / f"{key}-progress2.png"))
        pg.evaluate("document.getElementById('view-progress').scrollTop=10000"); pg.wait_for_timeout(150)
        pg.screenshot(path=str(out / f"{key}-progress3.png"))
        # empty state
        e = dict(s, startWeight=None, weighIns=[])
        pg.evaluate("v => {localStorage.setItem('burnbank.v2', v)}", json.dumps(e))
        pg.wait_for_function("JSON.parse(localStorage.getItem('burnbank.v2')).startWeight === null")
        pg.reload(); pg.wait_for_timeout(400)
        pg.click("nav button[data-view=progress]"); pg.wait_for_timeout(150)
        pg.screenshot(path=str(out / f"{key}-progress0.png"))
        ctx.close()
    b.close()

W, H, pad, label_h = 780, 1520, 24, 56
pages = ["progress1", "progress2", "progress3", "progress0"]
img = Image.new("RGB", (pad + len(THEMES) * (W + pad), pad + len(pages) * (H + label_h + pad)), (238, 236, 230))
d = ImageDraw.Draw(img)
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
except Exception: font = ImageFont.load_default()
names = {"progress1": "Progress top", "progress2": "Middle", "progress3": "Bottom", "progress0": "First open"}
for r, page in enumerate(pages):
    for c, (key, name) in enumerate(THEMES):
        x = pad + c * (W + pad); y = pad + r * (H + label_h + pad)
        d.text((x, y + 8), f"{name} · {names[page]}", fill=(40, 40, 40), font=font)
        img.paste(Image.open(out / f"{key}-{page}.png").convert("RGB"), (x, y + label_h))
img.save(out / "themes-progress.png", optimize=True)
print("wrote themes-progress.png", img.size)
