// 배치 검사기 (QA). 뷰어 페이지 안에서 실행해 지금 보이는 배치를 기획서 평가 기준 K1~K6으로 판정한다.
// 기준: PM/2026-10-12-3단계-배치3안-기획서.md
// 사용: 페이지에서 이 파일 내용을 실행한 뒤 checkLayout() → 결과 객체
function checkLayout() {
  const v = window.__viewer
  const M = window.APT_MODEL
  const I = window.APT_INTERIOR
  const st = v.state
  const items = I.furniture.filter(f => st.furniture[f.id].visible)
  const floorItems = items.filter(f => v.onFloor(f.id))
  const fp = id => v.footprint(id)
  const gapOf = (a, b) => Math.max(0, Math.max(a[0] - b[2], b[0] - a[2]), Math.max(a[1] - b[3], b[1] - a[3]))
  const r2 = n => Math.round(n * 100) / 100
  const overlap = (a, b, tol = 0.005) => a[0] < b[2] - tol && a[2] > b[0] + tol && a[1] < b[3] - tol && a[3] > b[1] + tol
  // 지나갈 수 없는 창·루버 (창턱이 있는 것). 현관문과 바닥까지 내려온 창(안방→발코니)은 지나갈 수 있다
  const blockingOpenings = M.openings.filter(o => o.kind !== 'door' && o.sill > 0.05).map(o => o.rect)
  const solids = [...M.walls, ...blockingOpenings]

  // K1 겹침
  const k1 = []
  for (const f of floorItems) {
    if (v.hitsWall(f.id)) k1.push(`${f.name}: 벽과 겹침`)
    for (const other of v.hitsFurniture(f.id)) if (f.name < other) k1.push(`${f.name} ↔ ${other}`)
  }

  // K2 동선: 5cm 격자, 장애물에서 r만큼 떨어진 칸만 걸을 수 있다 (폭 2r)
  const G = 0.05
  const nx = Math.ceil(M.extent[0] / G) + 1, ny = Math.ceil(M.extent[1] / G) + 1
  const idx = (i, j) => j * nx + i
  const inside = new Uint8Array(nx * ny)
  const mark = (arr, [x0, y0, x1, y1], val) => {
    for (let j = Math.max(0, Math.floor(y0 / G)); j <= Math.min(ny - 1, Math.ceil(y1 / G)); j++)
      for (let i = Math.max(0, Math.floor(x0 / G)); i <= Math.min(nx - 1, Math.ceil(x1 / G)); i++) {
        const cx = i * G, cy = j * G
        if (cx >= x0 && cx <= x1 && cy >= y0 && cy <= y1) arr[idx(i, j)] = val
      }
  }
  for (const c of M.base) mark(inside, c, 1)
  const blocked = new Uint8Array(nx * ny)
  for (let k = 0; k < blocked.length; k++) blocked[k] = inside[k] ? 0 : 1
  for (const s of solids) mark(blocked, s, 1)
  for (const f of floorItems) mark(blocked, fp(f.id), 1)
  function walkable(r) {
    const R = Math.round(r / G)
    const ok = new Uint8Array(nx * ny)
    for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
      if (blocked[idx(i, j)]) continue
      let clear = true
      for (let dj = -R; dj <= R && clear; dj++) for (let di = -R; di <= R; di++) {
        if (di * di + dj * dj > R * R) continue
        const a = i + di, b = j + dj
        if (a < 0 || b < 0 || a >= nx || b >= ny || blocked[idx(a, b)]) { clear = false; break }
      }
      ok[idx(i, j)] = clear ? 1 : 0
    }
    return ok
  }
  function reach(ok) {
    const start = M.rooms.find(r => r.name === '현관')
    // 현관 칸 중 걸을 수 있는 아무 칸에서 출발
    const seen = new Uint8Array(nx * ny)
    const q = []
    for (const c of start.cells) {
      for (let j = Math.ceil(c[1] / G); j <= Math.floor(c[3] / G); j++)
        for (let i = Math.ceil(c[0] / G); i <= Math.floor(c[2] / G); i++)
          if (ok[idx(i, j)] && !seen[idx(i, j)]) { seen[idx(i, j)] = 1; q.push(idx(i, j)) }
    }
    while (q.length) {
      const k = q.pop(), i = k % nx, j = (k - i) / nx
      for (const [a, b] of [[i + 1, j], [i - 1, j], [i, j + 1], [i, j - 1]]) {
        if (a < 0 || b < 0 || a >= nx || b >= ny) continue
        const n = idx(a, b)
        if (ok[n] && !seen[n]) { seen[n] = 1; q.push(n) }
      }
    }
    const reached = [], missed = []
    for (const room of M.rooms) {
      if (room.name === '현관') continue
      let hit = false
      for (const c of room.cells) {
        for (let j = Math.ceil(c[1] / G); j <= Math.floor(c[3] / G) && !hit; j++)
          for (let i = Math.ceil(c[0] / G); i <= Math.floor(c[2] / G); i++) if (seen[idx(i, j)]) { hit = true; break }
        if (hit) break
      }
      ;(hit ? reached : missed).push(room.name)
    }
    return { reached, missed }
  }
  const miss6 = reach(walkable(0.3)).missed, miss8 = reach(walkable(0.4)).missed
  // 빈 집에서도 못 가는 방(window.__k2base)은 구조상 한계로 따로 둔다
  const base = window.__k2base
  const k2 = base
    ? { '0.6m': miss6.filter(r => !base['0.6m'].includes(r)), '0.8m': miss8.filter(r => !base['0.8m'].includes(r)), '빈집에서도못감': base }
    : { '0.6m': miss6, '0.8m': miss8 }

  // K3 가구 앞 여유: 앞면 쪽으로 몇 m까지 비어 있는지
  const FRONT = { 0: [0, 1], 90: [-1, 0], 180: [0, -1], 270: [1, 0] }   // 앞면이 향하는 평면도 방향
  function freeDepth(id, dir, limit, ignore = []) {
    const [x0, y0, x1, y1] = fp(id)
    const others = floorItems.filter(o => o.id !== id && !ignore.includes(o.id)).map(o => fp(o.id))
    for (let d = 0.05; d <= limit + 1e-9; d += 0.05) {
      const box = dir[0] > 0 ? [x1, y0, x1 + d, y1] : dir[0] < 0 ? [x0 - d, y0, x0, y1] : dir[1] > 0 ? [x0, y1, x1, y1 + d] : [x0, y0 - d, x1, y0]
      if (solids.some(s => overlap(box, s, 0.01)) || others.some(o => overlap(box, o, 0.01))) return r2(d - 0.05)
    }
    return r2(limit)
  }
  const k3 = []
  for (const f of floorItems) {
    if (!f.front) continue
    const need = f.front / 1000
    const rot = ((st.furniture[f.id].rot % 360) + 360) % 360
    if (f.kind === 'bed') {
      // 침대는 긴 변 양옆 중 한쪽 이상. 머리맡 협탁은 통로를 막지 않으므로 뺀다
      const sides = rot % 180 === 0 ? [[0, 1], [0, -1]] : [[1, 0], [-1, 0]]
      const nightstands = floorItems.filter(o => o.id.startsWith('nightstand')).map(o => o.id)
      const depths = sides.map(d => freeDepth(f.id, d, 1.0, nightstands))
      const best = Math.max(...depths)
      // 동침 예외 (PM 결정 2026-10-12): 아기침대가 침대 옆에 붙어 있으면 그쪽을 접근면으로 본다
      const cribBeside = st.furniture.crib?.visible && gapOf(fp(f.id), fp('crib')) < 0.05
      const ok = best >= need - 1e-9 || cribBeside
      k3.push({ 가구: f.name, 기준: need, 실제: best, 양옆: depths, 판정: ok ? (best >= need - 1e-9 ? '통과' : '통과(동침 예외)') : '실패' })
    } else if (f.kind === 'dining') {
      // 식탁: 의자가 놓인 긴 변 양쪽 모두 의자를 뺄 공간 (최소 front, 권장 0.75m)
      const sides = rot % 180 === 0 ? [[0, 1], [0, -1]] : [[1, 0], [-1, 0]]
      const depths = sides.map(d => freeDepth(f.id, d, 1.0))
      const worst = Math.min(...depths)
      k3.push({ 가구: f.name, 기준: need, 권장: 0.75, 실제: worst, 양쪽: depths, 판정: worst >= need - 1e-9 ? (worst >= 0.75 - 1e-9 ? '통과' : '통과(권장 미달)') : '실패' })
    } else {
      const got = freeDepth(f.id, FRONT[rot], Math.max(need, 1.0))
      k3.push({ 가구: f.name, 기준: need, 실제: got, 판정: got >= need - 1e-9 ? '통과' : '실패' })
    }
  }

  // K3b 창가 발판 (QA 토론 추가): 창턱 0.6m 이상 창 앞 0.3m 안에 아이가 밟고 오를 높이(0.3~0.9m)의 물건
  const k3b = []
  for (const o of M.openings.filter(o => o.kind === 'window' && o.sill >= 0.6)) {
    const [x0, y0, x1, y1] = o.rect
    const horizontal = x1 - x0 >= y1 - y0
    const zone = horizontal ? [x0, y0 - 0.3, x1, y1 + 0.3] : [x0 - 0.3, y0, x1 + 0.3, y1]
    for (const f of floorItems) {
      const h = f.size[2] / 1000
      if (h >= 0.3 && h <= 0.9 && f.kind !== 'crib' && !f.builtin && overlap(zone, fp(f.id))) k3b.push(`${o.name} 아래: ${f.name}`)
    }
  }

  // K7 소품 개수 (창호 제외)
  const smalls = items.filter(f => f.group === '소품').map(f => f.name)

  // K4 TV 시청 거리 (TV 중심 ↔ 소파 중심)
  let k4 = '해당 없음 (TV 없음)'
  if (st.furniture.tv?.visible && st.furniture.sofa?.visible) {
    const [tx, ty] = st.furniture.tv.at, [sx, sy] = st.furniture.sofa.at
    const d = r2(Math.hypot(tx - sx, ty - sy))
    k4 = { 거리: d, 기준: '1.8~2.6m', 판정: d >= 1.8 && d <= 2.6 ? '통과' : '실패' }
  }

  // K5 아기침대 안전
  let k5 = '해당 없음'
  if (st.furniture.crib?.visible) {
    const c = fp('crib')
    const gap = (a, b) => Math.max(0, Math.max(a[0] - b[2], b[0] - a[2]), Math.max(a[1] - b[3], b[1] - a[3]))
    const windows = M.openings.filter(o => o.kind === 'window')
    const winGap = r2(Math.min(...windows.map(o => gap(c, o.rect))))
    const tallNear = floorItems.filter(f => f.id !== 'crib' && f.size[2] >= 1200 && gap(c, fp(f.id)) < 0.05).map(f => f.name)
    k5 = { 창까지: winGap, 붙은키큰가구: tallNear, 판정: winGap >= 0.3 && tallNear.length === 0 ? '통과' : '실패' }
  }

  // K6 낮은 창(창턱 0.3m 이하) 앞 0.5m 안의 키 큰 가구
  const k6 = []
  for (const o of M.openings.filter(o => o.kind === 'window' && o.sill <= 0.3)) {
    const [x0, y0, x1, y1] = o.rect
    const horizontal = x1 - x0 >= y1 - y0
    const zone = horizontal ? [x0, y0 - 0.5, x1, y1 + 0.5] : [x0 - 0.5, y0, x1 + 0.5, y1]
    for (const f of floorItems) if (f.size[2] >= 1200 && overlap(zone, fp(f.id))) k6.push(`${o.name} 앞: ${f.name}`)
  }

  const fails = [
    k1.length ? 'K1' : null,
    k2['0.6m'].length ? 'K2' : null,
    k3.some(x => x.판정 === '실패') ? 'K3' : null,
    k4.판정 === '실패' ? 'K4' : null,
    k5.판정 === '실패' ? 'K5' : null,
    k6.length ? 'K6' : null,
  ].filter(Boolean)
  // K3b는 '주의' 등급: 걸음마 이후 위험이라 창 잠금장치 등으로 줄일 수 있다 (실패항목에 넣지 않음)
  const cautions = k3b.length ? ['K3b'] : []
  return {
    조합: document.getElementById('combo-now').textContent,
    보이는가구: items.length,
    K1_겹침: k1,
    K2_못가는방: k2,
    K3_앞여유: k3,
    K4_TV거리: k4,
    K5_아기침대: k5,
    K6_창가림: k6,
    K3b_창가발판: k3b,
    K7_소품: { 개수: smalls.length, 목록: smalls, 판정: smalls.length >= 3 && smalls.length <= 5 ? '통과' : '확인 필요' },
    실패항목: fails,
    주의항목: cautions,
  }
}
