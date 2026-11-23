# 하우머치노트 썸네일(1200x675) 생성
# python3 tools/thumb.py src/images/{slug}/01.jpg --cat money --hook "궁금증 한 줄" --kw "큰 키워드" --num "핵심 숫자 배지"
# --kw 안의 "|"는 줄바꿈. --cat: money, family, home, living, study
import argparse, glob, os
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--cat', default='money')
ap.add_argument('--hook', default=''); ap.add_argument('--kw', required=True); ap.add_argument('--num', default='')
a = ap.parse_args()

W, H = 1200, 675
NAVY, NAVY2, BLUE = (13, 34, 58), (24, 62, 104), (47, 111, 171)
YEL, GRN, WHITE, SUB = (255, 210, 51), (16, 160, 120), (255, 255, 255), (178, 198, 222)
BLACK = glob.glob('/usr/share/fonts/**/NotoSansCJK-Black.ttc', recursive=True)[0]
BOLD = (glob.glob('/usr/share/fonts/**/NotoSansCJK-Bold.ttc', recursive=True) or [BLACK])[0]
F = lambda s, p=BLACK: ImageFont.truetype(p, s, index=1)

im = Image.new('RGB', (W, H), NAVY)
d = ImageDraw.Draw(im)
for y in range(H):  # 위→아래 그라데이션
    t = y / H
    d.line([(0, y), (W, y)], fill=tuple(int(NAVY2[i] * (1 - t) + NAVY[i] * t) for i in range(3)))
for r, al in [(330, 40), (250, 60)]:  # 왼쪽 원형 무대
    ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
    od.ellipse([250 - r, 360 - r, 250 + r, 360 + r], fill=BLUE + (al,))
    im.paste(ov, (0, 0), ov)
d = ImageDraw.Draw(im)

# ---- 카테고리 아이콘 (중심 250,360) ----
cx, cy = 250, 360
def won(x, y, s, col=NAVY):
    d.text((x, y), '₩', font=F(s), fill=col, anchor='mm')
if a.cat == 'money':  # 동전 더미 + 앞 동전
    for i in range(5):
        y = cy + 95 - i * 34
        d.ellipse([cx - 165, y - 30, cx - 15, y + 30], fill=(214, 160, 20), outline=NAVY, width=5)
        d.ellipse([cx - 165, y - 42, cx - 15, y + 18], fill=YEL, outline=NAVY, width=5)
    d.ellipse([cx - 20, cy - 70, cx + 170, cy + 120], fill=YEL, outline=NAVY, width=7)
    d.ellipse([cx + 2, cy - 48, cx + 148, cy + 98], outline=(214, 160, 20), width=6)
    won(cx + 75, cy + 22, 110)
elif a.cat == 'family':  # 케이크
    d.rounded_rectangle([cx - 150, cy + 10, cx + 150, cy + 140], 18, fill=(255, 236, 214), outline=NAVY, width=6)
    d.rounded_rectangle([cx - 110, cy - 90, cx + 110, cy + 16], 16, fill=(255, 196, 214), outline=NAVY, width=6)
    for x in range(cx - 130, cx + 131, 52):
        d.ellipse([x - 20, cy - 2, x + 20, cy + 34], fill=WHITE, outline=NAVY, width=4)
    d.rounded_rectangle([cx - 10, cy - 170, cx + 10, cy - 90], 6, fill=WHITE, outline=NAVY, width=4)
    d.ellipse([cx - 22, cy - 230, cx + 22, cy - 168], fill=YEL, outline=NAVY, width=4)
    d.text((cx, cy + 80), '1', font=F(70), fill=(230, 90, 120), anchor='mm')
elif a.cat == 'home':  # 집
    d.polygon([(cx - 175, cy - 10), (cx, cy - 175), (cx + 175, cy - 10)], fill=(232, 96, 76), outline=NAVY)
    d.rectangle([cx - 135, cy - 15, cx + 135, cy + 150], fill=(255, 243, 222), outline=NAVY, width=6)
    d.rectangle([cx - 30, cy + 50, cx + 30, cy + 150], fill=(150, 98, 60), outline=NAVY, width=5)
    for x in (cx - 105, cx + 50):
        d.rectangle([x, cy + 20, x + 55, cy + 72], fill=(160, 210, 255), outline=NAVY, width=5)
    d.ellipse([cx + 70, cy - 150, cx + 190, cy - 30], fill=YEL, outline=NAVY, width=6); won(cx + 130, cy - 88, 70)
elif a.cat == 'study':  # 책 + 학사모
    d.polygon([(cx - 170, cy - 40), (cx, cy - 10), (cx, cy + 150), (cx - 170, cy + 120)], fill=WHITE, outline=NAVY)
    d.polygon([(cx + 170, cy - 40), (cx, cy - 10), (cx, cy + 150), (cx + 170, cy + 120)], fill=(226, 236, 250), outline=NAVY)
    for i in range(4):
        y = cy + 20 + i * 26
        d.line([(cx - 140, y - 20 + i * 2), (cx - 30, y + i * 2)], fill=SUB, width=5)
    d.polygon([(cx - 140, cy - 120), (cx, cy - 180), (cx + 140, cy - 120), (cx, cy - 60)], fill=(40, 48, 70), outline=NAVY)
    d.line([(cx + 100, cy - 125), (cx + 100, cy - 70)], fill=YEL, width=6); d.ellipse([cx + 88, cy - 80, cx + 112, cy - 56], fill=YEL)
else:  # living: 영수증
    d.polygon([(cx - 120, cy - 170), (cx + 120, cy - 170), (cx + 120, cy + 150)] +
              [(cx + 120 - i * 30, cy + 150 + (15 if i % 2 else 0)) for i in range(1, 9)] + [(cx - 120, cy + 150)], fill=WHITE, outline=NAVY)
    for i in range(4):
        d.rounded_rectangle([cx - 85, cy - 120 + i * 48, cx + (85 if i % 2 else 40), cy - 100 + i * 48], 8, fill=SUB)
    d.ellipse([cx + 30, cy + 20, cx + 190, cy + 180], fill=YEL, outline=NAVY, width=7); won(cx + 110, cy + 100, 95)

# ---- 오른쪽 글자 ----
X0, X1 = 520, 1150
maxw = X1 - X0
def fitw(text, start, minimum, w, path=BLACK):
    s = start
    while s > minimum and d.textlength(text, font=F(s, path)) > w: s -= 2
    return F(s, path)
lines = a.kw.split('|')
size = 170 if len(lines) == 1 else 140
while any(d.textlength(l, font=F(size)) > maxw for l in lines) and size > 70: size -= 4
fk = F(size); lh = size * 1.12
hook_h = 64 if a.hook else 0
pill_h = 110 if a.num else 0
block = hook_h + len(lines) * lh + pill_h
y = 360 - block / 2 + 10
if a.hook:
    f = fitw(a.hook, 48, 30, maxw, BOLD); d.text((X0, y + 24), a.hook, font=f, fill=WHITE, anchor='lm'); y += hook_h
for i, l in enumerate(lines):  # 노란 키워드 + 남색 그림자
    yy = y + lh / 2 + i * lh
    d.text((X0 + 6, yy + 7), l, font=fk, fill=(5, 16, 30), anchor='lm')
    d.text((X0, yy), l, font=fk, fill=YEL, anchor='lm')
y += len(lines) * lh
if a.num:
    fn = fitw(a.num, 46, 26, maxw - 56)
    tw = d.textlength(a.num, font=fn); py = y + 60
    d.rounded_rectangle([X0, py - 40, X0 + tw + 56, py + 40], 40, fill=GRN)
    d.text((X0 + 28, py), a.num, font=fn, fill=WHITE, anchor='lm')

# ---- 브랜드 ----
d.rounded_rectangle([40, 30, 82, 72], 10, fill=YEL); d.text((61, 51), '₩', font=F(30), fill=NAVY, anchor='mm')
d.text((94, 51), '하우머치노트', font=F(28, BOLD), fill=WHITE, anchor='lm')
os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
im.save(a.out, quality=90)
