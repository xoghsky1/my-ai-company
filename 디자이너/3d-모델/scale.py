import sys
from PIL import Image
import numpy as np
from collections import deque
im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
H, W, _ = im.shape
mx = im.max(2)
wall = mx < 60
# close small gaps (dashed option borders over walls, antialiasing)
def dil(m, k=1):
    o = m.copy()
    for dy in range(-k, k+1):
        for dx in range(-k, k+1):
            o |= np.roll(np.roll(m, dy, 0), dx, 1)
    return o
def ero(m, k=1):
    return ~dil(~m, k)
wallc = ero(dil(wall, 2), 2)
# outside = pure white connected to border
white = im.min(2) > 247
out = np.zeros_like(white)
q = deque()
for x in range(W):
    for y in (0, H-1):
        if white[y, x]: out[y, x] = True; q.append((y, x))
for y in range(H):
    for x in (0, W-1):
        if white[y, x]: out[y, x] = True; q.append((y, x))
while q:
    y, x = q.popleft()
    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
        ny, nx = y+dy, x+dx
        if 0 <= ny < H and 0 <= nx < W and white[ny, nx] and not out[ny, nx]:
            out[ny, nx] = True; q.append((ny, nx))
env = ~out
ys, xs = np.nonzero(wallc)
print('wall bbox', xs.min(), xs.max(), ys.min(), ys.max())
print('env px', env.sum(), 'wall px', wallc.sum())
# horizontal wall thickness samples: left outer wall at row 200
for y in (100, 200, 300, 380):
    row = wallc[y]
    runs=[]; x=0
    while x < W:
        if row[x]:
            s=x
            while x<W and row[x]: x+=1
            runs.append((s,x-s))
        x+=1
    print('row', y, runs)
for x in (100, 250, 420):
    col = wallc[:, x]
    runs=[]; y=0
    while y < H:
        if col[y]:
            s=y
            while y<H and col[y]: y+=1
            runs.append((s,y-s))
        y+=1
    print('col', x, runs)
np.save(sys.argv[2]+'/wall.npy', wallc); np.save(sys.argv[2]+'/env.npy', env)
