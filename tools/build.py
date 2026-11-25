"""Writes game/game.yaml and game/data/world.yaml for lottery6.

A number lottery played on the phone: pick 6 of 43 numbers for up to 5 sets
(A to E) or let the phone pick them, buy, and watch the 6 numbers and the bonus
drawn one by one, the matching numbers lighting up. The odds are those of a real
6/43 lottery because the draw is real: 6 distinct numbers and a bonus out of 43.
Prizes are a 6/43 lottery's theoretical values (MUFG Bank's Loto 6 page, read
2026-11-25: https://www.bk.mufg.jp/tsukau/sonota/takarakuji/loto6/index.html).
The gal shows only at the start and on a win; the rest is the phone.

Needs gozen with page cells (columns, selected), buttons that stay and still
phones (local branch feat/phone-page-keys).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, '..', 'game')
# One set per purchase (2026-11-25 the author: a draw comes out at once, unlike the real
# thing, so buy one line at a time and let auto mode repeat it).
N, PICK, SETS, PRICE = 43, 6, 1, 200
LETTERS = 'ABCDE'
# tier: (name, prize)
TIERS = {1: ('1等', 200000000), 2: ('2等', 10000000), 3: ('3等', 300000), 4: ('4等', 6800), 5: ('5等', 1000)}
# The phone is held upright: sideways was harder to read (author 2026-11-25).
# The public URL of the web build (ends with /).
WEB_URL = 'https://nao1215.github.io/lottery6/'
HOLD = 'portrait'
# Seconds a result stays on auto before the next draw.
AUTO_PACE = 0.25
# On auto: draws a win's face stays, and the run of misses after which she looks troubled, then tired.
FACE_HOLD = 60
TROUBLED_AFTER = 150
TIRED_AFTER = 500
# Seconds a win's result stays on the phone on auto.
HIT_STOP = 2.2
# The phone's colors after the ORBIS app's screens (Fuller, Inc.; the author 2026-11-26 found the
# mint and the deco mock-ups "LLMっぽい" and chose "フラーのアプリ", then the coral): a pale gray
# ground, white cards, unpicked numbers white with a hairline (no soft fill), #484848 text. The coral
# is a shade deeper than ORBIS's #e89090 (it writes #c87880 for its coral text) so that gozen puts
# white text on it; a matched number is a muted gold.
PALETTE = dict(accent='#c66c72', background='#f5f5f7', text='#484848', muted='#a3a3aa', card='#ffffff', mark='#c9a45c')
ACCENT = PALETTE['accent']
PICK_COLOR = PALETTE['accent']


def v(name):
    return f'var.{name}'


def p(s, n):
    """Whether set s holds number n (0 or 1)."""
    return f'var.p{s}_{n}'


def count_sets_and_slots():
    return [count_sets(), {'call': 'slots'}]


def count_sets():
    return {'set': {v('sets'): ' + '.join(f'min(1, max(0, var.c{s} - 5))' for s in range(1, SETS + 1))}}


def draw_into(target, how_many, tag):
    """Commands drawing how_many distinct numbers of 1..N: var.x_n marks the drawn
    ones; target(k, n) are the commands that keep number n as the k-th drawn."""
    out = [{'set': {f'var.x_{n}': 0 for n in range(1, N + 1)}}]
    for k in range(1, how_many + 1):
        out.append({'set': {v('r'): f'rand({N - k + 1}) + 1'}})
        for n in range(1, N + 1):
            out.append({'if': f'var.x_{n} == 0', 'then': [
                {'set': {v('r'): 'var.r - 1'}},
                {'if': 'var.r == 0', 'then': [{'set': {f'var.x_{n}': 1}}] + target(k, n)},
            ]})
    return out


def key_event(n):
    """Toggle number n in the set being picked; a seventh number is not taken."""
    out = []
    for s in range(1, SETS + 1):
        out.append({'if': f'var.cur == {s}', 'then': [
            {'if': f'{p(s, n)} == 1', 'then': [{'set': {p(s, n): 0, f'var.c{s}': f'var.c{s} - 1'}}],
             'else': [{'if': f'var.c{s} < {PICK}', 'then': [{'set': {p(s, n): 1, f'var.c{s}': f'var.c{s} + 1'}}]}]},
        ]})
    return [{'sfx': 'tink'}] + out + count_sets_and_slots()


def clear_event():
    out = []
    for s in range(1, SETS + 1):
        sets = {p(s, n): 0 for n in range(1, N + 1)}
        sets[f'var.c{s}'] = 0
        out.append({'if': f'var.cur == {s}', 'then': [{'set': sets}]})
    return out + count_sets_and_slots()


def random_event():
    out = draw_into(lambda k, n: [], PICK, 'pick')
    for s in range(1, SETS + 1):
        sets = {p(s, n): f'var.x_{n}' for n in range(1, N + 1)}
        sets[f'var.c{s}'] = PICK
        out.append({'if': f'var.cur == {s}', 'then': [{'set': sets}]})
    return out + count_sets_and_slots()


def random_all_event():
    out = []
    for s in range(1, SETS + 1):
        out += [{'set': {v('cur'): s}}, {'call': 'random'}]
    return out + [{'set': {v('cur'): 1}}]


# The header: the money, and how many numbers the set being picked holds.
PICK_TITLE = '{var.c1}/6'


def pick_page():
    """The pick page (author 2026-11-25; the colors after ORBIS since 2026-11-26): the money large on top, the six
    numbers picked so far on a card, the 43 balls on a card, the buy button at the bottom."""
    # No label over the six slots and no stats line: the page has to fit the phone's screen, or
    # the buttons above Buy were cut under it (author 2026-11-25); an empty slot shows "・", and the
    # result page shows the stats.
    rows = []
    for j in range(1, PICK + 1):
        rows.append({'text': f'{{var.c1 >= {j} ? var.s1_{j} : "・"}}', 'columns': PICK, 'round': True,
                     'selected': f'var.c1 >= {j}', 'card': 'picks'})
    for n in range(1, N + 1):
        rows.append({'button': str(n), 'id': f'n{n}', 'columns': 7, 'round': True, 'stay': True,
                     'selected': f'{p(1, n)} == 1', 'event': f'key_{n}', 'card': 'grid'})
    rows += [
        {'button': 'ランダム', 'id': 'random', 'columns': 2, 'stay': True, 'event': 'random', 'card': 'grid'},
        {'button': 'クリア', 'id': 'clear', 'columns': 2, 'stay': True, 'event': 'clear', 'card': 'grid'},
        # The language switch (author 2026-11-25: "言語を簡単に日本語切り替えできるようにして欲しい"), at the
        # top right of the app bar (author 2026-11-25: "言語切り替えは右上にあるべきでは？"; gozen corner): it
        # reads "English" in Japanese and "日本語" in English (lang/en.yaml).
        {'button': 'English', 'id': 'lang', 'corner': True, 'stay': True, 'event': 'switch_language'},
        {'button': f'購入する（{PRICE}円）', 'id': 'buy', 'bottom': True, 'when': f'var.sets > 0 && gold >= {PRICE}'},
        # Auto is back on the pick page too (author 2026-11-25: "購入画面でオートを出すか"); with no
        # numbers picked it picks them at random.
        {'button': 'オート購入', 'id': 'auto', 'bottom': True, 'style': 'secondary', 'when': f'gold >= {PRICE}'},
        {'button': '葵くんにせびる', 'id': 'beg', 'bottom': True, 'when': f'gold < {PRICE}'},
    ]
    return {'phone': {'app': 'page', 'hold': HOLD, 'bar': 'large', 'title': '{grouped(gold)}円', 'color': ACCENT,
                      'var': 'var.pick', 'still': True, 'rows': rows}}


def slots_event():
    """s1_<j>: the j-th smallest number picked so far, for the six slots on the pick page."""
    body = [{'set': {v('slot'): 0}}]
    for n in range(1, N + 1):
        body.append({'if': f'{p(1, n)} == 1', 'then': [{'set': {v('slot'): 'var.slot + 1'}}] + [
            {'if': f'var.slot == {j}', 'then': [{'set': {f'var.s1_{j}': n}}]} for j in range(1, PICK + 1)]})
    return body


def sort_sets():
    """b<s>_<j>: the j-th smallest number of each full set."""
    out = []
    for s in range(1, SETS + 1):
        body = [{'set': {v('slot'): 0}}]
        for n in range(1, N + 1):
            body.append({'if': f'{p(s, n)} == 1', 'then': [{'set': {v('slot'): 'var.slot + 1'}}] + [
                {'if': f'var.slot == {j}', 'then': [{'set': {f'var.b{s}_{j}': n}}]} for j in range(1, PICK + 1)]})
        out.append({'if': f'var.c{s} == {PICK}', 'then': body})
    return out


def judge():
    """m<s>: main numbers matched, k<s>: bonus matched, t<s>: the tier (0 none),
    and the prize paid."""
    out = [{'set': {v('got'): 0, v('best'): 9}}]
    for s in range(1, SETS + 1):
        body = [{'set': {f'var.m{s}': 0, f'var.k{s}': 0, f'var.t{s}': 0, f'var.tn{s}': '"はずれ"'}}]
        for j in range(1, PICK + 1):
            b = f'var.b{s}_{j}'
            body.append({'if': ' || '.join(f'{b} == var.d{k}' for k in range(1, PICK + 1)), 'then': [{'set': {f'var.m{s}': f'var.m{s} + 1'}}]})
            body.append({'if': f'{b} == var.d7', 'then': [{'set': {f'var.k{s}': 1}}]})
        rules = [(1, f'var.m{s} == 6'), (2, f'var.m{s} == 5 && var.k{s} == 1'), (3, f'var.m{s} == 5'), (4, f'var.m{s} == 4'), (5, f'var.m{s} == 3')]
        chain = []
        for tier, cond in reversed(rules):
            name, prize = TIERS[tier]
            then = [{'set': {f'var.t{s}': tier, f'var.tn{s}': f'"{name}"', v('got'): f'var.got + {prize}', v('best'): f'min(var.best, {tier})'}},
                    {'gold': prize}]
            chain = [{'if': cond, 'then': then, **({'else': chain} if chain else {})}]
        body += chain
        out.append({'if': f'var.c{s} == {PICK}', 'then': body})
    return out + [{'set': {v('won'): 'var.won + var.got'}}]


def board(rev, final, auto=False, hold=AUTO_PACE):
    """The draw page (design A): the result large on top, the drawn balls on a card, your
    numbers on a card with the matching ones marked gold, the prize on a card, the buttons
    at the bottom."""
    rows = []
    if final:
        rows.append({'text': 'はずれ', 'size': 'display', 'when': 'var.t1 == 0'})
        for t, (name, _) in TIERS.items():
            rows.append({'text': name, 'size': 'display', 'when': f'var.t1 == {t}'})
    if auto:
        rows.append({'text': 'オート購入中', 'size': 'small'})
    rows.append({'text': '当せん番号（右はボーナス）', 'size': 'small', 'card': 'drawn'})
    for k in range(1, PICK + 2):
        label = f'{{var.d{k}}}' if k <= rev else '?'
        rows.append({'text': label, 'columns': 7, 'card': 'drawn', 'selected': 'true' if k <= min(rev, PICK) else 'false'})
    shown = [f'var.d{k}' for k in range(1, min(rev, PICK) + 1)]
    rows.append({'text': 'あなたの番号', 'size': 'small', 'card': 'mine'})
    for j in range(1, PICK + 1):
        b = f'var.b1_{j}'
        hit = ' || '.join(f'{b} == {d}' for d in shown) or 'false'
        if final and rev > PICK:
            hit = f'{hit} || {b} == var.d7 && var.m1 == 5'
        rows.append({'text': f'{{{b}}}', 'columns': PICK, 'card': 'mine', 'marked': hit})
    if final:
        rows += [
            {'text': '当せん金', 'size': 'small', 'card': 'prize'},
            {'text': '+{grouped(var.got)}円', 'size': 'display', 'card': 'prize'},

            {'text': '累計 {grouped(var.draws)}口', 'size': 'small'},
            {'text': '使った額 {grouped(var.spent)}円', 'size': 'small'},
            {'text': '当せん累計 {grouped(var.won)}円', 'size': 'small'},
        ]
        if auto:
            rows.append({'button': 'オートを止める', 'id': 'stop', 'bottom': True})
        else:
            # Auto is offered only after a miss, as keeping these numbers (author 2026-11-25).
            rows += [{'button': '同じ番号でもう一回', 'id': 'again', 'bottom': True, 'when': f'gold >= {PRICE}'},
                     {'button': 'この番号でオート', 'id': 'auto', 'bottom': True, 'style': 'secondary', 'when': 'var.got == 0'},
                     {'button': '番号を選ぶ', 'id': 'pick', 'bottom': True, 'style': 'secondary'}]
    # The tier is a row of its own per tier (a text, so lang/ translates it), the title the money.
    title = '{grouped(gold)}円' if final else '第{grouped(var.draws)}回 抽せん'
    cue = {'app': 'page', 'hold': HOLD, 'bar': 'large', 'title': title, 'color': ACCENT, 'still': True, 'rows': rows}
    if final:
        cue['var'] = 'var.after'
        if auto:
            cue.update({'timeout': hold, 'timeout_result': 'again'})
    else:
        fast = 0.15 if auto else 0.5
        cue.update({'var': 'var.tick', 'timeout': fast if rev < PICK else fast * 2})
    return {'phone': cue}




def win_event():
    """The amount is on the phone (the result held there like a hit stop); her picture and a line
    answer it, with no figure by her (author 2026-11-25)."""
    def show(kind, n):
        out = [{'set': {v('pic'): f'rand({n})'}}]
        for i in range(n):
            # On the upright screen the wide picture fills it, its sides cut off (author 2026-11-25:
            # "見切れていい。縦長のときは。どうせ当たらないから").
            pic = lambda tod: {'image': {'file': f'scenes/{kind}_{i + 1}_{tod}.jpg', 'fade': 0.15, 'fit': 'cover'}}
            out.append({'if': f'var.pic == {i}', 'then': [{'if': TOD_DAY, 'then': [pic('day')], 'else': [
                {'if': TOD_EVE, 'then': [pic('eve')], 'else': [pic('night')]}]}]})
        # No line by her: nothing waits for a press, the picture stays a moment and the amount follows
        # (author 2026-11-25: "プレイが止まるから、会話は気になるわ").
        out.append({'wait': 2.0})
        return out + [{'image': {'file': '', 'fade': 0}}]

    # Only the top prize shows a picture; the rest is the sound and the amount on the phone
    # (author 2026-11-25: "一枚絵は最高金額だけにして、残りはチャット欄用だけ").
    def top():
        # The top prize's one-sheet: she throws the notes about in a windowless white room (iwf
        # lottery_cg money_throw_living, run 20261126_0207_6). The author picked it 2026-11-26
        # ("クリアは6にする") after the tower pictures came out "全部色が変"; those are kept in
        # art/top_tower/.
        return [{'image': {'file': 'scenes/top.jpg', 'fade': 0.15, 'fit': 'cover'}},
                {'wait': 2.0}, {'image': {'file': '', 'fade': 0}}]

    return [{'if': 'var.best <= 2', 'then': [{'sfx': 'fanfare'}] + top(), 'else': [
        {'if': 'var.best == 3', 'then': [{'sfx': 'jingle'}]},
        {'if': 'var.best == 4', 'then': [{'sfx': 'levelup'}]},
        {'if': 'var.best == 5', 'then': [{'sfx': 'treasure'}]}]}]


# The time (author 2026-11-25: "時間の概念をつけて"): var.clock_minutes, shown on the phone's
# status bar, moves on with every draw. Aoi is at work by day and home from 23:00 to 8:00.
MINUTES_PER_DRAW = 3
START_MINUTES = 20 * 60
# The part of the day, shown by the room's window (author 2026-11-25: "時間の概念は背景の窓の外で分からんと"):
# day 6:00-16:59, evening 17:00-18:59, night otherwise.
TOD_DAY = 'var.clock_minutes % 1440 >= 360 && var.clock_minutes % 1440 < 1020'
TOD_EVE = 'var.clock_minutes % 1440 >= 1020 && var.clock_minutes % 1440 < 1140'
ROOMS = {'room_day': 'bg/room_day.jpg', 'room_eve': 'bg/room_eve.jpg', 'room': 'bg/room_night.jpg'}


def to_room():
    """Back into the room of the hour (the loop's next turn starts there)."""
    return {'if': TOD_DAY, 'then': [{'move': 'room_day'}], 'else': [
        {'if': TOD_EVE, 'then': [{'move': 'room_eve'}], 'else': [{'move': 'room'}]}]}


def play_event():
    out = [{'gold': f'-(var.sets * {PRICE})'},
           {'set': {'var.clock_minutes': f'var.clock_minutes + {MINUTES_PER_DRAW}'}},
           {'set': {v('spent'): f'var.spent + var.sets * {PRICE}', v('draws'): 'var.draws + 1'}}]
    out += sort_sets()
    out += draw_into(lambda k, n: [{'set': {f'var.d{k}': n}}], PICK + 1, 'draw')
    # Show the main numbers in order, as a draw lists them.
    out += judge()
    # Her picture is not on screen all the time: she shows at the milestones (author 2026-11-25:
    # "ギャルは節目節目で画像出すか。お金を半分失ったとか、ゼロになったとかで。立ち絵を常時出す必要はないかも").
    mood = []

    def reveal(auto):
        # A win shows her picture first, then the amount on the phone (author 2026-11-25:
        # "当選時はギャルの一枚絵を出してから金額表示かも").
        return [board(rev, False, auto) for rev in range(0, PICK + 2)] + mood + [
            {'if': 'var.got > 0', 'then': [{'call': 'win'}]}, board(PICK + 1, True, auto)]
    # Left on auto the draws tick by like a clicker game: no reveal, the result at once
    # (author 2026-11-25: "クッキークリッカーなみに小気味良く").
    # A win holds its result on the phone like a hit stop, even 1,000 yen (author 2026-11-25).
    out.append({'if': 'var.auto == 1', 'then': mood + [
        {'if': 'var.got > 0', 'then': [{'call': 'win'}, board(PICK + 1, True, True, HIT_STOP)], 'else': [board(PICK + 1, True, True)]}],
        'else': reveal(False)})
    # No notifications from him: the day's own course (his work, his coming home) carries him
    # (author 2026-11-25: "葵の通知はいらないかもな。一日の時間の流れがあるから").
    # The money's high mark since it last grew; half of it gone shows her once.
    out.append({'if': 'gold > var.peak', 'then': [{'set': {v('peak'): 'gold', v('halved'): 0}}]})

    out.append({'set': {v('next'): 'var.after'}})
    out.append({'if': 'var.after == "stop"', 'then': [{'set': {v('auto'): 0, v('next'): '"pick"'}}]})
    out.append({'if': 'var.after == "auto"', 'then': [{'set': {v('auto'): 1, v('next'): '"again"'}}]})
    return out


# Her standing picture on the right changes with what she has sunk into the draws
# (author 2026-11-25: "一定金額を使うと、立ち絵自体が変わる"); her face with each result.
STAGES = [0, 100_000, 1_000_000, 10_000_000]
FACES = ['normal', 'smile', 'surprise', 'trouble', 'tired']


def face_event():
    out = [{'set': {v('stage'): ' + '.join(f'min(1, floor(var.spent / {a}))' for a in STAGES[1:])}},
           # An unset var is none of the faces (it compares equal to neither "" nor nil).
           {'if': ' && '.join(f'var.face != "{fc}"' for fc in FACES), 'then': [{'set': {v('face'): '"normal"'}}]},
           {'if': f'gold < {PRICE}', 'then': [{'set': {v('face'): '"tired"'}}]}]
    for st in range(len(STAGES)):
        body = [{'if': f'var.face == "{fc}"', 'then': [{'image': {'file': f'gal/s{st}_{fc}.jpg', 'fade': 0}}]} for fc in FACES]
        out.append({'if': f'var.stage == {st}', 'then': body})
    return out


def loop_event():
    """Entered with the room: the pick page, the draw again with the same numbers,
    or, left on auto, the next draw (begging Aoi first when the money is out)."""
    cost = f'var.sets * {PRICE}'
    return [
        {'if': 'var.cur == 0', 'then': [{'set': {v('cur'): 1, v('face'): '"normal"'}}]},
        # No title (menus: none): the game keeps its own progress. Every turn writes the autosave,
        # on auto too, so closing the page loses nothing (author 2026-11-25: "毎回保存するか");
        # loading it starts resume.
        {'autosave': 'resume'},
        {'if': 'var.auto == 1', 'then': [
            {'if': f'gold < {cost}', 'then': [{'call': 'beg_any'}]},
            {'call': 'play'},
        ], 'else': [
            {'if': f'var.next == "again" && gold >= {cost} && var.sets > 0', 'then': [{'call': 'play'}], 'else': [
                {'set': {v('pick'): '""'}},
                pick_page(),
                {'if': 'var.pick == "buy"', 'then': [{'call': 'play'}]},
                {'if': 'var.pick == "auto"', 'then': [
                    {'if': 'var.sets == 0', 'then': [{'call': 'random'}]},
                    {'set': {v('auto'): 1}},
                ]},
                {'if': 'var.pick == "beg"', 'then': [{'call': 'beg_any'}, {'set': {v('next'): '"pick"'}}]},
            ]},
        ]},
        to_room(),
    ]


# Aoi Hayase, the project leader of the death-march game, answers her begging:
# polite to the letter and cutting in every word (author 2026-11-25: "紳士に口が悪い"), and he sends it every time.
# She sends a selfie with her ask, and he takes the bait, sharp-tongued as ever (author 2026-11-25:
# "チャットでギャルのバストアップ画像を送って、それに釣られる葵の構図にするか").
BEGS = [
    ('見て見て、今日のわたし', '…写真一枚で私の財布が開くと思われているのが心外です。開きましたが。{grouped(var.lend)}円'),
    ('かわいい？ お金ちょうだい', '質問と請求を一文にまとめる技術、営業部に欲しいです。かわいいのは認めます。{grouped(var.lend)}円'),
    ('ねぇ葵くん、これ見て元気出して', '元気は出ませんでしたが、送金ボタンは押していました。自分が怖いです。{grouped(var.lend)}円'),
    ('自撮りした！ だからお小遣い', '「だから」の使い方が日本語として破綻しています。送りましたけど'),
    ('会議中でしょ？ 癒やしてあげる', '会議中に開いたせいで、上司に画面を見られました。慰謝料をいただきたいくらいです。{grouped(var.lend)}円'),
    ('今日のネイル見て〜。あとお金', 'ネイルより先に目に入る物があるので、ネイルは見ていません。{grouped(var.lend)}円'),
    ('寂しいから写真送るね。あとお金ない', '寂しさを請求書に添付する方、初めてです。効きましたが。{grouped(var.lend)}円'),
    ('この服どう？ 葵くんのお金で買いたいの', '似合っています。くじに使わないと約束できるなら、の話ですが。どうせ使うんでしょう。{grouped(var.lend)}円'),
    ('ちょっと盛れた！ 軍資金ください', '盛れているのは写真で、増えているのはあなたの借金です。{grouped(var.lend)}円'),
    ('これでもダメ？', 'ダメと言える男なら、こんなに残高は減っていません。{grouped(var.lend)}円'),
    ('葵くんにだけ見せる顔', 'その顔を何人に見せたのかは聞かないでおきます。送りました。{grouped(var.lend)}円'),
    ('お仕事がんばってるご褒美♡', 'ご褒美を受け取る側が送金するのは、どういう仕組みでしょうか。{grouped(var.lend)}円'),
    ('ねぇ、既読ついたよね？', '既読をつけた自分を呪っています。写真を開いた指も呪っています。{grouped(var.lend)}円'),
    ('寝る前の一枚。おやすみ、あとお金', '「おやすみ」と「お金」を並べないでください。眠れなくなります。送りました'),
    ('わたしのこと好き？ 写真で答えて', '写真では答えません。送金で答えます。悔しいですが。{grouped(var.lend)}円'),
    ('今日もかわいく生きてる。だから生活費', 'かわいく生きることに、私の給料が必要な理由を論文にまとめてください。{grouped(var.lend)}円'),
    ('ほら、笑顔。お金入ったらもっと笑う', '笑顔の値段を知ってしまいました。思ったより高いですね。{grouped(var.lend)}円'),
    ('ねぇ、この写真待ち受けにしていいよ', '待ち受けにしたら、毎朝自分の弱さと向き合うことになります。送りました'),
    ('まじめな話、お金がない', 'まじめな話に、なぜ自撮りが添付されているのですか。効果は抜群ですが。{grouped(var.lend)}円'),
    ('一億当たったら、もっといい写真撮るね', '一億当たる前に、私の財布の写真を撮ってください。空っぽです。{grouped(var.lend)}円'),
    ('この角度、自信ある', 'その角度で、私の判断力も斜めになりました。{grouped(var.lend)}円'),
    ('ねぇ見た？ 見たならお金', '見ました。見た以上、払うしかない仕組みにいつの間にかなっています。送りました'),
    ('葵くんの部屋で撮ったよ', '私の部屋で撮った写真で、私からお金を取る。よくできた循環ですね。{grouped(var.lend)}円'),
    ('今日もがんばってる葵くんへ', 'がんばっている私から、がんばっていないあなたへ。{grouped(var.lend)}円'),
    ('写真代ってことで！', '写真代にしては高すぎますし、写真にしては可愛すぎます。腹が立ちますね。{grouped(var.lend)}円'),
    ('ねぇ、これで許して？', '何を許すのかは聞きません。聞いたら払えなくなりそうなので。送りました'),
    ('お金ちょうだい（かわいく）', '括弧書きで補足されても困ります。写真の方で十分伝わっていました。{grouped(var.lend)}円'),
    ('この顔で頼んでもダメ？', 'ダメではないのが問題なんです。{grouped(var.lend)}円'),
]


def lend():
    return [{'set': {v('begs'): 'var.begs + 1', v('lend'): '(rand(11) + 25) * 10000', v('bv'): f'rand({len(BEGS)})',
                     v('sv'): f'rand({SELFIES}) + 1'}},
            {'set': {v('borrowed'): 'var.borrowed + var.lend'}}]


def beg_any_event():
    """In person while he is home, else by chat (by itself on auto). Broke, she shows first."""
    # Always by chat: a talk in person stopped the play (author 2026-11-25: "葵とギャルの会話いらないかも。
    # チャットで十分。プレイが止まるから").
    return [{'if': 'var.auto == 1', 'then': [{'call': 'beg_quick'}], 'else': [{'call': 'beg'}]}]


SELFIES = 9  # game/assets/selfies/<n>.jpg, her chest showing (tools/chat_selfies.py; author 2026-11-26)


def beg_msgs():
    """Her ask, her selfie, his reply and the transfer: one screen. Only the rows whose when
    holds show, so each group lists every variant in the order they appear."""
    msgs = [{'day': '今日'}]
    for i, (ask, _) in enumerate(BEGS):
        msgs.append({'mine': True, 'text': ask, 'read': True, 'when': f'var.bv == {i}'})
    for n in range(1, SELFIES + 1):
        msgs.append({'mine': True, 'picture': f'selfies/{n}.jpg', 'read': True, 'when': f'var.sv == {n}'})
    for i, (_, reply) in enumerate(BEGS):
        msgs.append({'from': '早瀬 葵', 'icon': 'icons/hayase.png', 'text': reply, 'when': f'var.bv == {i}'})
    msgs.append({'from': '早瀬 葵', 'icon': 'icons/hayase.png', 'text': '［送金 {grouped(var.lend)}円］'})
    return msgs


def beg_event():
    return lend() + [
        # The whole exchange at once, held for reading, a press closes it (auto: one screen of chat).
        {'phone': {'app': 'chat', 'title': '葵くん', 'auto': True, 'messages': beg_msgs()}},
        {'gold': 'var.lend'}, {'sfx': 'heal'}, {'set': {v('peak'): 'gold', v('halved'): 0}},
    ]


def beg_quick_event():
    """On auto, the same chat plays out by itself (author 2026-11-25: "自動で男にチャットして資金補充")."""
    return lend() + [
        {'phone': {'app': 'chat', 'title': '葵くん', 'auto': True, 'messages': beg_msgs()}},
        {'gold': 'var.lend'}, {'sfx': 'heal'}, {'set': {v('peak'): 'gold', v('halved'): 0}},
    ]


def main():
    os.makedirs(os.path.join(GAME, 'data'), exist_ok=True)
    game = {
        'schema_version': 11, 'id': 'lottery6', 'title': 'lottery6',
        # No title screen (author 2026-11-25: "タイトル画面いらないかもな"): the play starts from the
        # newest save, or a new game. Settings stay on their key.
        'menus': 'none',
        # The page's share card and home-screen icon (author 2026-11-25: "ゲームのOGP画像は欲しい").
        # og:image needs the page's public URL (WEB_URL).
        'web': dict({'description': 'A number lottery: just pick 6 of 43. Out of money? Ask Aoi.',
                     'icon': 'web/icon.png'}, **({'url': WEB_URL, 'image': 'web/ogp.png'} if WEB_URL else {})),
        # Japanese unless the player's browser asks for English (as Succubus Live; author 2026-11-25),
        # written in Japanese; the pick page switches (lang/en.yaml from tools/en.py).
        'language': 'ja', 'written_in': 'ja', 'languages': ['ja', 'en'], 'screen': {'width': 1920, 'height': 1080, 'adapt': True},  # upright only on a phone held upright (author 2026-11-25)
        'fonts': {'regular': 'fonts/mplus-1p-regular.ttf'},
        'start': {'location': 'room', 'gold': 30000, 'event': 'opening'},
        'terms': {'currency': '円'},
        'ui': {'auto_read': True, 'auto_wait': 4,
               'window': '#141a20e8', 'border': '#7fb0c8', 'text': '#f4f7f9', 'accent': '#ffd35a', 'cursor': '#9cc8dc',
               # The title is one finished picture: the gal smiling at a win on her phone (author 2026-11-25).
               'title': {'background': 'scenes/jackpot_1_night.jpg'},
               'battle_ai_history': False,
               'phone': dict(PALETTE)},
    }
    events = {
        'opening': [
            {'set': {v('cur'): 1, v('next'): '"pick"', v('auto'): 0, v('begs'): 0, v('face'): '"normal"',
                     'var.clock_minutes': START_MINUTES, v('met'): 0, v('borrowed'): 0, v('mcool'): 0,
                     v('peak'): 30000, v('halved'): 0}},
            # The game starts on the phone: the opening is a chat, her line with a photo of her and a
            # ticket (author 2026-11-25: "オープニング、いきなりスマホでいいのでは"
            # "チャットで一枚絵を見せるか").
            {'phone': {'app': 'chat', 'title': '葵くん', 'auto': True, 'messages': [
                {'day': '今日'},
                {'mine': True, 'text': '当てるぞ！一億！', 'read': True},
                {'mine': True, 'picture': 'selfies/opening.jpg', 'read': True},
                {'from': '早瀬 葵', 'icon': 'icons/hayase.png', 'text': 'そのお金、出どころは私の財布ですよね。'},
            ]}},
        ],
        'loop': loop_event(),
        # the next of the game's languages: the one button switches between them
        'switch_language': [{'language': 'next'}],
        # Back from a save: at the pick page, auto off (the player was away).
        'resume': [{'set': {v('auto'): 0, v('next'): '"pick"'}}, {'call': 'loop'}],
        'beg_any': beg_any_event(),

        'play': play_event(),
        'win': win_event(),
        'clear': clear_event(),
        'slots': slots_event(),
        'random': random_event(),
        **({'random_all': random_all_event()} if SETS > 1 else {}),
        'beg': beg_event(),
        'beg_quick': beg_quick_event(),
    }
    for n in range(1, N + 1):
        events[f'key_{n}'] = key_event(n)
    world = {
        # The gyaru has no name, as in Rabbit Run and Succubus Live (author 2026-11-25: 名前を付けない).
        'actors': {'gyal': {'name': 'ギャル'}, 'aoi': {'name': '早瀬 葵'}},
        'locations': {k: {'name': '葵くんの部屋', 'background': bg, 'safe': True, 'bare': True,
                          'on_enter': [{'call': 'loop'}]} for k, bg in ROOMS.items()},
        # No music, the sounds only (author 2026-11-25: "音楽いらんかもな。効果音だけで。画面をまじめに見る人いないと思う");
        # the sounds come from 忘却のネーヴェ (~/Desktop/rpg, numpy-made).
        'events': events,
    }
    from en import EN
    os.makedirs(os.path.join(GAME, 'lang'), exist_ok=True)
    with open(os.path.join(GAME, 'lang', 'en.yaml'), 'w') as f:
        f.write('# Generated by tools/build.py from tools/en.py.\n' + json.dumps({'text': EN}, ensure_ascii=False, indent=1) + '\n')
    with open(os.path.join(GAME, 'game.yaml'), 'w') as f:
        f.write('# Generated by tools/build.py.\n' + json.dumps(game, ensure_ascii=False, indent=1) + '\n')
    with open(os.path.join(GAME, 'data', 'world.yaml'), 'w') as f:
        f.write('# Generated by tools/build.py.\n' + json.dumps(world, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    main()
