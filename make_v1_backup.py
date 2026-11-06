"""Produce a real v1 backup by driving the shipped v1 page, so v2's restore is tested against the genuine format.
Needs v1/burnbank-v1.html (the v1 app, kept in the project docs as burnbank-v1-source.html). The output, v1_backup.json,
is checked in beside this script, so you only need to run it if you change the scenario."""
import json, pathlib
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).parent
src = (root / "v1" / "burnbank-v1.html").read_text()
page_html = ("<!doctype html><html><head><meta charset='utf-8'>"
             "<meta name='viewport' content='width=device-width,initial-scale=1,viewport-fit=cover'></head><body>"
             + src + "</body></html>")
(root / "v1" / "test_page_v1.html").write_text(page_html)
url = "file://" + str(root / "v1" / "test_page_v1.html")

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 800})
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.clock.install(time="2026-10-26T14:30:00")
    pg.goto(url); pg.wait_for_timeout(300)
    # Monday 26 Oct: lunch 600 (edited to 700), football 20 min saved as favourite
    pg.fill("#in-kcal", "600"); pg.fill("#in-label", "Lunch"); pg.click("#btn-add")
    pg.click("#seg-burn"); pg.click("#t-presets .chip >> text=Football"); pg.fill("#in-min", "20")
    pg.check("#in-fav"); pg.click("#btn-add")
    pg.click("#t-list li:has-text('Lunch')"); pg.fill("#e-kcal", "700"); pg.click("#e-save")
    # midnight -> Tuesday 27 Oct, recap dismissed, 400 backdated to Monday, goal 1 kg, breakfast pending today
    pg.clock.set_fixed_time("2026-10-27T00:00:05"); pg.wait_for_timeout(1500)
    pg.click("#r-ok")
    pg.clock.set_fixed_time("2026-10-27T09:10:00"); pg.wait_for_timeout(1200)
    pg.click("#seg-food"); pg.fill("#in-kcal", "400"); pg.fill("#in-label", "Late snack"); pg.check("#in-yday"); pg.click("#btn-add")
    pg.click("nav button[data-view=goal]"); pg.fill("#in-goal", "1"); pg.click("#f-goal button[type=submit]")
    pg.click("nav button[data-view=today]")
    pg.fill("#in-kcal", "300"); pg.fill("#in-label", "Breakfast"); pg.click("#btn-add")
    pg.click("nav button[data-view=menu]")
    assert pg.locator("#m-saved").inner_text() == "1,480 kcal", pg.locator("#m-saved").inner_text()
    raw = pg.evaluate("localStorage.getItem('burnbank.v1')")
    assert errors == [], errors
    b.close()

o = json.loads(raw)
assert "supp" not in o["today"] and "p" not in o["today"]["entries"][0], "this is not a v1 shape"
(root / "v1_backup.json").write_text(raw)
print("v1 backup written:", len(raw), "bytes; keys:", sorted(o.keys()))
