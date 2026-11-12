# -*- coding: utf-8 -*-
"""장비별 투입 목록 단독 실행 테스트 — 2026-09-30 (Cowork)

16:00 자동 실행을 기다리지 않고 오늘 바꾼 machine_queue.py 를 실데이터로 한 번 돌린다.
- 하는 일: ERP 조회(읽기 전용) → 스냅샷 저장(erp/snapshot/) → 투입 목록 계산 → erp/worklog_unmatched.txt 갱신
- 안 하는 일: 현황판 HTML 생성 · 사내 배포 · GitHub 업로드 · 일일보고 · 메일 (generate.py 를 부르지 않는다)
- worklog_unmatched.txt 는 자동 실행 때마다 덮어쓰는 파일이라 테스트로 덮어써도 된다.
- 결과 요약: 화면 + erp/probe_test_queue_result.txt (.gitignore 의 erp/probe_*_result.txt 패턴으로 제외)
실행 (cnc-wiki 폴더에서): python erp\\test_machine_queue.py
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pandas as pd
import machine_queue as mq

logs = []
def log(s):
    print(s)
    logs.append(str(s))

def load_holds():
    try:
        data = json.load(open(os.path.join(HERE, 'hold_orders.json'), encoding='utf-8'))
        return {str(h['so_no']): str(h.get('reason', '보류')) for h in data.get('holds', []) if h.get('so_no')}
    except Exception as e:
        log(f'  (보류 대장 읽기 실패 → 0건으로 진행: {e})')
        return {}

log(f'[테스트] {pd.Timestamp.now(tz="Asia/Seoul"):%Y-%m-%d %H:%M:%S} KST · LEAD_CAP_DAYS={mq.LEAD_CAP_DAYS}')
holds = load_holds()
log(f'  보류 대장 {len(holds)}건')
q = mq.fetch_machine_queue(holds, log=log)
if q is None:
    log('❌ 투입 목록 생성 실패 — 위 경고 확인')
else:
    st = (q.get('worklog') or {}).get('stats') or {}
    kinds = {}
    for x in st.get('issues', []):
        kinds[x['kind']] = kinds.get(x['kind'], 0) + 1
    log(f"✅ FG {q['FG']['n']}품목/{q['FG']['qty']}개(셋업 {q['FG']['setups']}) · GX7 {q['GX7']['n']}품목/{q['GX7']['qty']}개(셋업 {q['GX7']['setups']}) · 기타 {q['etc']['n']}")
    log(f"  작업일지 매칭: 코드 {st.get('codes')} · 매칭 {st.get('matched')} · 후보2+ {st.get('ambiguous')} · 상한 {st.get('lead_cap')} · 초과 배정 {st.get('overflow', 0)} · 실패 {st.get('unmatched')} · 번호 없음 {st.get('nocode')}")
    log('  종류별: ' + ' · '.join(f'{k} {v}' for k, v in sorted(kinds.items())))
    log(f"  가공완료로 빠진 품목 {q['worklog']['ground_items']}개/{q['worklog']['ground_qty']}개 · 제외 보류 {q['excluded']['hold']} · 자투리 {q['excluded']['minor']}")
snap = os.path.join(HERE, 'snapshot')
if os.path.isdir(snap):
    for f in sorted(os.listdir(snap)):
        log(f'  스냅샷 {f} {os.path.getsize(os.path.join(snap, f)):,} B')
else:
    log('  ⚠️ erp/snapshot/ 없음')
with open(os.path.join(HERE, 'probe_test_queue_result.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(logs) + '\n')
