# -*- coding: utf-8 -*-
"""Генератор иконки-ладони «Давай Меняться» для PWA / App Store / Google Play."""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT, exist_ok=True)

S = 1024  # мастер-размер

# transform из SVG-пространства (100 units) в пиксели
k = 8.4
cx, cy = 44.25, 52.0
ox = S/2 - cx*k
oy = S/2 - cy*k
def X(x): return ox + x*k
def Y(y): return oy + y*k

def rrect(draw, x, y, w, h, r, fill):
    draw.rounded_rectangle([X(x), Y(y), X(x+w), Y(y+h)], radius=r*k, fill=fill)

def hex2rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))

# фон-градиент (тёплый), полный bleed -> подходит для maskable и any
top = hex2rgb('#FFF0D8'); bot = hex2rgb('#FFD9E6')
bg = Image.new('RGB', (S, S))
bgpx = bg.load()
for yy in range(S):
    t = yy/(S-1)
    col = tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3))
    for xx in range(S):
        bgpx[xx, yy] = col

img = bg.convert('RGBA')
d = ImageDraw.Draw(img)

# мягкая тень под ладонью
shadow = Image.new('RGBA', (S, S), (0,0,0,0))
ds = ImageDraw.Draw(shadow)
ds.ellipse([X(26), Y(78), X(78), Y(96)], fill=(120,80,40,55))
from PIL import ImageFilter
shadow = shadow.filter(ImageFilter.GaussianBlur(18))
img = Image.alpha_composite(img, shadow)
d = ImageDraw.Draw(img)

# ладонь
rrect(d, 30, 45, 44, 44, 17, hex2rgb('#FFB36B'))
# 4 пальца
rrect(d, 33, 22, 9, 40, 4.5, hex2rgb('#FF5D73'))   # красный
rrect(d, 45, 15, 9, 47, 4.5, hex2rgb('#FFD23F'))   # жёлтый
rrect(d, 57, 19, 9, 43, 4.5, hex2rgb('#3DD68C'))   # зелёный
rrect(d, 68, 27, 8.5, 35, 4.2, hex2rgb('#4CC2FF')) # голубой

# большой палец — на отдельном слое с поворотом вокруг (22,53)
thumb = Image.new('RGBA', (S, S), (0,0,0,0))
dt = ImageDraw.Draw(thumb)
dt.rounded_rectangle([X(18), Y(40), X(27), Y(67)], radius=4.5*k, fill=hex2rgb('#A06CFF'))
pivot = (X(22), Y(53))
thumb = thumb.rotate(-38, center=pivot, resample=Image.BICUBIC, expand=False)
img = Image.alpha_composite(img, thumb)

img = img.convert('RGB')

# мастер + производные размеры
img.save(os.path.join(OUT, "icon-1024.png"))
for size, name in [(512,"icon-512.png"),(192,"icon-192.png"),(180,"apple-touch-icon.png"),(96,"favicon-96.png")]:
    img.resize((size,size), Image.LANCZOS).save(os.path.join(OUT, name))

print("OK ->", OUT)
print(os.listdir(OUT))
