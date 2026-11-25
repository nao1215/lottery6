"""Builds the share card, game/assets/web/ogp.png (1200x630), as the author asked (2026-11-25):
the gal holding her phone out to the viewer, the game's own pick screen on it ("ギャルスマホを持っていて
こちらに見せていて、ゲームの画面と同じロトが写っているといい"), and only the name "lottery6" in Fredoka
Bold laid on afterwards ("lottery6だけでいい", "フォントダサいと駄目だから、後付け合成がいい"; the author
picked Fredoka among four).

The picture is an iwf one-sheet (lottery_cg show_phone) drawn with a blank screen: the screen is
found as the largest bright, near-white quadrilateral, and the game's screen (a capture of the pick
page) is warped onto its four corners.

usage: /media/nao/2nd/iwf-gina/work/venv/bin/python tools/ogp.py SHEET.jpg PHONE_SCREEN.png [--x 0.5] [--quad x,y,x,y,x,y,x,y] [--zoom 1.2] [--crop x0,y0,x1,y1]
(needs OpenCV, which the lab's venv has)
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'game', 'assets', 'web', 'ogp.png')
FONT = os.path.join(ROOT, 'tools', 'fonts', 'Fredoka.ttf')  # SIL OFL (tools/fonts/OFL-Fredoka.txt)
W, H = 1200, 630
# The edge of the name, the phone's coral (author 2026-11-26; it was the mint #13a58a).
EDGE = (198, 108, 114)
PANEL = (245, 245, 247)  # the phone pages' ground (ui.phone.background #f5f5f7)


def screen_quad(img):
    """The phone's blank screen: the largest bright, low-saturation region, as 4 corners (tl, tr, br, bl)."""
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask = ((hsv[..., 2] > 215) & (hsv[..., 1] < 40)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    best = max(range(1, n), key=lambda i: stats[i, cv2.CC_STAT_AREA])
    cnt, _ = cv2.findContours((labels == best).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnt, key=cv2.contourArea)
    quad = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True).reshape(-1, 2)
    if len(quad) != 4:
        quad = cv2.boxPoints(cv2.minAreaRect(c))
    s, d = quad.sum(axis=1), np.diff(quad, axis=1).ravel()
    return np.float32([quad[np.argmin(s)], quad[np.argmin(d)], quad[np.argmax(s)], quad[np.argmax(d)]])


def logo_screen(w=470, h=1000):
    """The screen the gal holds out: only the name, on the game's ground (author 2026-11-25:
    "スマホの中にロゴ、右にロト6の画面")."""
    im = Image.new('RGBA', (w, h), PANEL + (255,))
    f = ImageFont.truetype(FONT, round(w * 0.25))
    f.set_variation_by_name('Bold')
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((w / 2 + 4, h * 0.46 + 6), 'lottery6', font=f, fill=(0, 0, 0, 90), anchor='mm')
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(im).text((w / 2, h * 0.46), 'lottery6', font=f, fill='white', anchor='mm', stroke_width=round(w * 0.018), stroke_fill=EDGE)
    return np.asarray(im.convert('RGB'))


def mockup(screen, height):
    """A plain phone (black frame, rounded) showing screen, height px tall, with a soft shadow."""
    sh, sw = screen.shape[:2]
    b = round(height * 0.022)  # frame
    ih = height - 2 * b
    iw = round(ih * sw / sh)
    w = iw + 2 * b
    ph = Image.new('RGBA', (w, height), (0, 0, 0, 0))
    ImageDraw.Draw(ph).rounded_rectangle((0, 0, w - 1, height - 1), radius=round(w * 0.13), fill=(22, 22, 24, 255))
    scr = Image.fromarray(screen).resize((iw, ih), Image.LANCZOS).convert('RGBA')
    scr.putalpha(Image.fromarray(rounded_alpha(iw, ih)))
    ph.alpha_composite(scr, (b, b))
    return ph


def rounded_alpha(w, h):
    """A w x h mask with rounded corners like a phone's screen (radius 9% of the width)."""
    a = Image.new('L', (w, h), 0)
    ImageDraw.Draw(a).rounded_rectangle((0, 0, w - 1, h - 1), radius=round(w * 0.09), fill=255)
    return np.asarray(a)


def fit_screen(scr, quad):
    """The game's screen padded with its own ground to the shape of the phone's screen, with room at
    the bottom: squeezed into a screen of another shape the buttons were crowded at the bottom and
    the last one ran into the rounded corners (author 2026-11-25: "下はボタンが詰まってる")."""
    tl, tr, br, bl = quad
    aspect = (np.linalg.norm(tr - tl) + np.linalg.norm(br - bl)) / (np.linalg.norm(bl - tl) + np.linalg.norm(br - tr))
    h, w = scr.shape[:2]
    ground = np.median(scr[:, :3].reshape(-1, 3), axis=0).astype(np.uint8).tolist()  # the screen's left edge
    # the capture's own phone frame shows dark in the crop's corners: the ground there
    scr = scr.copy()
    r = round(w * 0.12)
    for ys, xs in ((slice(0, r), slice(0, r)), (slice(0, r), slice(w - r, w)), (slice(h - r, h), slice(0, r)), (slice(h - r, h), slice(w - r, w))):
        part = scr[ys, xs]
        part[part.astype(int).sum(axis=2) < 450] = ground
    bottom = 0  # the capture keeps its own room under the buttons (the page fits the screen)
    hh = h + bottom
    ww = max(w, round(hh * aspect))
    hh = max(hh, round(ww / aspect))
    out = np.empty((hh, ww, 3), np.uint8)
    out[:] = ground
    x = (ww - w) // 2
    out[:h, x:x + w] = scr
    return out


def cover_card(out, x, zoom):
    """The picture fills the card, around x (a share of the width)."""
    k = W / out.width if out.width / out.height < W / H else H / out.height
    k *= zoom  # zoom in to leave out what is at the picture's edges
    out = out.resize((round(out.width * k), round(out.height * k)), Image.LANCZOS)
    left = min(max(round(out.width * x - W / 2), 0), out.width - W)
    top = min(max(0, round((out.height - H) * 0.3)), out.height - H)
    return out.crop((left, top, left + W, top + H)).convert('RGBA')


def panel_left(card, crop):
    x0, y0, x1, y1 = crop
    return round((x1 - x0) * H / (y1 - y0))


def panel_card(out, crop):
    """The crop (x0,y0,x1,y1 of the picture) fills the card's height on the left with a straight
    edge, and a panel of the game's ground color takes the rest (author 2026-11-25: the skirt's
    band trimmed out, and a fade into the wall looked unnatural, "ぼかし方が不自然")."""
    pic = out.crop(crop).resize((panel_left(None, crop), H), Image.LANCZOS)
    card = Image.new('RGB', (W, H), PANEL)
    card.paste(pic, (0, 0))
    # a thin coral line where the picture ends, so the edge reads as a deliberate split
    ImageDraw.Draw(card).rectangle((pic.width, 0, pic.width + 5, H), fill=EDGE)
    return card.convert('RGBA')


def main(sheet, phone, x=0.5, quad=None, zoom=1.0, crop=None, name_x=985, split=None):
    img = np.asarray(Image.open(sheet).convert('RGB'))
    quad = screen_quad(img) if quad is None else np.float32(quad)
    # reach out to the black frame: the generated screen's own drawing in its rounded corners and
    # beside the notch must not show; the frame (dark) is kept below
    mid = quad.mean(axis=0)
    quad = mid + (quad - mid) * 1.02
    game = np.asarray(Image.open(phone).convert('RGB'))
    scr = fit_screen(logo_screen() if split else game, quad)
    h, w = scr.shape[:2]
    m = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), quad)
    warped = cv2.warpPerspective(scr, m, (img.shape[1], img.shape[0]))
    inside = cv2.warpPerspective(np.full((h, w), 255, np.uint8), m, (img.shape[1], img.shape[0]))
    # The whole screen takes the game, but the fingers over its edge (skin, pink nails) stay in
    # front. Keeping only the blank white let the lines and letters drawn on the generated screen
    # show through the game (author 2026-11-25: "スマホの合成劣化してない？").
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(int)
    finger = (hsv[..., 1] > 60) & (hsv[..., 2] > 60)
    finger = cv2.morphologyEx(finger.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    finger = cv2.dilate(finger, np.ones((3, 3), np.uint8)) * 255
    # The game's screen has rounded corners of its own (rounded_alpha), so no square corner of it
    # shows past the frame (author 2026-11-25: "矩形のはしがみえる"); the frame and the notch
    # (dark) stay in front.
    corners = cv2.warpPerspective(rounded_alpha(w, h), m, (img.shape[1], img.shape[0]))
    dark = cv2.dilate((hsv[..., 2] < 80).astype(np.uint8), np.ones((3, 3), np.uint8)) * 255
    # and nothing past the phone's outline (the black frame, filled), however the corners round
    ring = cv2.morphologyEx((hsv[..., 2] < 80).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cs, _ = cv2.findContours(ring, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    mid = tuple(float(v) for v in quad.mean(axis=0))
    body = np.zeros(ring.shape, np.uint8)
    for c in sorted(cs, key=cv2.contourArea, reverse=True):
        if cv2.pointPolygonTest(c, mid, False) >= 0:
            cv2.drawContours(body, [c], -1, 255, -1)
            break
    body = cv2.erode(body, np.ones((5, 5), np.uint8))
    inside = cv2.min(cv2.min(cv2.min(inside, corners), body), 255 - np.maximum(finger, dark))
    inside = cv2.GaussianBlur(inside, (3, 3), 0)[..., None] / 255.0
    # The generated screen's white left between the frame and the game's edge (thin dashes along
    # the top) takes the game's ground; nothing outside the phone is painted (a square frame-colored
    # fill there stuck out past the rounded frame, author 2026-11-25: "角が飛び出ている").
    img = img.copy()
    near = cv2.dilate((inside[..., 0] > 0).astype(np.uint8), np.ones((11, 11), np.uint8)) > 0
    left = near & (inside[..., 0] == 0) & (hsv[..., 2] > 140) & (hsv[..., 1] < 50) & (finger == 0)
    left &= cv2.warpPerspective(np.full((h, w), 255, np.uint8), m, (img.shape[1], img.shape[0]), borderValue=0) > 0
    left &= body > 0
    img[left] = scr[h // 2, 2]
    out = Image.fromarray((img * (1 - inside) + warped * inside).astype(np.uint8))
    if split is not None:
        save(split_card(out, split, fit_screen(game, quad)))
        return
    if crop is not None:
        card = panel_card(out, crop)
    else:
        card = cover_card(out, x, zoom)
    f = ImageFont.truetype(FONT, 100 if crop is None else 84)
    f.set_variation_by_name('Bold')
    # the name: top right over the wall, or in the middle of the panel on the right
    # (author 2026-11-25: "lottery6を右中央に置けば？")
    if crop is None:
        at, anchor = (W - 48, H / 2), 'rm'  # right middle (author 2026-11-25)
    else:
        at, anchor = (name_x, H / 2), 'mm'  # the middle of the free space right of the phone
    shadow = Image.new('RGBA', card.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((at[0] + 6, at[1] + 8), 'lottery6', font=f, fill=(0, 0, 0, 120), anchor=anchor)
    card.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(card).text(at, 'lottery6', font=f, fill='white', anchor=anchor, stroke_width=8, stroke_fill=EDGE)
    save(card)


def save(card):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    card.convert('RGB').save(OUT)


def split_card(out, split, game):
    """The picture from x0,y0 of it (scaled so x0..x1 fills the card's width), the gal's phone
    showing the name, and the game's pick screen on a second phone at the right, over what is there
    (a skirt drawn with a band, another person's hand)."""
    x0, y0, x1 = split
    k = W / (x1 - x0)
    pic = out.resize((round(out.width * k), round(out.height * k)), Image.LANCZOS)
    card = pic.crop((round(x0 * k), round(y0 * k), round(x0 * k) + W, round(y0 * k) + H)).convert('RGBA')
    ph = mockup(game, 640)
    ph = ph.rotate(-4, resample=Image.BICUBIC, expand=True)
    shadow = Image.new('RGBA', card.size, (0, 0, 0, 0))
    at = (W - ph.width - 6, 4)
    shadow.alpha_composite(Image.new('RGBA', ph.size, (0, 0, 0, 110)), at)
    shadow.putalpha(Image.fromarray(np.minimum(np.asarray(shadow.split()[3]), 255)))
    mask = Image.new('L', card.size, 0)
    mask.paste(ph.split()[3], at)
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0))
    sh.putalpha(mask.point(lambda v: v * 110 // 255))
    sh = sh.transform(card.size, Image.AFFINE, (1, 0, -10, 0, 1, -14)).filter(ImageFilter.GaussianBlur(12))
    card.alpha_composite(sh)
    card.alpha_composite(ph, at)
    return card


if __name__ == '__main__':
    args = sys.argv[1:]
    x = 0.5
    if '--x' in args:
        i = args.index('--x')
        x = float(args[i + 1])
        del args[i:i + 2]
    quad = None
    if '--quad' in args:  # the screen's corners tl,tr,br,bl as x,y,x,y,... when finding them fails
        i = args.index('--quad')
        v = [float(n) for n in args[i + 1].split(',')]
        quad = [v[k:k + 2] for k in range(0, 8, 2)]
        del args[i:i + 2]
    zoom = 1.0
    if '--zoom' in args:
        i = args.index('--zoom')
        zoom = float(args[i + 1])
        del args[i:i + 2]
    crop = None
    if '--crop' in args:  # x0,y0,x1,y1 of the picture on the left, the wall's color as a panel on the right
        i = args.index('--crop')
        crop = tuple(int(n) for n in args[i + 1].split(','))
        del args[i:i + 2]
    name_x = 985
    if '--name-x' in args:  # where the name's middle goes across the card, with --crop
        i = args.index('--name-x')
        name_x = float(args[i + 1])
        del args[i:i + 2]
    split = None
    if '--split' in args:  # x0,y0,x1 of the picture: logo on the gal's phone, the game on a phone at the right
        i = args.index('--split')
        split = tuple(int(n) for n in args[i + 1].split(','))
        del args[i:i + 2]
    main(args[0], args[1], x, quad, zoom, crop, name_x, split)
