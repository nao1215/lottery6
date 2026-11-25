"""The share card (game/assets/web/ogp.png, 1200x630) as a picture of the gal with a phone drawn in
front of it, upright, showing the game's pick page (author 2026-11-25: generated phones came out
tilted or back to the viewer, so "スマホは自分で描く"). The name "lottery6" in Fredoka Bold.

usage: python3 tools/ogp_mock.py PICTURE.jpg SCREEN.png [--x 0.3] [--name left|right]
The card in use (author 2026-11-25): art/ogp/bed_15.jpg (lottery_cg money_bed) and art/ogp_screen_en.png, --x 0.35.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ogp import FONT, EDGE, OUT, W, H, rounded_alpha  # noqa: E402

import numpy as np  # noqa: E402


def phone(screen, height):
    """A plain phone: a near-black frame with rounded corners and the screen inside."""
    b = round(height * 0.024)
    sw, sh = screen.size
    ih = height - 2 * b
    iw = round(ih * sw / sh)
    w = iw + 2 * b
    ph = Image.new('RGBA', (w, height), (0, 0, 0, 0))
    ImageDraw.Draw(ph).rounded_rectangle((0, 0, w - 1, height - 1), radius=round(w * 0.14), fill=(20, 20, 22, 255))
    # a faint edge light, so the frame reads as glass and metal, not a flat hole
    ImageDraw.Draw(ph).rounded_rectangle((1, 1, w - 2, height - 2), radius=round(w * 0.14), outline=(70, 70, 76, 255), width=2)
    s = screen.resize((iw, ih), Image.LANCZOS).convert('RGBA')
    s.putalpha(Image.fromarray(rounded_alpha(iw, ih)))
    ph.alpha_composite(s, (b, b))
    return ph


def main(picture, screen, x=0.3, name='left'):
    pic = Image.open(picture).convert('RGB')
    k = max(W / pic.width, H / pic.height)
    pic = pic.resize((round(pic.width * k), round(pic.height * k)), Image.LANCZOS)
    left = min(max(round(pic.width * x - W / 2), 0), pic.width - W)
    card = pic.crop((left, 0, left + W, H)).convert('RGBA')
    ph = phone(Image.open(screen).convert('RGB'), 600)
    at = (W - ph.width - 70, (H - ph.height) // 2)
    # a soft shadow under the phone
    mask = Image.new('L', card.size, 0)
    mask.paste(ph.split()[3], at)
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0))
    sh.putalpha(mask.point(lambda v: v * 120 // 255))
    sh = sh.transform(card.size, Image.AFFINE, (1, 0, -12, 0, 1, -16)).filter(ImageFilter.GaussianBlur(14))
    card.alpha_composite(sh)
    card.alpha_composite(ph, at)
    f = ImageFont.truetype(FONT, 104)
    f.set_variation_by_name('Bold')
    pos, anchor = ((44, 30), 'lt') if name == 'left' else ((at[0] - 30, H - 40), 'rs')
    s = Image.new('RGBA', card.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).text((pos[0] + 6, pos[1] + 8), 'lottery6', font=f, fill=(0, 0, 0, 120), anchor=anchor)
    card.alpha_composite(s.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(card).text(pos, 'lottery6', font=f, fill='white', anchor=anchor, stroke_width=8, stroke_fill=EDGE)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    card.convert('RGB').save(OUT)


if __name__ == '__main__':
    args = sys.argv[1:]
    opts = {}
    for key in ('--x', '--name'):
        if key in args:
            i = args.index(key)
            opts[key[2:]] = float(args[i + 1]) if key == '--x' else args[i + 1]
            del args[i:i + 2]
    main(args[0], args[1], **opts)
