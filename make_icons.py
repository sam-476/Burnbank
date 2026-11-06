"""Launcher icon PNGs for pre-Oreo launchers: charcoal rounded plate, amber hand and dot (same mark as the adaptive icon)."""
import pathlib
from PIL import Image, ImageDraw

root = pathlib.Path(__file__).parent / "android" / "res"
sizes = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
BG = (20, 22, 27, 255)
AMBER = (232, 163, 61, 255)

for name, px in sizes.items():
    S = 8  # supersample
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = n * 0.2
    d.rounded_rectangle((0, 0, n - 1, n - 1), radius=r, fill=BG)
    c = n / 2
    hw = n * 0.09
    d.rounded_rectangle((c - hw / 2, c - n * 0.3, c + hw / 2, c + hw / 2), radius=hw / 2, fill=AMBER)
    dr = n * 0.075
    d.ellipse((c - dr, c - dr, c + dr, c + dr), fill=AMBER)
    out = img.resize((px, px), Image.LANCZOS)
    folder = root / ("mipmap-" + name)
    folder.mkdir(exist_ok=True)
    out.save(folder / "ic_launcher.png")
    print(name, px)
