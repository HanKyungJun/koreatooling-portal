import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd, os

def classify(shape):
    s = str(shape).strip().lower()
    if s in ('형     상', 'nan', ''): return None
    if '볼' in s: return '볼'
    if '드릴' in s: return '드릴'
    if '스퀘어' in s: return '스퀘어'
    if '면취' in s or '챔퍼' in s or 'c0.' in s: return '면취'
    if 'nc' in s: return 'NC'
    if any(x in s for x in ['코너', 'r0.', 'r1', 'r2', 'r3', 'r4']): return '코너R'
    if '평' in s: return '평'
    return None

# ── 데이터 수집 ────────────────────────────────────────────────────────────────
records = []
base = 'raw/출하현황'
for year in [2022, 2023, 2024, 2025, 2026]:
    folder = os.path.join(base, f'재연마 작업일지({year})')
    for month in range(1, 13):
        fp = os.path.join(folder, f'재연마_월간생산일지 ({month}월).xls')
        if not os.path.exists(fp): continue
        try:
            xl = pd.ExcelFile(fp)
            for sheet in xl.sheet_names:
                if not sheet.isdigit(): continue
                df = pd.read_excel(fp, sheet_name=sheet, header=None)
                for machine, r_start, r_end in [('FG', 2, 17), ('GX7', 21, 36)]:
                    for ri in range(r_start, min(r_end, len(df))):
                        row = df.iloc[ri]
                        shape  = row.iloc[1]
                        qty    = row.iloc[10]
                        t      = row.iloc[11]
                        dia    = row.iloc[3]
                        flutes = row.iloc[2]
                        if pd.isna(shape) or str(shape).strip() == '': continue
                        group = classify(shape)
                        if not group: continue
                        try:
                            qty    = int(qty)    if pd.notna(qty)    else 0
                            t      = int(t)      if pd.notna(t)      else 0
                            dia    = float(dia)  if pd.notna(dia)    else None
                            flutes = int(flutes) if pd.notna(flutes) else None
                        except:
                            continue
                        if qty <= 0: continue
                        records.append({
                            'year': year, 'month': month, 'machine': machine,
                            'shape_raw': str(shape).strip(), 'group': group,
                            'qty': qty, 'time': t, 'dia': dia, 'flutes': flutes
                        })
        except:
            pass

df_all = pd.DataFrame(records)
print(f'총 {len(df_all)}건 수집 완료')


# ── 테이블 생성 함수 ──────────────────────────────────────────────────────────
def fmt_dia(d):
    return f'Ø{int(d)}' if d == int(d) else f'Ø{d}'

def conditions_table(sub, group=None):
    # 직경 × 날수 조합별 평균 가공시간
    grp = sub[sub['time'] > 0].groupby(['dia', 'flutes']).agg(
        avg_time=('time', 'mean'),
        qty=('qty', 'sum')
    ).reset_index().sort_values(['flutes', 'dia'])

    if group == '볼':
        shape_codes = {'볼': 'BA', '평': 'FL', '드릴': 'DR', '면취': 'CE', '코너R': 'CO', 'NC': 'NC'}
        scode = shape_codes.get(group, group)
        rows = [
            '|  |  |  |  |  | 볼 게쉬 | | | 플런지 힐 클리어런스 | | | OD / 볼 피니쉬 | | |  |  |',
            '| 날수 | 직경 | 형상 | 품목코드 | 평균 가공시간(초) | RPM | Feed | 휠 | RPM | Feed | 휠 | RPM | Feed | 휠 | DOC(mm) | 상태 |',
            '|------|------|------|---------|----------------|-----|------|-----|-----|------|-----|-----|------|-----|---------|------|'
        ]
        for _, r in grp.iterrows():
            dia  = fmt_dia(r['dia'])
            fl   = f"{int(r['flutes'])}날"
            avg  = f"{int(r['avg_time'])}"
            code = f"{int(r['flutes'])}{scode}{int(r['dia']*10):03d}1100"
            rows.append(f'| {fl} | {dia} | {group} ({scode}) | `{code}` | {avg} |  |  |  |  |  |  |  |  |  |  | 미기록 |')
    else:
        rows = [
            '| 직경 | 날수 | 평균 가공시간(초) | RPM | Feed (진입/중간/마무리) | DOC(mm) | 휠 | 상태 |',
            '|------|------|----------------|-----|----------------------|---------|-----|------|'
        ]
        for _, r in grp.iterrows():
            dia = fmt_dia(r['dia'])
            fl  = f"{int(r['flutes'])}날"
            avg = f"{int(r['avg_time'])}"
            rows.append(f'| {dia} | {fl} | {avg} |  |  /  /  |  |  | 미기록 |')
    return '\n'.join(rows)

def yearly_table(sub):
    lines = [
        '| 연도 | 1월 | 2월 | 3월 | 4월 | 5월 | 6월 | 7월 | 8월 | 9월 | 10월 | 11월 | 12월 | 연간합계 |',
        '|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|------|------|---------|'
    ]
    for yr in [2022, 2023, 2024, 2025, 2026]:
        row, total = [], 0
        for m in range(1, 13):
            v = int(sub[(sub['year'] == yr) & (sub['month'] == m)]['qty'].sum())
            total += v
            row.append(f'{v:,}' if v > 0 else '-')
        if total > 0:
            lines.append(f'| {yr}년 | ' + ' | '.join(row) + f' | **{total:,}** |')
    return '\n'.join(lines)

def subtypes_list(sub):
    st = sub.groupby('shape_raw')['qty'].sum().sort_values(ascending=False).head(10)
    return '\n'.join(f'- `{n}` — {int(c):,}개' for n, c in st.items())


# ── 페이지 정보 ───────────────────────────────────────────────────────────────
pages = {
    '볼':    {'emoji': '⚪', 'stack': '스택-1-1',
              'desc': '볼 엔드밀 형상의 재연삭. 반구형 선단부를 연삭하며 3D 곡면 가공용으로 주로 사용됩니다.',
              'note': 'FG 장비에서 처리량이 가장 많은 형상. 거의 대부분 2날입니다.'},
    '평':    {'emoji': '▬', 'stack': '스택-1-1',
              'desc': '플랫 엔드밀 선단면 재연삭. 평면 가공, 포켓 가공 등 범용 가공에 사용됩니다.',
              'note': '라핑(평_라핑) 처리가 병행되는 경우가 많습니다.',
              'aliases': ['스퀘어', 'FL', 'SQ', '평엔드밀', '스퀘어엔드밀']},
    '드릴':  {'emoji': '🔩', 'stack': '스택-1-1',
              'desc': '드릴 선단부 재연삭. 포인트 각도 및 절삭날 재생을 목적으로 합니다.',
              'note': '전량 2날. 소수점 직경(Ø6.9, Ø8.7 등)이 많습니다.'},
    '스퀘어': {'emoji': '⬛', 'stack': '스택-1-1',
              'desc': '스퀘어 엔드밀 재연삭. 직각 코너를 유지하며 측면 및 바닥 가공에 사용됩니다.',
              'note': '대직경(Ø16~Ø20) 비율이 높습니다.'},
    '면취':  {'emoji': '🔺', 'stack': '스택-1-2',
              'desc': '면취(Chamfer) 공구 재연삭. 모따기, 버 제거 등에 사용됩니다.',
              'note': '60°, 90°, 120° 등 각도별 변형 존재. 거의 2날.'},
    '코너R': {'emoji': '🔵', 'stack': '스택-1-2',
              'desc': '코너R 엔드밀 재연삭. R값에 따라 가공 조건이 달라지며 정밀 윤곽 가공에 사용됩니다.',
              'note': 'GX7 장비에서 처리량이 가장 많은 형상. R0.2~R3 범위.'},
    'NC':    {'emoji': '🔧', 'stack': '스택-1-1',
              'desc': 'NC 공구 재연삭. HSS 재질 포함.',
              'note': 'HSS(고속도강) 재질 포함. 초경 대비 연삭 조건 차이 있음.'},
}


# ── 페이지 생성 ───────────────────────────────────────────────────────────────
for group, info in pages.items():
    sub        = df_all[df_all['group'] == group]
    total_qty  = int(sub['qty'].sum())
    years      = sorted(sub['year'].unique())
    fg_qty     = int(sub[sub['machine'] == 'FG']['qty'].sum())
    gx_qty     = int(sub[sub['machine'] == 'GX7']['qty'].sum())

    aliases = info.get('aliases', [])
    aliases_line = f'\naliases: {aliases}' if aliases else ''
    content = f"""---
type: tool
category: "연삭 (Grinding)"
shape: "{group}"{aliases_line}
tags: [연삭, {group}, 형상별, 조건참조]
updated: 2026-04-22
---

# 연삭 조건 참조 — {info['emoji']} {group} 형상

{info['desc']}

> {info['note']}

---

## 직경 × 날수별 조건표

평균 가공시간은 작업일지(2022~2026) 실데이터 기준입니다.
RPM / Feed / DOC 칸은 조건 확정 시 채워넣으세요.

{conditions_table(sub, group=group)}

---

## 개별 조건 상세 페이지

확정 조건이 있는 공구는 별도 페이지로 관리합니다:

| 공구 규격 | 날수 | RPM | 상태 | 페이지 |
|-----------|------|-----|------|--------|
| — | — | — | 미기록 | — |

> 📌 신규 조건 확정 시 [[연삭-조건-기록]] 양식으로 페이지 생성 후 여기에 추가하세요.

---

## 관련 페이지

- [[연삭-조건-목록]] — 전체 형상 목록
- [[연삭-조건-기록]] — 기록 양식 및 진단 가이드
- [[anca-cnc-tool-grinder]] — 장비 페이지
- [[{info['stack']}]] — 주요 사용 스택
"""
    out = f'wiki/tools/연삭-조건-{group}.md'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  업데이트: {out}')

print('\n완료!')
