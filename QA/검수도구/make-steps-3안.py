"""3안 배치 검수 단계 파일(steps-3안.json)을 만든다. layout-check.js를 각 단계에 넣어 페이지에서 실행한다.

사용: python make-steps-3안.py  → node shoot.mjs <뷰어 URL> <저장 폴더> steps-3안.json
"""
import json
from pathlib import Path

here = Path(__file__).parent
checker = (here / 'layout-check.js').read_text(encoding='utf-8')


def run(body):
    return '(() => { ' + checker + '\n' + body + ' })()'


TOP = "document.getElementById('view-top').click(); __viewer.controls.update();"
OBL = "document.getElementById('view-oblique').click(); __viewer.controls.update();"

steps = [
    # 빈 집(분양 기본 품목만): 가구 없이도 못 가는 방이 있는지 = 구조상 한계 기준선
    {'name': '00-빈집-기준선', 'js': run(
        "__viewer.loadProposal('A'); const s = __viewer.state; for (const f of APT_INTERIOR.furniture) s.furniture[f.id].visible = !!f.builtin;"
        " window.__k2base = null; const r = checkLayout(); window.__k2base = r.K2_못가는방; return r"
    )},
]
for pid in ['A', 'B', 'C']:
    steps.append({'name': f'{pid}-1-위에서', 'js': run(f"__viewer.loadProposal('{pid}'); {TOP} return checkLayout()"), 'wait': 1200})
    steps.append({'name': f'{pid}-2-비스듬히', 'js': run(f"{OBL} return '{pid}'"), 'wait': 1000})
    # 거실 눈높이: 주방 쪽 위에서 거실 창을 바라봄 (PM 토론 요청)
    EYE = ("const cx = APT_MODEL.extent[0]/2, cz = APT_MODEL.extent[1]/2;"
           " __viewer.camera.position.set(4.7 - cx, 1.55, 3.6 - cz); __viewer.controls.target.set(4.7 - cx, 0.7, 7.2 - cz); __viewer.controls.update();")
    steps.append({'name': f'{pid}-3-거실눈높이', 'js': run(f"{EYE} return '{pid}'"), 'wait': 1000})
    # 침실 쪽: 안방·아기방을 위에서 비스듬히
    BED = ("const cx = APT_MODEL.extent[0]/2, cz = APT_MODEL.extent[1]/2;"
           " __viewer.camera.position.set(4.6 - cx, 6.5, 9.6 - cz); __viewer.controls.target.set(4.6 - cx, 0, 6.0 - cz); __viewer.controls.update();")
    steps.append({'name': f'{pid}-4-침실쪽', 'js': run(f"{BED} return '{pid}'"), 'wait': 1000})

(here / 'steps-3안.json').write_text(json.dumps(steps, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'{len(steps)} steps → steps-3안.json')
