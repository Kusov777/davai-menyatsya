# -*- coding: utf-8 -*-
"""Иконка «Давай Меняться» — изящная радужная ладонь с детскими искорками."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT, exist_ok=True)
S = 1024

def hex2rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

# transform из SVG-пространства (100) в пиксели
k = 8.4
cx, cy = 44.25, 52.0
ox = S/2 - cx*k
oy = S/2 - cy*k
def X(x): return ox + x*k
def Y(y): return oy + y*k

# --- маска руки: изящные пальцы (стройнее, мягкий веер) ----------------------
mask = Image.new('L', (S, S), 0)
def add(layer):
    global mask
    mask = ImageChops.lighter(mask, layer)

palm = Image.new('L', (S, S), 0); pd = ImageDraw.Draw(palm)
pd.rounded_rectangle([390, 582, 636, 792], radius=104, fill=255)   # ладонь, чистая округлая
pd.ellipse([352, 656, 486, 800], fill=255)                          # подушечка большого пальца
add(palm)

def finger(bx, by, length, width, angle):
    L = Image.new('L', (S, S), 0); d = ImageDraw.Draw(L)
    d.rounded_rectangle([bx - width/2, by - length, bx + width/2, by + 32],
                        radius=width/2, fill=255)
    L = L.rotate(angle, center=(bx, by), resample=Image.BICUBIC)
    add(L)

#       bx   by   len  wid  angle(+ = наклон влево)  — пальцы стройнее, веер мягче
finger(442, 596, 262, 52,  8)    # указательный
finger(506, 596, 312, 54,  2)    # средний
finger(568, 596, 270, 50, -7)    # безымянный
finger(624, 602, 206, 44, -16)   # мизинец
finger(406, 728, 226, 74, 52)    # большой палец

# --- яркая радужная заливка на всю ладонь (горизонталь) ----------------------
bbox = mask.getbbox()
x0, x1 = bbox[0] - 6, bbox[2] + 6
stops = ['#FF2E63', '#FF7A00', '#FFC400', '#2BD576', '#12A9FF', '#8A4FFF']
N = 600
lut = []
for kk in range(N):
    tt = kk/(N-1); sg = tt*(len(stops)-1); i = min(len(stops)-2, int(sg)); f = sg-i
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

# --- мягкий объём (без «царапин») --------------------------------------------
def soft(box, val, blur):
    g = Image.new('L', (S, S), 0); ImageDraw.Draw(g).ellipse(box, fill=val)
    return ImageChops.darker(g.filter(ImageFilter.GaussianBlur(blur)), mask)
hl = Image.new('RGBA', (S, S), (255, 255, 255, 0)); hl.putalpha(soft([330, 300, 700, 650], 46, 80))
hand = Image.alpha_composite(hand, hl)
sh = Image.new('RGBA', (S, S), (70, 25, 55, 0)); sh.putalpha(soft([340, 680, 690, 880], 58, 80))
hand = Image.alpha_composite(hand, sh)

# --- детские искорки-звёздочки (4 луча, белая сердцевина) ---------------------
def sparkle(x, y, r, color, alpha=255):
    layer = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    i = r*0.16
    pts = [(x, y-r),(x+i, y-i),(x+r, y),(x+i, y+i),(x, y+r),(x-i, y+i),(x-r, y),(x-i, y-i)]
    d.polygon(pts, fill=color+(alpha,))
    d.ellipse([x-r*0.22, y-r*0.22, x+r*0.22, y+r*0.22], fill=(255, 255, 255, 240))
    glow = layer.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(glow, layer)

for (sx, sy, sr, sc) in [
    (770, 300, 46, hex2rgb('#FFC400')),   # золотая, крупная — справа сверху
    (286, 408, 33, hex2rgb('#FF2E63')),   # коралловая — слева у большого
    (590, 150, 25, hex2rgb('#12A9FF')),   # голубая — над средним
    (726, 560, 17, hex2rgb('#2BD576')),   # маленькая зелёная
]:
    hand = Image.alpha_composite(hand, sparkle(sx, sy, sr, sc))

# --- прозрачный логотип (обрезка по всему содержимому, вкл. искорки) ----------
crop = hand.split()[3].getbbox(); pad = 22
box = (max(0, crop[0]-pad), max(0, crop[1]-pad), min(S, crop[2]+pad), min(S, crop[3]+pad))
hand.crop(box).save(os.path.join(OUT, "hand.png"))

# --- иконка с тёплым фоном (для лаунчера/PWA) --------------------------------
def with_bg(size):
    top, bot = hex2rgb('#FFF0D8'), hex2rgb('#FFE0EA')
    bg = Image.new('RGB', (S, S)); bpx = bg.load()
    for yy in range(S):
        c = lerp(top, bot, yy/(S-1))
        for xx in range(S): bpx[xx, yy] = c
    bg = bg.convert('RGBA')
    dd = Image.new('L', (S, S), 0); dd.paste(mask, (0, 24)); dd = dd.filter(ImageFilter.GaussianBlur(22))
    shadow = Image.new('RGBA', (S, S), (110, 70, 50, 0)); shadow.putalpha(dd.point(lambda v: int(v*0.40)))
    bg = Image.alpha_composite(bg, shadow)
    bg = Image.alpha_composite(bg, hand)
    return bg.convert('RGB').resize((size, size), Image.LANCZOS)

with_bg(1024).save(os.path.join(OUT, "icon-1024.png"))
for size, name in [(512,"icon-512.png"),(192,"icon-192.png"),(180,"apple-touch-icon.png"),(96,"favicon-96.png")]:
    with_bg(size).save(os.path.join(OUT, name))

print("OK ->", OUT)
print(sorted(os.listdir(OUT)))
