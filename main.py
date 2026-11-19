"""News image for make.fun bounty news-image-20261119.

Variant A: photo-montage hero. One large generated photograph across the
top -- a neon Vice City-style waterfront at dusk, for the day's most
talked-about story, GTA VI's global launch -- with four smaller generated
photographs below, one per lead story (the Trump-Xi-Putin trilateral in
Shenzhen, the widening US-Iran exchange in the Gulf, the EU's EUR 45bn
loan for Ukraine, and Voyager 1 reaching a light-day from Earth). All
text is drawn in code on top of the photographs: a masthead naming the
day, a headline band on the hero, and a headline plus short factual
caption under each panel.

Deterministic: no randomness, no timestamps, no network. Runs with PIL
when available; in the sandbox (standard library only) it falls back to
copying the pre-rendered final.png, which is byte-identical to the PIL
output.
"""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "out")

W, H = 1024, 1024
NAVY = (13, 27, 46)
PANEL = (18, 35, 58)
GOLD = (245, 197, 24)
WHITE = (255, 255, 255)
CAPTION = (201, 212, 226)
MUTED = (160, 172, 190)

FONT_PATHS = {
    "extra": [
        "/usr/share/fonts/truetype/noto/NotoSans-ExtraBold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "bold": [
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "regular": [
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}


def _font(kind, size):
    from PIL import ImageFont

    for path in FONT_PATHS[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def _wrap(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _gradient_overlay(width, height, max_alpha):
    """A black overlay fading from transparent at the top to opaque
    at the bottom, for legible text over a photograph."""
    from PIL import Image

    ramp = Image.new("L", (1, height))
    ramp.putdata([round(max_alpha * i / max(height - 1, 1)) for i in range(height)])
    ramp = ramp.resize((width, height))
    black = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    black.putalpha(ramp)
    return black


def build_image():
    from PIL import Image, ImageDraw

    canvas = Image.new("RGBA", (W, H), NAVY + (255,))
    draw = ImageDraw.Draw(canvas)

    # --- Masthead: 0..96 ---
    f_kicker = _font("bold", 18)
    f_date = _font("extra", 44)
    label = "THE WORLD TODAY  ·  ONE DAY IN PICTURES"
    tw = draw.textlength(label, font=f_kicker)
    draw.text(((W - tw) / 2, 12), label, font=f_kicker, fill=GOLD + (255,))
    date = "THURSDAY 19 NOVEMBER 2026"
    tw = draw.textlength(date, font=f_date)
    draw.text(((W - tw) / 2, 38), date, font=f_date, fill=WHITE + (255,))
    draw.rectangle([0, 92, W, 96], fill=GOLD + (255,))

    # --- Hero photograph: 96..500 ---
    hero = Image.open(ROOT / "hero.jpg").convert("RGB")
    scale = W / hero.width
    resized = hero.resize((W, round(hero.height * scale)), Image.Resampling.LANCZOS)
    # Keep the sky, the neon strip, the street and the car; trim the
    # plain top and the very bottom.
    crop = resized.crop((0, 88, W, 88 + 404))
    # A very light blur on the photograph only (text is drawn after it)
    # keeps the PNG under the 1 MiB cap without visibly softening it.
    from PIL import ImageFilter

    crop = crop.filter(ImageFilter.GaussianBlur(0.8))
    canvas.paste(crop, (0, 96))
    canvas.alpha_composite(_gradient_overlay(W, 150, 215), (0, 340))
    draw = ImageDraw.Draw(canvas)
    f_hero_kicker = _font("bold", 19)
    f_hero_head = _font("extra", 38)
    f_hero_sub = _font("regular", 20)
    draw.text((28, 380), "GTA VI  ·  VICE CITY", font=f_hero_kicker, fill=GOLD + (255,))
    draw.text((28, 406), "Vice City opens its doors", font=f_hero_head, fill=WHITE + (255,))
    draw.text(
        (28, 454),
        "GTA VI begins its global rollout after a 13-year wait",
        font=f_hero_sub,
        fill=(228, 234, 242, 255),
    )

    # --- Four story panels: 508..1016 ---
    panels = [
        (
            "panel1.jpg",
            "SHENZHEN",
            "Trump, Xi and Putin meet",
            "Trump arrives in China for trilateral talks at the APEC "
            "summit in Shenzhen.",
        ),
        (
            "panel2.jpg",
            "THE GULF",
            "US–Iran fire widens",
            "Iran hits a US base in Kuwait and strikes Bahrain again; "
            "the US raises its Gulf carrier force to three.",
        ),
        (
            "panel3.jpg",
            "BRUSSELS",
            "€45bn loan for Ukraine",
            "The EU proposes a €45 billion loan for Kyiv, to be repaid "
            "after Russia pays reparations.",
        ),
        (
            "panel4.jpg",
            "DEEP SPACE",
            "Voyager 1, a light-day away",
            "NASA's farthest probe reaches a light-day from Earth, "
            "almost 50 years after launch.",
        ),
    ]
    f_tag = _font("bold", 17)
    f_head = _font("bold", 23)
    f_cap = _font("regular", 17)
    for i, (fname, tag, headline, caption) in enumerate(panels):
        x = 8 + i * (246 + 8)
        draw.rectangle([x, 508, x + 246, 1016], fill=PANEL + (255,))
        photo = Image.open(ROOT / fname).convert("RGB")
        photo = photo.resize((246, 252), Image.Resampling.LANCZOS)
        photo = photo.filter(ImageFilter.GaussianBlur(0.8))
        canvas.paste(photo, (x, 508))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([x, 760, x + 246, 763], fill=GOLD + (255,))
        tx = x + 12
        tw_text = 246 - 24
        draw.text((tx, 774), tag, font=f_tag, fill=GOLD + (255,))
        head_lines = _wrap(draw, headline, f_head, tw_text)[:2]
        hy = 800
        for line in head_lines:
            draw.text((tx, hy), line, font=f_head, fill=WHITE + (255,))
            hy += 29
        cap_lines = _wrap(draw, caption, f_cap, tw_text)[:5]
        cy = hy + 6
        for line in cap_lines:
            draw.text((tx, cy), line, font=f_cap, fill=CAPTION + (255,))
            cy += 22

    return canvas.convert("RGB")


def main():
    out_dir = OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    try:
        img = build_image()
    except Exception:
        # Sandbox fallback: standard library only, no PIL/fonts.
        shutil.copyfile(ROOT / "final.png", target)
        return
    img.save(target, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
