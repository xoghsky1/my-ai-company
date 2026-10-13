"""조명(밤 모드, 기본 vs 조명특화) 검수 단계 파일(steps-조명.json)을 만든다.

사용: python make-steps-조명.py → node shoot.mjs <뷰어 URL> <저장 폴더> steps-조명.json
"""
import json
from pathlib import Path

here = Path(__file__).parent
PRE = "const v = __viewer; const $ = id => document.getElementById(id); const L = v.light;"
VIEW = ("const cx = APT_MODEL.extent[0]/2, cz = APT_MODEL.extent[1]/2; v.setWall(2.3);"
        " v.camera.position.set(5.2 - cx, 9.5, 12.5 - cz); v.controls.target.set(5.2 - cx, 0, 5.6 - cz); v.controls.update();")


def js(body):
    return '(() => { ' + PRE + ' ' + body + ' })()'


def stat(extra=''):
    return ("return { 밤: L.night, 방식: L.mode, 장면: L.scene, 비교: L.compare, 배경: '#' + v.scene.background.getHexString(),"
            " 거실방등: +v.roomLights.find(r => r.name === '거실').main.intensity.toFixed(2), 거실간접: +(v.roomLights.find(r => r.name === '거실').cove?.intensity ?? 0).toFixed(2),"
            " 아기방간접: +(v.roomLights.find(r => r.name === '아기방').cove?.intensity ?? 0).toFixed(2) " + extra + "}")


steps = [
    {'name': '01-낮', 'js': js("v.loadProposal('A'); document.querySelector('.tabs button[data-tab=light]').click(); " + VIEW + stat()), 'wait': 1000},
    {'name': '02-밤-기본', 'js': js("window.dispatchEvent(new KeyboardEvent('keydown', { key: 'n' })); " + VIEW + stat()), 'wait': 1500},
    {'name': '03-밤-특화-일상', 'js': js("$('light-special').click(); v.applyScene('일상'); " + stat()), 'wait': 1500},
    {'name': '04-밤-특화-휴식', 'js': js("v.applyScene('휴식'); " + stat()), 'wait': 1500},
    {'name': '05-밤-특화-영화', 'js': js("v.applyScene('영화'); " + stat()), 'wait': 1500},
    {'name': '06-밤-특화-밤수유', 'js': js("v.applyScene('밤 수유'); " + stat()), 'wait': 1500},
    {'name': '07-나란히비교', 'js': js("v.applyScene('휴식'); $('light-compare').click(); " + stat(", 이름표: !$('compare-labels').hidden")), 'wait': 1500},
    {'name': '08-거실걷기-기본', 'js': js("$('light-compare').click(); $('light-basic').click(); v.walkStart(); Object.assign(v.walk, { x: 5.6, y: 4.6, yaw: Math.PI / 2, pitch: -0.05 }); return { 천장: true }"), 'wait': 1500},
    {'name': '09-거실걷기-특화휴식', 'js': js("$('light-special').click(); v.applyScene('휴식'); " + stat()), 'wait': 1500},
    {'name': '10-방끄기·밝기', 'js': js(
        "v.walkEnd(); const cb = [...$('light-rooms').querySelectorAll('label')].find(l => l.textContent.includes('안방')).querySelector('input'); cb.click();"
        " const off = +v.roomLights.find(r => r.name === '안방').main.intensity.toFixed(2); $('light-dim').value = 30; $('light-dim').dispatchEvent(new Event('input')); "
        + "return { 안방끔: off, 장면: L.scene, 밝기표시: $('light-dim-v').textContent }"), 'wait': 600},
    {'name': '11-낮으로', 'js': js("window.dispatchEvent(new KeyboardEvent('keydown', { key: 'n' })); " + stat(", 비교이름표숨김: $('compare-labels').hidden")), 'wait': 800},
]
(here / 'steps-조명.json').write_text(json.dumps(steps, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(steps), 'steps')
