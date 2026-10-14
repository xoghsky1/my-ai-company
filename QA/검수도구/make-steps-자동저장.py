"""자동 저장 · 파일 내보내기·가져오기 검수 단계 파일(steps-자동저장.json)을 만든다.

새로고침과 "다른 PC"(저장소를 모두 지운 브라우저)를 흉내 낸다. 내보낸 파일 내용은 sessionStorage에 잠시 두고 넘긴다.
사용: python make-steps-자동저장.py → node shoot.mjs <뷰어 URL> <저장 폴더> steps-자동저장.json
"""
import json
from pathlib import Path

here = Path(__file__).parent
PRE = ("const v = __viewer; const $ = id => document.getElementById(id);"
       " const now = () => ({ 조합: v.currentCombo, 수정됨: v.changed, 거실바닥: v.state.floors['거실'], 소파: JSON.stringify(v.state.furniture.sofa), 알림: $('toast').hidden ? null : $('toast').innerText.replace(/\\s+/g, ' ') });")
CLEAR = "for (const k of ['apt-autosave', 'apt-interior-combos', 'apt-my-products']) localStorage.removeItem(k);"


def js(body):
    return '(() => { ' + PRE + ' ' + body + ' })()'


def ajs(body):
    return '(async () => { ' + PRE + ' ' + body + ' })()'


steps = [
    {'name': '00-초기화', 'js': js(CLEAR + " sessionStorage.removeItem('qa-export'); location.reload(); return 'reload'"), 'wait': 3000},
    {'name': '01-처음', 'js': js("return now()")},
    {'name': '02-편집', 'js': js(
        "v.loadProposal('B'); const chip = [...$('floor-chips').querySelectorAll('.chip')]; $('finish-room').value = '거실'; $('finish-room').dispatchEvent(new Event('change'));"
        " [...$('floor-chips').querySelectorAll('.chip')].find(c => !c.classList.contains('on')).click();"
        " v.selectFurniture(v.furnitureObjs.get('sofa')); window.dispatchEvent(new KeyboardEvent('keydown', { key: 'r' })); window.__before = now(); return window.__before")},
    {'name': '03-새로고침', 'js': js("sessionStorage.setItem('qa-before', JSON.stringify(window.__before)); location.reload(); return 'reload'"), 'wait': 3000},
    {'name': '04-이어서열림', 'js': js(
        "const before = JSON.parse(sessionStorage.getItem('qa-before')); const n = now(); const r = { ...n, 같음: ['조합', '수정됨', '거실바닥', '소파'].every(k => n[k] === before[k]) };"
        " $('furniture-reset').click(); r.처음자리_B안소파 = JSON.stringify(v.state.furniture.sofa.at) === JSON.stringify(v.stateFrom(APT_INTERIOR.proposals.find(p => p.id === 'B')).furniture.sofa.at);"
        " window.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true })); return r")},
    {'name': '05-처음상태로·되돌리기', 'js': js(
        "const r = {}; const btn = [...$('toast').querySelectorAll('button')].find(b => b.textContent === '처음 상태로'); btn?.click(); r.처음상태로 = now();"
        " window.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true })); r.되돌림 = now(); return r")},
    {'name': '06-내보내기', 'js': ajs(
        "$('combo-name').value = '내보내기테스트'; $('combo-save').click();"
        " $('p-name').value = '테스트 서랍장'; $('p-w').value = 900; $('p-d').value = 450; $('p-h').value = 800; $('p-price').value = 250000; $('p-add').click();"
        " let dl = null; const orig = HTMLAnchorElement.prototype.click; HTMLAnchorElement.prototype.click = function () { dl = { name: this.download, href: this.href } };"
        " $('export-file').click(); HTMLAnchorElement.prototype.click = orig;"
        " const text = await (await fetch(dl.href)).text(); sessionStorage.setItem('qa-export', text); const d = JSON.parse(text);"
        " return { 파일이름: dl.name, app: d.app, 조합수: d.combos.length, 조합: d.combos.map(c => c.name), 제품: d.products.map(p => p.name), 화면조합: d.current.combo, 안내: $('io-msg').textContent }")},
    {'name': '07-다른PC', 'js': js(CLEAR + " location.reload(); return 'reload'"), 'wait': 3000},
    {'name': '08-다른PC-처음', 'js': js("return { ...now(), 조합목록: [...$('combo-list').querySelectorAll('.name')].map(e => e.textContent), 제품수: v.products.length }")},
    {'name': '09-가져오기', 'js': js(
        "v.importData(JSON.parse(sessionStorage.getItem('qa-export')), false);"
        " return { ...now(), 조합목록: [...$('combo-list').querySelectorAll('.name')].map(e => e.textContent), 제품: v.products.map(p => p.name), 제품보임: v.products.map(p => v.state.furniture[p.id]?.visible), 안내: $('io-msg').textContent }")},
    {'name': '10-가져온뒤새로고침', 'js': js("location.reload(); return 'reload'"), 'wait': 3000},
    {'name': '11-유지', 'js': js("return { ...now(), 조합목록: [...$('combo-list').querySelectorAll('.name')].map(e => e.textContent), 제품수: v.products.length }")},
    {'name': '12-잘못된파일', 'js': ajs(
        "const r = {}; v.importData({ app: 'other' }, false); r.다른앱 = [$('io-msg').textContent, $('io-msg').className];"
        " v.importData({ app: 'apt-3d-viewer', combos: [{ name: 1 }] }, false); r.빈내용 = $('io-msg').textContent;"
        " const dt = new DataTransfer(); dt.items.add(new File(['{not json'], 'bad.json', { type: 'application/json' })); $('import-input').files = dt.files;"
        " $('import-input').dispatchEvent(new Event('change')); await new Promise(res => setTimeout(res, 300)); r.깨진파일 = $('io-msg').textContent; r.조합그대로 = v.currentCombo; return r")},
    {'name': '12b-깨진자동저장', 'js': js("localStorage.setItem('apt-autosave', JSON.stringify({ v: 1, combo: 'X', changed: true, state: { floors: {}, walls: {}, furniture: { sofa: { at: null, rot: 0, visible: true } } } })); location.reload(); return 'reload'"), 'wait': 3000},
    {'name': '12c-깨진자동저장-결과', 'js': js("return { 뷰어동작: !!v.scene, ...now() }")},
    {'name': '13-정리', 'js': js(CLEAR + " sessionStorage.clear(); return 'ok'")},
]
(here / 'steps-자동저장.json').write_text(json.dumps(steps, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(steps), 'steps')
