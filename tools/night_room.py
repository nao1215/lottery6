"""Builds bg/room_night.jpg from bg/room_day.jpg, so night is the same room as day (author 2026-11-25:
"背景の部屋が時間帯によってだいぶ違うな。夜だけ違う？").

The room is darkened and cooled. The view through the window is drawn again as a night skyline
by img2img on the local ComfyUI (WAI SDXL): dots of light scattered over the day's buildings looked
like noise (author: "ビルの明かりが変だな"). Only the glass is replaced; the frame and the room stay.

usage: python3 tools/night_room.py [seed]   (the room in the game: seed 12, author 2026-11-25)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.expanduser('~/Desktop/gta/tools'))
import comfy  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = os.path.join(ROOT, 'game', 'assets', 'bg')
PROMPT = ('cityscape at night, skyline, many skyscrapers, countless lit office windows, bright city lights, '
          'night sky, scenery, no humans, detailed, masterpiece')
NEG = ('window frame, window, curtains, indoors, people, person, text, watermark, daytime, blue sky, clouds, sun, '
       'lowres, blurry')


def window(day):
    """The glass of the window (bool, the frame excluded) and its box."""
    r, g, b = (day[..., i] for i in range(3))
    h = day.shape[0]
    sky = (b > 190) & (b - r > 20)
    sky[int(h * 0.64):, :] = False  # below, a glass table reflects the sky
    xs = np.nonzero(sky.mean(axis=0) > 0.25)[0]
    ys = np.nonzero(sky[:, xs.min():xs.max()].mean(axis=1) > 0.25)[0]
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), int(h * 0.65)
    box = np.zeros(sky.shape, bool)
    box[y0:y1 + 1, x0:x1 + 1] = True
    bright = day.mean(axis=2)
    frame = (bright < 45) & (np.abs(r - b) < 30)  # the dark frame and mullion
    frame = np.asarray(Image.fromarray((frame * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
    return box & ~frame, (x0, y0, x1, y1)


def main(seed=1):
    day = np.asarray(Image.open(os.path.join(BG, 'room_day.jpg')).convert('RGB')).astype(float)
    h, w, _ = day.shape
    glass, (x0, y0, x1, y1) = window(day)
    room = day * np.array([0.30, 0.31, 0.40]) * (0.85 + 0.3 * np.linspace(0, 1, h)[:, None])[..., None]
    # the view: the day's skyline darkened under a navy sky, as the start of the redraw
    crop = Image.fromarray(day[y0:y1, x0:x1].astype(np.uint8))
    c = np.asarray(crop).astype(float)
    sky = (c[..., 2] > 170) & (c[..., 2] - c[..., 0] > 15) | (c.mean(axis=2) > 205)
    start = np.where(sky[..., None], np.array([16, 26, 60]), c * np.array([0.42, 0.40, 0.45]))
    start = Image.fromarray(np.clip(start, 0, 255).astype(np.uint8))
    sw, sh = 1024, round(1024 * start.height / start.width / 8) * 8
    night = comfy.sdxl(PROMPT, NEG, init=start.resize((sw, sh), Image.LANCZOS), denoise=0.58, seed=seed, steps=30, cfg=7.0)
    night = np.asarray(night.resize((x1 - x0, y1 - y0), Image.LANCZOS)).astype(float)
    view = room.copy()
    view[y0:y1, x0:x1] = night
    m = np.asarray(Image.fromarray((glass * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))) / 255.0
    out = room * (1 - m[..., None]) + view * m[..., None]
    name = 'room_night.jpg' if len(sys.argv) < 3 else sys.argv[2]
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(os.path.join(BG, name), quality=92)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
