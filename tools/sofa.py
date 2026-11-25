"""Puts the gal on the room's sofa, lying on her stomach with her phone (author 2026-11-25: "背景のソファに
ギャルが寝っ転がってスマホ見ているといいかも。パンツは見えてもいい。どうせ小さいから"): writes
bg/room_<tod>.jpg from art/room_base/room_<tod>.jpg. On the upright screen the phone covers her, which the
author is fine with ("縦持ちのときはギャル見えなくていいよ").

The pose is iwf's sofa_phone seed 7300003 (7300001 was the first pick, but its skirt has a band:
author "スカートが違うな。帯入ってる"). A couch the cut-out kept would be keyed out by its color.

usage: python3 tools/sofa.py
"""
import os
import shutil

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = os.path.join(ROOT, 'game', 'assets', 'bg')
BASE = os.path.join(ROOT, 'art', 'room_base')  # the rooms without her (kept out of the game's files)
SRC = ('/media/nao/2nd/video-lab/gyal/lottery-sofa/portraits/ギャル（スター）/候補/透過/'
       '83e7cc3d63115ee0fca2acabdaf35c3b-7300003/portrait.png')
TODS = {'room_day.jpg': 1.0, 'room_eve.jpg': None, 'room_night.jpg': None}
# where she lies: her belly on the right sofa's seat, her width on the screen
SEAT_Y, MID_X, WIDTH = 880, 1360, 250


def cut():
    im = np.asarray(Image.open(SRC).convert('RGBA')).astype(float)
    r, g, b, a = (im[..., i] for i in range(4))
    couch = (r > 100) & (g < 70) & (b > 35) & (r - g > 60) & (b < r * 0.9)
    m = Image.fromarray((couch * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))
    a = np.minimum(a, 255 - np.asarray(m, dtype=float))
    out = np.dstack([r, g, b, a]).astype(np.uint8)
    fig = Image.fromarray(out, 'RGBA')
    return fig.crop(fig.getchannel('A').getbbox())


def light(fig, room):
    """Her colors brought to the room's light: the mean of the room's colors over its whole."""
    if room == 'room_day.jpg':
        return fig
    ref = np.asarray(Image.open(os.path.join(BASE, 'room_day.jpg')).convert('RGB')).astype(float).mean(axis=(0, 1))
    now = np.asarray(Image.open(os.path.join(BASE, room)).convert('RGB')).astype(float).mean(axis=(0, 1))
    a = np.asarray(fig).astype(float)
    a[..., :3] = np.clip(a[..., :3] * (now / ref), 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def main():
    os.makedirs(BASE, exist_ok=True)
    for room in TODS:
        if not os.path.exists(os.path.join(BASE, room)):
            shutil.copy(os.path.join(BG, room), os.path.join(BASE, room))
    fig = cut()
    k = WIDTH / fig.width
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    for room in TODS:
        bg = Image.open(os.path.join(BASE, room)).convert('RGBA')
        her = light(fig, room)
        # a soft shadow where she rests on the seat, so she does not float
        from PIL import ImageDraw
        sh = Image.new('L', bg.size, 0)
        ImageDraw.Draw(sh).ellipse((MID_X - her.width * 0.45, SEAT_Y - 26, MID_X + her.width * 0.45, SEAT_Y + 14), fill=110)
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        bg.paste(Image.new('RGBA', bg.size, (0, 0, 0, 255)), (0, 0), sh)
        bg.alpha_composite(her, (MID_X - her.width // 2, SEAT_Y - her.height))
        bg.convert('RGB').save(os.path.join(BG, room), quality=92)


if __name__ == '__main__':
    main()
