"""English for lottery6 (author 2026-11-25: "デフォルト英語だが、言語を簡単に日本語切り替えできるようにして欲しい").
The game is written in Japanese (written_in: ja) and shown in English first; tools/build.py writes
these into game/lang/en.yaml. A key is the Japanese text exactly as build.py writes it, {…} and all;
a value may use other expressions than its key.

Aoi stays polite to the letter and cutting in every word, in English too.
"""

L = '{grouped(var.lend)}'
Y = '¥'

EN = {
    # the phone's pages
    '{grouped(gold)}円': Y + '{grouped(gold)}',
    'ランダム': 'Random',
    'クリア': 'Clear',
    '購入する（200円）': 'Buy (¥200)',
    'オート購入': 'Auto buy',
    'オート購入中': 'Auto buying',
    'オートを止める': 'Stop auto',
    '葵くんにせびる': 'Ask Aoi for money',
    '累計 {grouped(var.draws)}口': '{grouped(var.draws)} tickets',
    '使った額 {grouped(var.spent)}円': Y + '{grouped(var.spent)} spent',
    '当せん累計 {grouped(var.won)}円': Y + '{grouped(var.won)} won in all',
    '第{grouped(var.draws)}回 抽せん': 'Draw #{grouped(var.draws)}',
    '当せん番号（右はボーナス）': 'Winning numbers (bonus on the right)',
    'あなたの番号': 'Your numbers',
    '当せん金': 'Prize',
    '+{grouped(var.got)}円': '+' + Y + '{grouped(var.got)}',
    'はずれ': 'No luck',
    '1等': '1st prize',
    '2等': '2nd prize',
    '3等': '3rd prize',
    '4等': '4th prize',
    '5等': '5th prize',
    '同じ番号でもう一回': 'Same numbers again',
    'この番号でオート': 'Auto with these',
    '番号を選ぶ': 'Pick numbers',
    # the switch shows the other language: "English" in Japanese, "日本語" in English
    'English': '日本語',
    # the chat
    '葵くん': 'Aoi',
    '早瀬 葵': 'Aoi Hayase',
    '今日': 'Today',
    '［送金 {grouped(var.lend)}円］': '[Sent ' + Y + L + ']',
    # people and places
    'ギャル': 'Gyaru',
    '葵くんの部屋': "Aoi's place",
    'lottery6': 'lottery6',
    # the opening chat
    '当てるぞ！一億！': "I'm winning a hundred million!",
    'そのお金、出どころは私の財布ですよね。': 'That money came out of my wallet, I believe.',
    # her asks, with a selfie
    '見て見て、今日のわたし': 'Look at me today',
    'かわいい？ お金ちょうだい': 'Cute? Send money',
    'ねぇ葵くん、これ見て元気出して': 'Aoi, look at this and cheer up',
    '自撮りした！ だからお小遣い': 'Took a selfie! So, allowance',
    '会議中でしょ？ 癒やしてあげる': "You're in a meeting, right? Let me heal you",
    '今日のネイル見て〜。あとお金': 'Look at my nails~ Also money',
    '寂しいから写真送るね。あとお金ない': "I'm lonely so here's a pic. Also I'm broke",
    'この服どう？ 葵くんのお金で買いたいの': 'Like this outfit? I want to buy it with your money',
    'ちょっと盛れた！ 軍資金ください': 'Good angle today! Funding please',
    'これでもダメ？': 'Still no?',
    '葵くんにだけ見せる顔': 'A face only you get to see',
    'お仕事がんばってるご褒美♡': 'A treat for working so hard♡',
    'ねぇ、既読ついたよね？': 'Hey, you read it, right?',
    '寝る前の一枚。おやすみ、あとお金': 'One before bed. Good night, also money',
    'わたしのこと好き？ 写真で答えて': 'Do you like me? Answer with a picture',
    '今日もかわいく生きてる。だから生活費': "Still living cute today. So, living expenses",
    'ほら、笑顔。お金入ったらもっと笑う': "See, a smile. I'll smile more once the money's in",
    'ねぇ、この写真待ち受けにしていいよ': 'You can make this your wallpaper',
    'まじめな話、お金がない': "Seriously, I'm out of money",
    '一億当たったら、もっといい写真撮るね': "When I win a hundred million I'll take better pics",
    'この角度、自信ある': "I'm proud of this angle",
    'ねぇ見た？ 見たならお金': 'Did you see it? If you did, money',
    '葵くんの部屋で撮ったよ': 'Took it at your place',
    '今日もがんばってる葵くんへ': 'To Aoi, working hard again today',
    '写真代ってことで！': "Call it a photo fee!",
    'ねぇ、これで許して？': 'Forgive me with this?',
    'お金ちょうだい（かわいく）': 'Send money (cutely)',
    'この顔で頼んでもダメ？': 'Not even if I ask with this face?',
    # his answers: taken in, and saying so
    '…写真一枚で私の財布が開くと思われているのが心外です。開きましたが。' + L + '円':
        "It's insulting to think one photo opens my wallet. It did, though. " + Y + L,
    '質問と請求を一文にまとめる技術、営業部に欲しいです。かわいいのは認めます。' + L + '円':
        'A question and an invoice in one line. Our sales team could use you. And yes, cute. ' + Y + L,
    '元気は出ませんでしたが、送金ボタンは押していました。自分が怖いです。' + L + '円':
        "I did not cheer up, yet I pressed send. I frighten myself. " + Y + L,
    '「だから」の使い方が日本語として破綻しています。送りましたけど': '"So" does not connect those two things in any language. Sent anyway',
    '会議中に開いたせいで、上司に画面を見られました。慰謝料をいただきたいくらいです。' + L + '円':
        'I opened it in the meeting and my boss saw the screen. I should be the one asking for damages. ' + Y + L,
    'ネイルより先に目に入る物があるので、ネイルは見ていません。' + L + '円':
        'Something else catches the eye before the nails, so I have not looked at the nails. ' + Y + L,
    '寂しさを請求書に添付する方、初めてです。効きましたが。' + L + '円':
        "You are the first person I know to attach loneliness to an invoice. It worked. " + Y + L,
    '似合っています。くじに使わないと約束できるなら、の話ですが。どうせ使うんでしょう。' + L + '円':
        'It suits you, provided it never turns into lottery tickets. It will, won\'t it. ' + Y + L,
    '盛れているのは写真で、増えているのはあなたの借金です。' + L + '円':
        'What looks good is the photo. What grows is your debt. ' + Y + L,
    'ダメと言える男なら、こんなに残高は減っていません。' + L + '円':
        'If I were a man who could say no, my balance would not look like this. ' + Y + L,
    'その顔を何人に見せたのかは聞かないでおきます。送りました。' + L + '円':
        'I will not ask how many people have seen that face. Sent. ' + Y + L,
    'ご褒美を受け取る側が送金するのは、どういう仕組みでしょうか。' + L + '円':
        'Explain how the person getting the treat ends up paying for it. ' + Y + L,
    '既読をつけた自分を呪っています。写真を開いた指も呪っています。' + L + '円':
        'I curse myself for reading it, and the finger that opened the photo. ' + Y + L,
    '「おやすみ」と「お金」を並べないでください。眠れなくなります。送りました':
        'Please do not put "good night" next to "money". I will not sleep now. Sent',
    '写真では答えません。送金で答えます。悔しいですが。' + L + '円':
        'I will not answer with a photo. I will answer with a transfer, much to my regret. ' + Y + L,
    'かわいく生きることに、私の給料が必要な理由を論文にまとめてください。' + L + '円':
        'Please write a paper on why living cute requires my salary. ' + Y + L,
    '笑顔の値段を知ってしまいました。思ったより高いですね。' + L + '円':
        'Now I know what a smile costs. More than I thought. ' + Y + L,
    '待ち受けにしたら、毎朝自分の弱さと向き合うことになります。送りました':
        'As my wallpaper it would show me my own weakness every morning. Sent',
    'まじめな話に、なぜ自撮りが添付されているのですか。効果は抜群ですが。' + L + '円':
        'Why does a serious talk come with a selfie? It works far too well. ' + Y + L,
    '一億当たる前に、私の財布の写真を撮ってください。空っぽです。' + L + '円':
        'Before the hundred million, take a picture of my wallet. It is empty. ' + Y + L,
    'その角度で、私の判断力も斜めになりました。' + L + '円':
        'At that angle my judgment tilted too. ' + Y + L,
    '見ました。見た以上、払うしかない仕組みにいつの間にかなっています。送りました':
        'I saw it. Somehow, seeing it now means paying. Sent',
    '私の部屋で撮った写真で、私からお金を取る。よくできた循環ですね。' + L + '円':
        'You took a photo in my apartment to get money out of me. Very efficient. ' + Y + L,
    'がんばっている私から、がんばっていないあなたへ。' + L + '円':
        'From the one working hard to the one who is not. ' + Y + L,
    '写真代にしては高すぎますし、写真にしては可愛すぎます。腹が立ちますね。' + L + '円':
        'Too expensive for a photo fee, too cute for a photo. It is infuriating. ' + Y + L,
    '何を許すのかは聞きません。聞いたら払えなくなりそうなので。送りました':
        'I will not ask what I am forgiving. If I asked, I might not pay. Sent',
    '括弧書きで補足されても困ります。写真の方で十分伝わっていました。' + L + '円':
        'No need for the parentheses. The photo said it already. ' + Y + L,
    'ダメではないのが問題なんです。' + L + '円':
        'The problem is that it is not a no. ' + Y + L,
}
