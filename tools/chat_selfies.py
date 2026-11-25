"""Builds the selfies the gal sends Aoi in chat when she wants money: game/assets/selfies/<n>.jpg,
720x960 (3:4), cut around her face from iwf lottery_cg's selfie scenes (葵に送る自撮り, 胸元 and
寝そべり), her hoodie open at the chest.

The author 2026-11-25: "葵に贈る写真はちょっと胸元見えててもいいんじゃない。だから金渡すんだろ多分".
2026-11-26 the author picked these from the eight drawn ("7,9,12がアウトかな": a plaid skirt or
lavender hair tips; the skirt is plain yellow and the hair one color), then "パーカーが正しいのは8,11だけ
かも": her hoodie is a pullover with no zipper, so a zipped front or an open one showing a bra is out.
2026-11-26 the author took the nine with a plain yellow skirt from the night's batch (selfie_nozip and
the rest; "スカートに柄があるのがあるな", "チャットは今回選んだのでいい"). The plain selfies they replace
(the old tools/selfies.py) are kept in art/selfies_plain/, outside the repository.

usage: python3 tools/chat_selfies.py
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'game', 'assets', 'selfies')
SRC = '/media/nao/2nd/video-lab/gyal/lottery-cg/ok/ギャル（スター・着衣）/lottery6 の一枚絵（タイトル・当選）'
# (run folder, picture, where her face is across the picture, 0..1)
PICKS = [
    ('20261125_1543_3', '08_葵に送る自撮り（胸元）.jpg', 0.69),
    ('20261126_0236', '17_葵に送る自撮り（胸元・チャックなし）.jpg', 0.35),
    ('20261126_0250_4', '17_葵に送る自撮り（胸元・チャックなし）.jpg', 0.3),
    ('20261126_0251_3', '17_葵に送る自撮り（胸元・チャックなし）.jpg', 0.31),
    ('20261126_0251_4', '17_葵に送る自撮り（胸元・チャックなし）.jpg', 0.69),
    ('20261126_0251_6', '17_葵に送る自撮り（胸元・チャックなし）.jpg', 0.69),
    ('20261126_0236_5', '18_葵に送る自撮り（寝そべり・チャックなし）.jpg', 0.3),
    ('20261126_0236_6', '18_葵に送る自撮り（寝そべり・チャックなし）.jpg', 0.5),
    ('20261126_0232', '08_葵に送る自撮り（胸元）.jpg', 0.58),
]
W, H = 720, 960


def selfie(path, face_x):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    cw = round(h * W / H)
    x0 = min(max(round(face_x * w - cw / 2), 0), w - cw)
    return im.crop((x0, 0, x0 + cw, h)).resize((W, H), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for n, (run, name, face_x) in enumerate(PICKS, 1):
        selfie(os.path.join(SRC, run, name), face_x).save(os.path.join(OUT, f'{n}.jpg'), quality=90)
    # Remove numbered selfies past the picks (the plain set had more).
    n = len(PICKS) + 1
    while os.path.exists(os.path.join(OUT, f'{n}.jpg')):
        os.remove(os.path.join(OUT, f'{n}.jpg'))
        n += 1
    print(f'{len(PICKS)} selfies in {OUT}')


if __name__ == '__main__':
    main()
