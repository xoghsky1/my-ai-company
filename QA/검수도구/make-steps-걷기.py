"""1인칭 걷기 검수 단계 파일(steps-걷기.json)을 만든다.

실제 키보드 입력(shoot.mjs의 key 단계는 누름·뗌이 바로 붙어 있음) 대신, 키를 누른 상태(walkKeys)를 넣고 시간이 흐른 뒤 위치를 본다.
사용: python make-steps-걷기.py → node shoot.mjs <뷰어 URL> <저장 폴더> steps-걷기.json
"""
import json
from pathlib import Path

here = Path(__file__).parent
PRE = "const v = __viewer; const $ = id => document.getElementById(id); const w = () => v.walk && ({ x: +v.walk.x.toFixed(2), y: +v.walk.y.toFixed(2), 방: v.walk.room, 눈: +v.camera.position.y.toFixed(2) });"


def js(body):
    return '(() => { ' + PRE + ' ' + body + ' })()'


def hold(keys, ms):
    """키를 ms 동안 누르고 있다가 뗀 뒤 위치를 돌려준다."""
    return ("(async () => { " + PRE + f" for (const k of {json.dumps(keys)}) v.walkKeys.add(k); await new Promise(r => setTimeout(r, {ms}));"
            " v.walkKeys.clear(); await new Promise(r => setTimeout(r, 100)); return w() })()")


steps = [
    {'name': '01-시작', 'js': js(
        "v.loadProposal('A'); v.setWall(1.0); document.getElementById('view-oblique').click(); v.controls.update(); const cam0 = v.camera.position.toArray().map(n => +n.toFixed(2));"
        " window.__cam0 = cam0; $('walk-toggle').click();"
        " return { 걷는중: !!v.walk, 위치: w(), 시야각: v.camera.fov, 버튼: $('walk-toggle').textContent, 안내: $('hint').textContent, 벽: document.getElementById('wall-full').classList.contains('on') }"), 'wait': 800},
    {'name': '02-앞으로', 'js': hold(['w'], 1000), 'wait': 600},
    {'name': '03-빨리', 'js': hold(['w', 'shift'], 500), 'wait': 600},
    # 현관에서 곧장 아래로 가면 아기방 문으로 들어가 공기청정기 앞에서 멈춘다
    {'name': '04-아기방-공기청정기앞', 'js': hold(['w'], 3000), 'wait': 600},
    # 거실 가운데에서 아래로: 거실 창(창턱 0.2m) 앞에서 멈춰야 한다 (창 안쪽 면 - 몸 0.2)
    {'name': '05-거실창에막힘', 'js': "(async () => { const v = __viewer; Object.assign(v.walk, { x: 5.17, y: 7.15, yaw: Math.PI / 2, pitch: 0 }); v.walkKeys.add('w'); await new Promise(r => setTimeout(r, 2500)); v.walkKeys.clear(); return { x: +v.walk.x.toFixed(2), y: +v.walk.y.toFixed(2), 방: v.walk.room } })()", 'wait': 800},
    # 안방에서 아래로: 바닥까지 오는 안방-발코니 창은 지나가 발코니로 나간다
    {'name': '05b-발코니로나가기', 'js': "(async () => { const v = __viewer; Object.assign(v.walk, { x: 2.75, y: 7.59, yaw: Math.PI / 2, pitch: 0 }); v.walkKeys.add('w'); await new Promise(r => setTimeout(r, 1500)); v.walkKeys.clear(); return { x: +v.walk.x.toFixed(2), y: +v.walk.y.toFixed(2), 방: v.walk.room } })()", 'wait': 800},
    {'name': '06-둘러보기', 'js': js(
        "const c = document.querySelector('#stage canvas').getBoundingClientRect(); const yaw0 = v.walk.yaw;"
        " const ev = (t, x) => (t === 'pointerdown' ? document.querySelector('#stage canvas') : window).dispatchEvent(new PointerEvent(t, { clientX: x, clientY: c.top + c.height / 2, button: 0, bubbles: true }));"
        " ev('pointerdown', c.left + 500); ev('pointermove', c.left + 860); ev('pointerup', c.left + 860);"
        " return { 돌아간각도: Math.round((v.walk.yaw - yaw0) * 180 / Math.PI) }"), 'wait': 800},
    {'name': '07-가구에막힘', 'js': js(
        # 소파 가운데를 향해 서서 걷기: 소파 사각형 안으로 들어가면 안 된다
        "const s = v.state.furniture.sofa; const [a0, b0, a1, b1] = v.footprint('sofa'); v.walk.x = a0 - 0.6; v.walk.y = (b0 + b1) / 2; v.walk.yaw = 0; v.walk.pitch = 0;"
        " window.__sofa = [a0, b0, a1, b1]; return { 소파: [a0, b0, a1, b1].map(n => +n.toFixed(2)), 출발: w() }")},
    {'name': '08-가구에막힘-결과', 'js': hold(['w'], 2000)},
    {'name': '09-아이눈높이', 'js': js("$('eye-child').click(); return { 눈: +v.camera.position.y.toFixed(2), 버튼: $('eye-child').className }"), 'wait': 800},
    {'name': '10-끝내기', 'js': js(
        "$('eye-adult').click(); window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));"
        " const cam = v.camera.position.toArray().map(n => +n.toFixed(2));"
        " return { 걷는중: !!v.walk, 시점복귀: JSON.stringify(cam) === JSON.stringify(window.__cam0), 시야각: v.camera.fov, 낮은벽복귀: document.getElementById('wall-low').classList.contains('on'), 안내: $('hint').textContent, 버튼: $('walk-toggle').textContent }"), 'wait': 800},
    {'name': '11-가구끌기정상', 'js': js("return { 컨트롤: v.controls.enabled }")},
]
(here / 'steps-걷기.json').write_text(json.dumps(steps, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(steps), 'steps')
