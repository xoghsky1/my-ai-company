"""59㎡A 확장형 평면도 이미지에서 3D 모델 데이터(model.json)를 만든다.

모든 치수는 추정이다. 평면도 이미지의 축척을 전용면적 59.83㎡에 맞춰 잡았다.
실측 치수가 들어오면 이 스크립트의 결과 대신 실측값으로 바꾼다.

실행: python build_model.py  (scale.py로 wall.npy, env.npy를 먼저 만든다)
"""
import json
from collections import deque

import numpy as np

wall = np.load('wall.npy')
env = np.load('env.npy')
H, W = wall.shape

# 옵션 표시(갈색 점선, 숫자 상자)가 외벽 위에 겹쳐 벽이 끊겨 보이는 곳을 메운다.
from PIL import Image  # noqa: E402
_rgb = np.asarray(Image.open('../../자료/59A_확장형_평면도.png').convert('RGB')).astype(int)
_brown = (_rgb.max(2) - _rgb.min(2) > 40) & (_rgb[..., 0] > _rgb[..., 1]) & (_rgb[..., 1] > _rgb[..., 2])
wall[:, 14:24] |= _brown[:, 14:24] & env[:, 14:24]   # 왼쪽 외벽
wall[15:28, 14:56] = True                             # 왼쪽 위 '1' 표시 상자 자리의 외벽
wall[12:60, 17:24] = True
wall[15:28, 302:360] = True                           # 오른쪽 위 '3' 표시 상자 자리의 외벽
wall[15:40, 335:350] = True


def drop_small(mask, min_px=150):
    """방 이름 글자·화살표·문짝 선처럼 작은 검은 덩어리는 벽이 아니므로 지운다."""
    seen = np.zeros_like(mask)
    out = mask.copy()
    h, w = mask.shape
    for sy, sx in zip(*np.nonzero(mask)):
        if seen[sy, sx]:
            continue
        seen[sy, sx] = True
        q, pts = deque([(sy, sx)]), []
        while q:
            y, x = q.popleft()
            pts.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if len(pts) < min_px:
            for y, x in pts:
                out[y, x] = False
    return out


wall = drop_small(wall)

EXCLUSIVE_AREA = 59.83  # ㎡, 주거전용면적 (분양 홈페이지)
WALL_H = 2.3            # m, 추정 (천장고 확인 필요)
HEAD_H = 2.1            # m, 창·문 윗선 추정


def erode(m, k):
    o = m.copy()
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            o &= np.roll(np.roll(m, dy, 0), dx, 1)
    return o


# 1. 축척: 발코니·실외기실(왼쪽 아래)을 뺀 외곽을 벽 중심선까지 줄여 전용면적에 맞춘다.
yy, xx = np.mgrid[0:H, 0:W]
service = (yy >= 413) & (xx <= 190)
main = env & ~service
centerline = erode(main, 4)
M = (EXCLUSIVE_AREA / centerline.sum()) ** 0.5  # m/px
print(f'축척 {M * 100:.2f} cm/px, 외곽 {W * M:.2f} x {H * M:.2f} m')

ys, xs = np.nonzero(env)
X0, Y0 = xs.min(), ys.min()


def m(x, y):
    return round((x - X0) * M, 3), round((y - Y0) * M, 3)


# 2. 벽: 2px 격자로 줄인 뒤 가로 줄을 세로로 합쳐 직사각형으로 만든다.
C = 2
gw = wall[: H // C * C, : W // C * C].reshape(H // C, C, W // C, C).mean((1, 3)) > 0.5
rects = []
open_runs = {}
for gy in range(gw.shape[0] + 1):
    row_runs = set()
    if gy < gw.shape[0]:
        gx = 0
        while gx < gw.shape[1]:
            if gw[gy, gx]:
                s = gx
                while gx < gw.shape[1] and gw[gy, gx]:
                    gx += 1
                row_runs.add((s, gx))
            gx += 1
    for run in list(open_runs):
        if run not in row_runs:
            rects.append((run[0], open_runs.pop(run), run[1], gy))
    for run in row_runs:
        open_runs.setdefault(run, gy)
walls = []
for x0, y0, x1, y1 in rects:
    ax, ay = m(x0 * C, y0 * C)
    bx, by = m(x1 * C, y1 * C)
    walls.append([ax, ay, bx, by])

# 3. 창·문 (평면도 픽셀 좌표 x0, y0, x1, y1 / 바닥에서 창틀까지 높이 / 종류). 위치는 평면도에서 읽음, 높이는 추정.
OPENINGS = [
    (55, 15, 122, 28, 0.9, 'window', '옷방 창'),
    (188, 15, 241, 28, 1.0, 'window', '주방 창'),
    (261, 15, 301, 28, 1.0, 'window', '다용도실 창'),
    (365, 137, 408, 152, 0.0, 'door', '현관문'),
    (212, 445, 334, 461, 0.2, 'window', '거실 창'),
    (386, 445, 454, 461, 0.9, 'window', '아기방 창'),
    (104, 410, 182, 432, 0.0, 'window', '안방-발코니 창'),
    (106, 480, 170, 494, 0.9, 'window', '발코니 창'),
    (40, 480, 80, 494, 0.1, 'louver', '실외기실 루버'),
]
openings = []
for x0, y0, x1, y1, sill, kind, name in OPENINGS:
    ax, ay = m(x0, y0)
    bx, by = m(x1, y1)
    openings.append({'name': name, 'kind': kind, 'rect': [ax, ay, bx, by], 'sill': sill, 'head': HEAD_H})

# 4. 방: 이름표 위치에서 벽이 아닌 칸으로 동시에 퍼져 나가 방 영역을 나눈다 (문틈에서는 대략 나뉜다).
ROOMS = [
    ('옷방', '침실3', 87, 97),
    ('욕실2', '욕실2', 60, 237),
    ('안방', '침실1', 103, 343),
    ('주방/식당', '주방/식당', 262, 168),
    ('다용도실', '다용도실', 293, 83),
    ('현관', '현관', 385, 177),
    ('욕실1', '욕실1', 447, 237),
    ('거실', '거실', 272, 347),
    ('아기방', '침실2', 425, 347),
    ('실외기실', '실외기실', 62, 457),
    ('발코니', '발코니', 142, 457),
    ('복도', '', 120, 220),
]
# 문턱·개방된 경계에 긋는 방 나눔선 (평면도 픽셀 좌표 x0, y0, x1, y1). 벽은 아니고 바닥 구분용이다.
DIVIDERS = [
    (95, 163, 150, 167),    # 옷방 | 복도
    (95, 270, 185, 274),    # 복도 | 안방
    (57, 270, 97, 274),     # 욕실2(안방 욕실) | 안방
    (183, 218, 187, 274),   # 복도 | 주방·거실 쪽
    (150, 258, 360, 262),   # 주방/식당 | 거실
    (246, 12, 250, 110),    # 주방 | 다용도실
    (335, 218, 412, 222),   # 현관 | 홀
    (408, 218, 412, 275),   # 홀 | 욕실1
    (362, 270, 412, 274),   # 홀 | 아기방
    (330, 120, 366, 152),   # 현관 밖 공용복도
]
free = env & ~wall
for x0, y0, x1, y1 in DIVIDERS:
    free[y0:y1, x0:x1] = False
free[:15, :] = False   # 외벽 바깥에 걸친 옵션 점선 띠
free[:, 504:] = False
for o in OPENINGS:  # 창 자리로는 방이 새어 나가지 않게 막는다
    free[o[1]:o[3], o[0]:o[2]] = False
owner = -np.ones((H, W), int)
q = deque()
for i, (_, _, x, y) in enumerate(ROOMS):
    owner[y, x] = i
    q.append((y, x))
while q:
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < H and 0 <= nx < W and free[ny, nx] and owner[ny, nx] < 0:
            owner[ny, nx] = owner[y, x]
            q.append((ny, nx))

rooms = []
for i, (name, plan_name, lx, ly) in enumerate(ROOMS):
    mask = owner[: H // C * C, : W // C * C].reshape(H // C, C, W // C, C)[:, 0, :, 0] == i
    cells = []
    for gy in range(mask.shape[0]):
        gx = 0
        while gx < mask.shape[1]:
            if mask[gy, gx]:
                s = gx
                while gx < mask.shape[1] and mask[gy, gx]:
                    gx += 1
                ax, ay = m(s * C, gy * C)
                bx, by = m(gx * C, (gy + 1) * C)
                cells.append([ax, ay, bx, by])
            gx += 1
    pys, pxs = np.nonzero(owner == i)
    area = (owner == i).sum() * M * M
    bw = max(c[2] for c in cells) - min(c[0] for c in cells)   # 그리는 바닥 칸 기준 외곽 크기
    bd = max(c[3] for c in cells) - min(c[1] for c in cells)
    lx_m, ly_m = m(lx, ly)

    # 이 방에 닿은 벽면: 방 픽셀 바로 옆이 벽인 경계를 이어 선분으로 만든다 (벽 색 칠하기용).
    R = owner == i
    faces = []
    for side, (dy, dx) in {'n': (-1, 0), 's': (1, 0), 'w': (0, -1), 'e': (0, 1)}.items():
        touch = R & np.roll(np.roll(wall, -dy, 0), -dx, 1)
        if side in ('n', 's'):
            for y in range(H):
                xs_ = np.nonzero(touch[y])[0]
                for run in np.split(xs_, np.nonzero(np.diff(xs_) > 1)[0] + 1):
                    if len(run) >= 4:
                        ey = y if side == 'n' else y + 1
                        ax, ay = m(run[0], ey)
                        bx, _ = m(run[-1] + 1, ey)
                        faces.append([ax, ay, bx, ay, side])
        else:
            for x in range(W):
                ys_ = np.nonzero(touch[:, x])[0]
                for run in np.split(ys_, np.nonzero(np.diff(ys_) > 1)[0] + 1):
                    if len(run) >= 4:
                        ex = x if side == 'w' else x + 1
                        ax, ay = m(ex, run[0])
                        _, by = m(ex, run[-1] + 1)
                        faces.append([ax, ay, ax, by, side])

    rooms.append({'name': name, 'planName': plan_name, 'label': [lx_m, ly_m], 'area': round(area, 2),
                  'size': [round(bw, 2), round(bd, 2)], 'cells': cells, 'wallFaces': faces})
    print(f'{name:6s} {area:5.2f}㎡  {bw:.2f} x {bd:.2f} m (안목, 추정)')

# 바닥판: 방 나눔선·문틈까지 집 안 전체를 덮는 바닥 (방 바닥 아래에 깔린다)
inside = env.copy()
inside[:15, :] = False
inside[:, 504:] = False
for x0, y0, x1, y1 in [(330, 0, 366, 152)]:  # 현관 밖 공용복도
    inside[y0:y1, x0:x1] = False
gi = inside[: H // C * C, : W // C * C].reshape(H // C, C, W // C, C)[:, 0, :, 0]
base = []
for gy in range(gi.shape[0]):
    gx = 0
    while gx < gi.shape[1]:
        if gi[gy, gx]:
            s = gx
            while gx < gi.shape[1] and gi[gy, gx]:
                gx += 1
            ax, ay = m(s * C, gy * C)
            bx, by = m(gx * C, (gy + 1) * C)
            base.append([ax, ay, bx, by])
        gx += 1

model = {
    'base': base,
    'title': '산성역 헤리스톤 59㎡A 확장형 (201동 1층)',
    'estimated': True,
    'scaleCmPerPx': round(M * 100, 3),
    'wallHeight': WALL_H,
    'extent': [round((W - X0) * M, 2), round((H - Y0) * M, 2)],
    'walls': walls,
    'openings': openings,
    'rooms': rooms,
}
with open('model.json', 'w', encoding='utf-8') as f:
    json.dump(model, f, ensure_ascii=False, separators=(',', ':'))
# 브라우저에서 파일을 직접 열 때(file://)는 json을 읽을 수 없어서, 스크립트로도 낸다.
with open('model.js', 'w', encoding='utf-8') as f:
    f.write('window.APT_MODEL = ' + json.dumps(model, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(f'벽 {len(walls)}개, 창·문 {len(openings)}개, 방 {len(rooms)}개 → model.json')

if __name__ == '__main__':
    from PIL import Image
    pal = np.array([[230, 120, 120], [120, 200, 230], [240, 200, 90], [150, 220, 120], [200, 140, 230],
                    [240, 160, 60], [90, 160, 230], [250, 230, 150], [230, 150, 200], [160, 160, 160], [120, 220, 200], [255, 120, 40]])
    for x0, y0, x1, y1 in DIVIDERS:
        pass
    img = np.full((H, W, 3), 255, np.uint8)
    for i in range(len(ROOMS)):
        img[owner == i] = pal[i]
    img[wall] = 0
    for o in OPENINGS:
        img[o[1]:o[3], o[0]:o[2]] = [0, 120, 255]
    for x0, y0, x1, y1 in DIVIDERS:
        img[y0:y1, x0:x1] = [255, 0, 0]
    Image.fromarray(img).resize((W * 2, H * 2), Image.NEAREST).save('debug_rooms.png')
