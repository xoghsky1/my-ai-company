"""평면도 외벽에서 창·현관 같은 개구부를 찾는다 (픽셀 좌표)."""
import sys
import numpy as np
d = sys.argv[1]
wall = np.load(d + '/wall.npy'); env = np.load(d + '/env.npy')
H, W = wall.shape
T = 24
def runs(flags):
    out = []; i = 0
    while i < len(flags):
        if flags[i]:
            s = i
            while i < len(flags) and flags[i]: i += 1
            if i - s >= 6: out.append((s, i - 1))
        i += 1
    return out
res = {}
for side in ('top', 'bottom', 'left', 'right'):
    flags = []; depth = []
    n = W if side in ('top', 'bottom') else H
    for k in range(n):
        line = env[:, k] if side in ('top', 'bottom') else env[k, :]
        wl = wall[:, k] if side in ('top', 'bottom') else wall[k, :]
        if side in ('bottom', 'right'): line = line[::-1]; wl = wl[::-1]
        idx = np.nonzero(line)[0]
        if len(idx) == 0: flags.append(False); depth.append(-1); continue
        s = idx[0]
        if side in ('bottom', 'right'): pos = len(line) - 1 - s
        else: pos = s
        flags.append(not wl[s:s + T].any()); depth.append(pos)
    for a, b in runs(flags):
        res.setdefault(side, []).append((a, b, int(np.median(depth[a:b + 1]))))
for k, v in res.items(): print(k, v)
