"""Screenshot Today / Macros / Goal / Menu (picker open) and the TDEE calculator form in each theme with sample data,
and compose preview sheets. Needs test_page.html (test_app.py writes it)."""
import pathlib
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

root = pathlib.Path(__file__).parent
url = "file://" + str(root / "test_page.html")
out = root / "shots"; out.mkdir(exist_ok=True)
THEMES = [("dark", "Dark (default)"), ("white", "Simple white"), ("steam", "Steam")]

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 760}, device_scale_factor=2, color_scheme="dark")
    pg = ctx.new_page()
    pg.clock.install(time="2026-10-26T14:30:00")
    pg.goto(url); pg.wait_for_timeout(300)
    pg.click("#btn-move-no")
    pg.fill("#in-kcal", "650"); pg.fill("#in-label", "Lunch"); pg.click("#btn-add")
    pg.click("#seg-burn"); pg.click("#t-presets .chip >> text=Run"); pg.fill("#in-min", "30"); pg.check("#in-fav"); pg.click("#btn-add")
    pg.clock.set_fixed_time("2026-10-27T00:00:05"); pg.wait_for_timeout(1500); pg.click("#r-ok")
    pg.clock.set_fixed_time("2026-10-27T13:40:00"); pg.wait_for_timeout(1200)
    pg.click("#seg-food"); pg.check("#in-adv")
    pg.fill("#in-kcal", "420"); pg.fill("#in-label", "Eggs and toast"); pg.fill("#in-p", "28"); pg.fill("#in-c", "34"); pg.fill("#in-f", "18"); pg.click("#btn-add")
    pg.fill("#in-kcal", "560"); pg.fill("#in-label", "Chicken rice"); pg.fill("#in-p", "46"); pg.check("#in-fav"); pg.click("#btn-add")
    pg.click("nav button[data-view=goal]"); pg.fill("#in-goal", "3"); pg.click("#f-goal button[type=submit]")
    pg.click("nav button[data-view=macros]"); pg.check("#in-vit")
    pg.click("nav button[data-view=menu]"); pg.wait_for_timeout(2600)
    for key, name in THEMES:
        pg.click("nav button[data-view=menu]"); pg.wait_for_timeout(100)
        if pg.locator("#m-themes").is_hidden(): pg.click("#btn-themes")
        pg.click(f"#m-themes button[data-skin={key}]"); pg.wait_for_timeout(2500)
        pg.screenshot(path=str(out / f"{key}-menu.png"))
        # the calculator form, filled in, scrolled into view
        pg.click("#btn-themes")
        if pg.locator("#f-calc").is_hidden(): pg.click("#btn-calc")
        pg.click("#cs-m"); pg.fill("#in-age", "28"); pg.fill("#in-height", "178"); pg.fill("#in-weight", "80"); pg.select_option("#in-act", "2")
        pg.evaluate("document.getElementById('f-calc').scrollIntoView({block:'center'})"); pg.wait_for_timeout(150)
        pg.screenshot(path=str(out / f"{key}-calc.png"))
        pg.click("#btn-calc")
        pg.click("nav button[data-view=today]"); pg.wait_for_timeout(100)
        pg.screenshot(path=str(out / f"{key}-today.png"))
        pg.click("nav button[data-view=macros]"); pg.wait_for_timeout(100)
        pg.screenshot(path=str(out / f"{key}-macros.png"))
        pg.click("nav button[data-view=goal]"); pg.wait_for_timeout(100)
        pg.evaluate("document.getElementById('view-goal').scrollTop=10000"); pg.wait_for_timeout(100)
        pg.screenshot(path=str(out / f"{key}-goal.png"))
    # the hold in progress, Dark theme
    pg.click("nav button[data-view=menu]"); pg.click("#btn-themes"); pg.click("#m-themes button[data-skin=dark]"); pg.wait_for_timeout(2500)
    pg.click("nav button[data-view=today]"); pg.wait_for_timeout(100)
    box = pg.locator("#t-favs .chip >> nth=0").bounding_box()
    pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2); pg.mouse.down(); pg.wait_for_timeout(450)
    pg.screenshot(path=str(out / "dark-holding.png")); pg.mouse.up()
    b.close()

def sheet(pages, fname):
    W, H = 780, 1520
    pad, label_h = 24, 56
    cols = len(THEMES); rows = len(pages)
    img = Image.new("RGB", (pad + cols * (W + pad), pad + rows * (H + label_h + pad)), (238, 236, 230))
    d = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except Exception: font = ImageFont.load_default()
    for r, page in enumerate(pages):
        for c, (key, name) in enumerate(THEMES):
            x = pad + c * (W + pad); y = pad + r * (H + label_h + pad)
            d.text((x, y + 8), f"{name} · {page.capitalize()}", fill=(40, 40, 40), font=font)
            im = Image.open(out / f"{key}-{page}.png").convert("RGB")
            img.paste(im, (x, y + label_h))
    img.save(out / fname, optimize=True)
    print("wrote", fname, img.size)

sheet(["today", "menu"], "themes-today-menu.png")
sheet(["macros", "goal"], "themes-macros-goal.png")
sheet(["calc"], "themes-calc.png")
