"""구역(방) 편집 화면 검수 단계 파일(steps-구역편집.json)을 만든다.

사용: python make-steps-구역편집.py → node shoot.mjs <뷰어 URL> <저장 폴더> steps-구역편집.json
"""
import json
from pathlib import Path

here = Path(__file__).parent
PRE = ("const v = __viewer; const $ = id => document.getElementById(id); const M = window.APT_MODEL;"
       " const cv = document.querySelector('#stage canvas'); const R = cv.getBoundingClientRect();"
       " const scr = (x, y) => { const p = new v.THREE.Vector3(x - M.extent[0]/2, 0, y - M.extent[1]/2).project(v.camera); return [R.left + (p.x+1)/2*R.width, R.top + (1-p.y)/2*R.height] };"
       " const label = n => M.rooms.find(r => r.name === n).label;"
       " const bar = n => [...$('room-bar').querySelectorAll('button')].find(b => b.textContent === n);"
       " const panel = () => ({ 보임: !$('room-panel').hidden, 가구: [...$('room-panel').querySelectorAll('.rp-name')].map(b => b.textContent) });"
       " const faded = () => [...v.furnitureObjs].filter(([, g]) => g.userData.faded).length;"
       " const shownLabels = () => v.labels.filter(l => l.visible).map(l => l.element.textContent);"
       " const cam = () => v.camera.position.toArray().map(n => +n.toFixed(2));")


def js(body):
    return '(() => { ' + PRE + ' ' + body + ' })()'


steps = [
    {'name': '01-전체', 'js': js("v.loadProposal('A'); v.setWall(2.3); document.getElementById('view-oblique').click(); v.controls.update(); window.__cam0 = cam();"
                                 " return { 바로가기: [...$('room-bar').querySelectorAll('button')].map(b => b.textContent), 패널: panel().보임 }"), 'wait': 800},
    {'name': '02-거실들어가기', 'js': js("bar('거실').click(); return 'click'"), 'wait': 1200},
    {'name': '03-거실상태', 'js': js(
        "return { 집중: v.focus?.room, 낮은벽: $('wall-low').classList.contains('on'), 애니끝: !v.camAnim, 패널: panel(), 흐린가구수: faded(), 보이는이름표: shownLabels(),"
        " 바로가기on: $('room-bar').querySelector('.on')?.textContent, 안내: $('hint').textContent, 마감칩: $('room-panel').querySelectorAll('.chip').length }")},
    {'name': '04-바닥바꾸고되돌리기', 'js': js(
        "const f0 = v.state.floors['거실']; [...$('room-panel').querySelectorAll('.chips')][0].querySelector('.chip:not(.on)').click(); const f1 = v.state.floors['거실'];"
        " window.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true })); return { 바뀜: f1 !== f0, 되돌림: v.state.floors['거실'] === f0, 패널유지: panel().보임 }")},
    {'name': '05-패널에서돌리기·숨기기', 'js': js(
        "const rows = [...$('room-panel').querySelectorAll('.rp-item')]; const sofaRow = rows.find(r => r.textContent.includes('소파')); const r0 = v.state.furniture.sofa.rot;"
        " [...sofaRow.querySelectorAll('button')].find(b => b.textContent === '⟳').click(); const r1 = v.state.furniture.sofa.rot;"
        " const lampRow = [...$('room-panel').querySelectorAll('.rp-item')].find(r => r.textContent.includes('플로어 스탠드')); lampRow.querySelector('input').click();"
        " const r = { 돌림: [r0, r1], 선택: v.state && document.querySelector('#info .room-name')?.textContent, 스탠드숨김: !v.state.furniture.lamp.visible, 숨겨도목록에: panel().가구.includes('플로어 스탠드') };"
        " window.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true })); window.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true }));"
        " r.되돌림 = [v.state.furniture.sofa.rot, v.state.furniture.lamp.visible]; return r")},
    {'name': '06-안방더블클릭', 'js': js(
        "const [x, y] = scr(...label('안방')); cv.dispatchEvent(new MouseEvent('dblclick', { clientX: x, clientY: y, bubbles: true })); return [x, y].map(Math.round)"), 'wait': 1200},
    {'name': '07-안방상태', 'js': js(
        "return { 집중: v.focus?.room, 패널: panel(), 거실소파흐림: v.furnitureObjs.get('sofa').userData.faded, 침대흐림: v.furnitureObjs.get('bed').userData.faded, 보이는이름표: shownLabels() }")},
    {'name': '08-흐린가구못잡음', 'js': js(
        # 흐린 거실 소파 위치를 눌러도 선택되지 않아야 한다
        "v.selectFurniture(null); const s = v.state.furniture.sofa.at; const [x, y] = scr(s[0], s[1]); const o = { clientX: x, clientY: y, button: 0, bubbles: true };"
        " v.controls.enabled = false; cv.dispatchEvent(new PointerEvent('pointerdown', o)); cv.dispatchEvent(new PointerEvent('pointerup', o)); v.controls.enabled = true;"
        " return { 선택된것: document.querySelector('#info .room-name')?.textContent ?? '없음' }")},
    {'name': '09-제품넣기는이방에', 'js': js(
        "localStorage.removeItem('apt-my-products'); $('room-panel').querySelector('.row button').click(); const tab = document.querySelector('.tabs button.on')?.dataset.tab;"
        " $('p-name').value = '안방 화장대'; $('p-w').value = 800; $('p-d').value = 400; $('p-h').value = 750; $('p-price').value = 300000; $('p-add').click();"
        " const p = v.products.at(-1); const at = v.state.furniture[p.id].at; return { 탭: tab, 자리: at, 방: M.rooms.find(r => r.cells.some(c => at[0] >= c[0] && at[0] <= c[2] && at[1] >= c[1] && at[1] <= c[3]))?.name, 패널에: panel().가구.includes('안방 화장대') }"), 'wait': 800},
    {'name': '10-Esc나가기', 'js': js("window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })); return 'esc'"), 'wait': 1200},
    {'name': '11-나간상태', 'js': js(
        "return { 집중: v.focus, 벽복귀: $('wall-full').classList.contains('on'), 시점복귀: JSON.stringify(cam()) === JSON.stringify(window.__cam0), 흐린가구수: faded(), 이름표수: shownLabels().length, 패널: panel().보임, 안내: $('hint').textContent }")},
    {'name': '12-한번클릭→이방편집', 'js': js(
        "const [x, y] = scr(...label('아기방')); const o = { clientX: x, clientY: y, button: 0, bubbles: true }; v.controls.enabled = false; cv.dispatchEvent(new PointerEvent('pointerdown', o)); cv.dispatchEvent(new PointerEvent('pointerup', o)); v.controls.enabled = true;"
        " const btn = $('room-edit'); const r = { 버튼: btn?.textContent }; btn?.click(); r.집중 = v.focus?.room; return r"), 'wait': 1200},
    {'name': '13-편집중걷기', 'js': js(
        "$('walk-toggle').click(); const r = { 집중: v.focus, 걷는중: !!v.walk }; window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })); r.걷기끝 = !v.walk; r.시점 = JSON.stringify(cam()) === JSON.stringify(window.__cam0); localStorage.removeItem('apt-my-products'); return r"), 'wait': 800},
]
(here / 'steps-구역편집.json').write_text(json.dumps(steps, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(steps), 'steps')
