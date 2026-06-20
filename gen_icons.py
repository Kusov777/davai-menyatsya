# -*- coding: utf-8 -*-
"""Иконка «Давай Меняться» — реалистичная радужная ладонь (PWA / App Store / Google Play)."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT, exist_ok=True)
S = 1024

def hex2rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# --- маска руки ---------------------------------------------------------------
mask = Image.new('L', (S, S), 0)
md = ImageDraw.Draw(mask)

def add(layer):
    global mask
    mask = ImageChops.lighter(mask, layer)

# ладонь + бугор у основания большого пальца (тенар) — даёт натуральную форму
palm = Image.new('L', (S, S), 0); pd = ImageDraw.Draw(palm)
pd.rounded_rectangle([372, 560, 652, 812], radius=112, fill=255)
pd.ellipse([336, 648, 500, 824], fill=255)          # тенар (подушечка большого)
pd.ellipse([360, 690, 660, 836], fill=255)          # округлая нижняя часть/запястье
add(palm)

# пальцы: основание у ладони, кончики веером (реалистичные пропорции)
def finger(bx, by, length, width, angle):
    L = Image.new('L', (S, S), 0); d = ImageDraw.Draw(L)
    d.rounded_rectangle([bx - width/2, by - length, bx + width/2, by + 36],
                        radius=width/2, fill=255)
    L = L.rotate(angle, center=(bx, by), resample=Image.BICUBIC)
    add(L)

#       bx   by   len  wid  angle(+ = наклон влево)
finger(432, 600, 252, 66,  9)    # указательный
finger(502, 600, 304, 70,  2)    # средний (самый длинный)
finger(570, 600, 264, 64, -7)    # безымянный
finger(628, 606, 198, 56, -17)   # мизинец (короче)
# большой палец — от тенара вверх-влево
finger(404, 732, 232, 86, 52)

# --- яркая радужная заливка на всю ладонь (диагональ, в стиле Авито) ----------
bbox = mask.getbbox()
x0, x1 = bbox[0] - 6, bbox[2] + 6
y0, y1 = bbox[1] - 6, bbox[3] + 6
stops = ['#FF2E63', '#FF7A00', '#FFC400', '#2BD576', '#12A9FF', '#8A4FFF']
def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))
N = 600
lut = []
for k in range(N):
    tt = k/(N-1); sg = tt*(len(stops)-1); i = min(len(stops)-2, int(sg)); f = sg-i
    lut.append(lerp(hex2rgb(stops[i]), hex2rgb(stops[i+1]), f))
grad = Image.new('RGB', (S, S)); gp = grad.load()
span = (x1 - x0)
for x in range(S):
    t = (x - x0)/span
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    col = lut[int(t*(N-1))]
    for y in range(S):
        gp[x, y] = col
hand = grad.convert('RGBA'); hand.putalpha(mask)

# --- объём: верхний блик + нижняя тень внутри руки ---------------------------
def soft(box, val, blur):
    g = Image.new('L', (S, S), 0); ImageDraw.Draw(g).ellipse(box, fill=val)
    return ImageChops.darker(g.filter(ImageFilter.GaussianBlur(blur)), mask)

hl = Image.new('RGBA', (S, S), (255, 255, 255, 0)); hl.putalpha(soft([320, 300, 700, 640], 40, 75))
hand = Image.alpha_composite(hand, hl)
sh = Image.new('RGBA', (S, S), (70, 25, 55, 0)); sh.putalpha(soft([330, 670, 700, 880], 66, 75))
hand = Image.alpha_composite(hand, sh)

# тонкие тёмные «промежутки» между пальцами для читаемости
sep = Image.new('RGBA', (S, S), (0, 0, 0, 0)); sd = ImageDraw.Draw(sep)
for vx in (467, 536, 600):
    sd.line([(vx, 500), (vx, 615)], fill=(80, 40, 50, 42), width=6)
sep = sep.filter(ImageFilter.GaussianBlur(3))
sep.putalpha(ImageChops.darker(sep.split()[3], mask))
hand = Image.alpha_composite(hand, sep)

# --- сохранить прозрачный логотип (обрезанный) -------------------------------
crop = mask.getbbox(); pad = 24
box = (crop[0]-pad, crop[1]-pad, crop[2]+pad, crop[3]+pad)
hand.crop(box).save(os.path.join(OUT, "hand.png"))   # логотип без фона

# --- иконка с тёплым фоном (для лаунчера/PWA) --------------------------------
def with_bg(size):
    top, bot = hex2rgb('#FFF0D8'), hex2rgb('#FFD9E6')
    bg = Image.new('RGB', (S, S)); bpx = bg.load()
    for yy in range(S):
        c = lerp(top, bot, yy/(S-1))
        for xx in range(S): bpx[xx, yy] = c
    bg = bg.convert('RGBA')
    drop = Image.new('RGBA', (S, S), (0, 0, 0, 0)); drop.putalpha(mask)
    sm = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dd = Image.new('L', (S, S), 0); dd.paste(mask, (0, 26)); dd = dd.filter(ImageFilter.GaussianBlur(22))
    shadow = Image.new('RGBA', (S, S), (110, 70, 50, 0)); shadow.putalpha(dd.point(lambda v: int(v*0.45)))
    bg = Image.alpha_composite(bg, shadow)
    bg = Image.alpha_composite(bg, hand)
    return bg.convert('RGB').resize((size, size), Image.LANCZOS)

with_bg(1024).save(os.path.join(OUT, "icon-1024.png"))
for size, name in [(512,"icon-512.png"),(192,"icon-192.png"),(180,"apple-touch-icon.png"),(96,"favicon-96.png")]:
    with_bg(size).save(os.path.join(OUT, name))

print("OK ->", OUT)
print(sorted(os.listdir(OUT)))
