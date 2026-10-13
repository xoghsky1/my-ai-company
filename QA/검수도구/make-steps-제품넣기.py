"""제품 넣기·견적 합산 검수 단계 파일(steps-제품넣기.json)을 만든다.

사용: python make-steps-제품넣기.py → node shoot.mjs <뷰어 URL> <저장 폴더> steps-제품넣기.json
"""
import json
from pathlib import Path

here = Path(__file__).parent
PRE = ("const v = __viewer; const $ = id => document.getElementById(id);"
       " const key = (k, o = {}) => window.dispatchEvent(new KeyboardEvent('keydown', { key: k, ctrlKey: true, bubbles: true, ...o }));"
       " const fill = (name, w, d, h, shape, price, url) => { $('p-name').value = name; $('p-w').value = w; $('p-d').value = d; $('p-h').value = h;"
       " $('p-shape').selectedIndex = [...$('p-shape').options].findIndex(o => o.text.startsWith(shape)); $('p-price').value = price; $('p-url').value = url; $('p-add').click() };"
       " const est = () => ({ 놓인: $('est-count').textContent, 합계: $('est-placed').textContent, 전체: $('est-all').textContent });"
       " const ids = () => v.products.map(p => p.id);")


def js(body):
    return '(() => { ' + PRE + ' ' + body + ' })()'


steps = [
    {'name': '00-초기화', 'js': js("localStorage.removeItem('apt-my-products'); localStorage.removeItem('apt-interior-combos'); location.reload(); return 'reload'"), 'wait': 3000},
    {'name': '01-빈목록', 'js': js("document.querySelector('[data-tab=product]').click(); return { 제품수: v.products.length, ...est(), 목록: $('product-list').textContent }")},
    {'name': '02-입력검사', 'js': js(
        "const r = {}; fill('', 2000, 900, 800, '소파', 1000, ''); r.이름없음 = $('p-msg').textContent;"
        " fill('소파', 0, 900, 800, '소파', 1000, ''); r.크기0 = $('p-msg').textContent;"
        " fill('소파', 2000, 900, 800, '소파', 1000, 'javascript:alert(1)'); r.나쁜링크 = $('p-msg').textContent; r.제품수 = v.products.length; return r")},
    {'name': '03-소파넣기', 'js': js(
        "v.loadProposal('A'); document.getElementById('view-top').click(); v.controls.update();"
        " fill('한샘 3인 소파 <b>테스트</b>', 2200, 950, 800, '소파', 1890000, 'https://example.com/sofa');"
        " const p = v.products[0]; const s = v.state.furniture[p.id];"
        " return { 제품수: v.products.length, 보임: s.visible, 자리: s.at, 방향: s.rot, 겹침: v.hitsFurniture(p.id), 벽겹침: v.hitsWall(p.id), 안내: $('p-msg').textContent, 모양: p.item.kind, 선택정보: $('info').innerText, 이름태그안됨: !$('info').querySelector('b'), 링크: $('info').querySelector('a')?.href, ...est(), 가구목록에있음: $('furniture-list').textContent.includes('내 제품') }"), 'wait': 800},
    {'name': '04-두번째·견적', 'js': js(
        "const r = {}; fill('수납장', 800, 400, 700, '수납장', 250000, ''); r.둘다놓음 = est();"
        " const cb = $('product-list').querySelectorAll('input[type=checkbox]')[1]; cb.click(); r.하나뺌 = est();"
        " key('z'); r.되돌림 = est(); key('z'); r.두번되돌림_수납장넣기전 = est(); key('y'); r.다시하기 = est(); return r")},
    {'name': '05-조합저장·불러오기', 'js': js(
        "const r = {}; $('combo-name').value = '제품테스트'; $('combo-save').click(); r.저장 = est();"
        " v.loadProposal('B'); r.B안 = est();"
        " [...document.querySelectorAll('#combo-list li')].find(li => li.textContent.includes('제품테스트')).querySelector('button').click(); r.불러옴 = est(); return r")},
    {'name': '05b-빈자리없음', 'js': js(
        "fill('너무 큰 장', 5000, 5000, 900, '수납장', 0, ''); const p = v.products[2]; const r = { 안내: $('p-msg').textContent, 자리: v.state.furniture[p.id].at };"
        " window.confirm = () => true; [...$('product-list').querySelectorAll('li')][2].querySelectorAll('button')[1].click(); r.지운뒤제품수 = v.products.length;"
        " key('z'); r.삭제되돌림_제품수 = v.products.length; r.되돌린이름 = v.products[2]?.name; key('y'); r.다시삭제_제품수 = v.products.length; return r")},
    {'name': '05c-수정', 'js': js(
        "const r = {}; const row = () => $('product-list').querySelectorAll('li')[1]; row().querySelectorAll('button')[0].click();"
        " r.폼채움 = [$('p-name').value, $('p-w').value, $('p-d').value, $('p-h').value, $('p-price').value]; r.버튼 = $('p-add').textContent; r.제목 = $('p-form-title').textContent; r.강조 = row().className;"
        " const at0 = JSON.stringify(v.state.furniture[v.products[1].id].at);"
        " $('p-name').value = '수납장 (큰 것)'; $('p-w').value = 1200; $('p-price').value = 390000; $('p-add').click();"
        " const p = v.products[1]; r.고친후 = { 이름: p.name, 크기: p.size, 가격: p.price, 장면크기: p.item.size, 자리그대로: JSON.stringify(v.state.furniture[p.id].at) === at0, 정보: $('info').innerText.split(String.fromCharCode(10)).slice(0, 3) }; r.견적 = est(); r.버튼복귀 = $('p-add').textContent;"
        " key('z'); r.되돌림 = { 이름: v.products[1].name, 크기: v.products[1].size, ...est() }; key('y'); r.다시하기 = { 이름: v.products[1].name, ...est() };"
        " row().querySelectorAll('button')[0].click(); $('p-cancel').click(); r.취소 = { 버튼: $('p-add').textContent, 폼비움: $('p-name').value === '', 이름: v.products[1].name }; return r")},
    {'name': '06-겹침검사', 'js': js(
        "const p = v.products[0]; v.state.furniture[p.id].at = [...v.state.furniture.sofa.at]; v.selectFurniture(v.furnitureObjs.get(p.id)); v.state.furniture[p.id].rot = 0;"
        " return { 겹침: v.hitsFurniture(p.id), 정보: $('info').innerText }")},
    {'name': '07-새로고침', 'js': js("location.reload(); return 'reload'"), 'wait': 3000},
    {'name': '08-새로고침후', 'js': js(
        "document.querySelector('[data-tab=product]').click(); const r = { 제품수: v.products.length, 이름: v.products.map(p => p.name), ...est() };"
        " [...document.querySelectorAll('#combo-list li')].find(li => li.textContent.includes('제품테스트')).querySelector('button').click(); r.조합불러옴 = est(); return r")},
    {'name': '09-화면', 'js': js(
        "const p = v.products[0]; v.state.furniture[p.id].at = [4.7, 5.6]; v.state.furniture[p.id].rot = 0; v.selectFurniture(v.furnitureObjs.get(p.id));"
        " document.getElementById('view-oblique').click(); v.controls.update(); return est()"), 'wait': 1200},
    {'name': '10-삭제', 'js': js(
        "window.confirm = () => true; const before = ids(); [...$('product-list').querySelectorAll('button')].find(x => x.textContent === '삭제').click();"
        " return { 전: before.length, 후: v.products.length, 장면에서빠짐: !v.furnitureObjs.has(before[0]), 저장: JSON.parse(localStorage.getItem('apt-my-products')).length, ...est() }")},
    {'name': '11-정리', 'js': js("localStorage.removeItem('apt-my-products'); localStorage.removeItem('apt-interior-combos'); return 'ok'")},
]
(here / 'steps-제품넣기.json').write_text(json.dumps(steps, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(steps), 'steps')
