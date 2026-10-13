#!/bin/sh
# 3안 배치 검수를 돌리고 요약을 출력한다. 사용: sh run-3안.sh <저장 폴더>
cd "$(dirname "$0")" || exit 1
PYTHONIOENCODING=utf-8 python3 make-steps-3안.py >/dev/null
URL="file:///C:/Users/taehopark94/OneDrive%20-%20NCSOFT/%EB%B0%94%ED%83%95%20%ED%99%94%EB%A9%B4/th-ai-company/%EA%B0%9C%EB%B0%9C/viewer/index.html"
rm -rf "$1"
timeout 280 node shoot.mjs "$URL" "$1" steps-3안.json >/dev/null 2>&1
PYTHONIOENCODING=utf-8 python3 - "$1/result.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
for r in d['results']:
    v = r.get('value')
    if not isinstance(v, dict):
        continue
    print('==', r['step'], v.get('조합'), '실패:', v.get('실패항목'), '주의:', v.get('주의항목'))
    print('  K1', v['K1_겹침'])
    print('  K2', v['K2_못가는방'])
    print('  K3', [(x['가구'], x['실제'], x['판정']) for x in v['K3_앞여유']])
    print('  K4', v['K4_TV거리'], ' K5', v['K5_아기침대'], ' K6', v['K6_창가림'])
    print('  K3b', v.get('K3b_창가발판'), ' K7', v.get('K7_소품'))
print('logs', d['logs'][:3])
PY
