"""확장형 평면도(59A_확장형_평면도.png)의 축척을 기본형 평면도로 잡는다.

전용면적 59.83㎡는 발코니를 뺀 면적이다. 확장형 그림에는 확장한 발코니가 집 안으로 들어와 있어
전용면적에 바로 맞추면 집이 작게 나온다. 그래서
1) 원본의 기본형 그림에서 외곽(벽 포함)과 발코니·실외기실 영역을 찾고,
2) 발코니를 뺀 영역을 벽 중심선까지 줄여 59.83㎡에 맞춘 축척(기본형 m/px)을 구한 뒤,
3) 기본형·확장형 외곽 면적 비(같은 건물 외곽)로 확장형 그림의 축척으로 옮긴다.

실행: python scale_basic.py  (env.npy가 있어야 한다: scale.py 먼저)
"""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

here = Path(__file__).parent
EXCLUSIVE_AREA = 59.83
BASIC_CROP = (560, 405, 900, 735)      # 원본에서 기본형 평면도 자리 (px)
BALCONY_SEEDS = [(28, 110), (250, 150), (285, 30)]   # 자른 그림 안의 발코니2·발코니1·실외기실 바닥 (y, x)

im = np.asarray(Image.open(here / '../../자료/59A_평면안내_원본.png').convert('RGB').crop(BASIC_CROP)).astype(int)
H, W, _ = im.shape


def flood(start, ok):
    m = np.zeros((H, W), bool)
    q = deque(start)
    for p in start:
        m[p] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and ok[ny, nx] and not m[ny, nx]:
                m[ny, nx] = True
                q.append((ny, nx))
    return m


def erode(m, k):
    o = m.copy()
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            o &= np.roll(np.roll(m, dy, 0), dx, 1)
    return o


white = im.min(2) > 247
border = [(y, x) for x in range(W) for y in (0, H - 1) if white[y, x]] + [(y, x) for y in range(H) for x in (0, W - 1) if white[y, x]]
env_basic = ~flood(border, white)
floor = (im.max(2) >= 200) & env_basic
balcony = flood(BALCONY_SEEDS, floor)

env_ext = np.load(here / 'env.npy')
k = (env_basic.sum() / env_ext.sum()) ** 0.5     # 기본형 px / 확장형 px
for e in (2, 3):                                 # 벽 두께 절반 (기본형 그림 기준 2~3px)
    m_basic = (EXCLUSIVE_AREA / erode(env_basic & ~balcony, e).sum()) ** 0.5
    print(f'중심선 {e}px: 확장형 축척 {m_basic * k * 100:.3f} cm/px')
print(f'발코니 비율 {balcony.sum() / env_basic.sum():.3f} → build_model.py의 M은 두 값의 가운데(약 2.00 cm/px)')
