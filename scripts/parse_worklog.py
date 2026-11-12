#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
재연마 작업일지 다개년 파싱 → CSV

실행:
    python scripts/parse_worklog.py              # 2022~2026 전체
    python scripts/parse_worklog.py 2026         # 특정 연도만
    python scripts/parse_worklog.py 2025 2026    # 여러 연도

입력: raw/출하현황/재연마 작업일지(YYYY)/재연마_월간생산일지 (M월).xls
출력: outputs/worklog_parsed/jobs_all.csv   — 작업 레코드
      outputs/worklog_parsed/meter_all.csv  — 설비 계기값 행 (참고, 해석 미확정)

━━━ 파싱 규칙 (2026-08-28 확립, 반드시 유지) ━━━
1. 고정 행 범위로 읽지 말 것.
   daily_report.py 는 FG를 행 2~16 / GX7을 행 21~35로 하드코딩하지만,
   2022년 일부 시트는 FAST GRIND 블록이 15슬롯을 넘어 확장돼 있다.
   고정 범위로 읽으면 2022년만 759건(+20.8%)이 누락된다.
   → A열에서 'FAST GRIND' / 'GX7' 마커를 찾아 블록을 동적으로 탐지한다.

2. 수량>0 조건만으로는 작업 아닌 행이 섞인다.
   블록 끝에 ① '합' 합계행 ② 설비 계기값 행이 붙어 있고 둘 다 수량 열에 값이 있다.
   → '형상'(1열)이 비어 있으면 작업 행이 아니다.

3. 계기값 행은 연도별로 의미가 다르다. 해석하지 말 것.
   2022: [146, 공란, 609160, 269.3] / 2024: [92387, 92551, 164] / 2025: [4033, 4108, 75]
   리셋은 확인됨(2026-01-02 FG 11035→1)이나 시간 단위로 해석되지 않는다.
   계기 차이 대비 그날 사이클 합계가 2.5배 크고, 상관은 수량(0.69) > 시간(0.34).

4. 가공비(9열)·금액(12열)은 추출하지 않는다.
   2024년 이후 실거래 개당 단가가 들어 있다 (2022~2023은 가공비=1로 마스킹).
   CLAUDE.md §4 기준 대외비.

5. 「가공시간」(11열)은 ANCA 장비가 기록한 개당 사이클 타임이다 [사내 확인, 2026-08-28].
   셋업·대기·검사·드레싱은 포함되지 않는다.
"""
import sys, csv, datetime
from pathlib import Path

try:
    import xlrd
except ImportError:
    sys.exit("xlrd 가 필요합니다:  pip install xlrd")

BASE = Path(__file__).resolve().parent.parent
RAW  = BASE / 'raw' / '출하현황'
OUT  = BASE / 'outputs' / 'worklog_parsed'

COLS = ['연','월','일','설비','순서','형상','날수F','날경','상크경',
        '코팅','특이사항','작업자','완료여부','수량','단위시간s','시간합계s']
# 시트 열 인덱스 (0-base) — 2022~2026 전 연도 동일함을 실측 확인
C_SEQ, C_SHAPE, C_FLUTE, C_DIA, C_SHANK, C_COAT = 0, 1, 2, 3, 4, 5
C_NOTE, C_WORKER, C_DONE = 6, 7, 8
C_QTY, C_UNIT_SEC, C_TOTAL_SEC = 10, 11, 13
# 9=가공비, 12=금액 → 대외비, 추출하지 않음


def cell(sh, r, c):
    if r >= sh.nrows or c >= sh.ncols:
        return ''
    v = sh.cell_value(r, c)
    if isinstance(v, float) and v == int(v):
        v = int(v)
    return str(v).strip()


def num(x):
    try:
        return float(str(x).replace(',', ''))
    except (TypeError, ValueError):
        return 0.0


def parse_year(year):
    """한 해치 xls 12개를 파싱해 (작업행, 계기행, 경고) 반환."""
    jobs, meters, warns = [], [], []
    for month in range(1, 13):
        path = RAW / f'재연마 작업일지({year})' / f'재연마_월간생산일지 ({month}월).xls'
        if not path.exists():
            warns.append(f'{year}-{month:02d} 파일 없음')
            continue
        try:
            wb = xlrd.open_workbook(str(path))
        except Exception as exc:
            warns.append(f'{year}-{month:02d} 열기 실패: {exc}')
            continue

        for day in range(1, 32):
            if str(day) not in wb.sheet_names():
                continue
            sh = wb.sheet_by_name(str(day))

            # 규칙 1 — 블록 마커 동적 탐지
            marks = []
            for r in range(sh.nrows):
                tag = cell(sh, r, 0).upper().replace(' ', '')
                if tag in ('FASTGRIND', 'GX7'):
                    marks.append((r, 'FG' if tag == 'FASTGRIND' else 'GX7'))
            if not marks:
                warns.append(f'{year}-{month:02d}-{day:02d} 블록 마커 없음')
                continue

            for i, (mrow, equip) in enumerate(marks):
                if cell(sh, mrow + 1, C_SHAPE).replace(' ', '') != '형상':
                    warns.append(f'{year}-{month:02d}-{day:02d} {equip} 헤더 이상')
                end = marks[i + 1][0] if i + 1 < len(marks) else sh.nrows

                for r in range(mrow + 2, end):
                    qty = num(cell(sh, r, C_QTY))
                    if qty <= 0:
                        continue
                    shape = cell(sh, r, C_SHAPE)
                    if not shape:                       # 규칙 2
                        seq = cell(sh, r, C_SEQ).replace(' ', '')
                        if not seq.startswith('합'):     # 합계행은 버리고 계기행만 보존
                            meters.append([year, month, day, equip,
                                           num(cell(sh, r, C_QTY)),
                                           num(cell(sh, r, C_UNIT_SEC)),
                                           num(cell(sh, r, 12))])
                        continue
                    jobs.append([
                        year, month, day, equip,
                        cell(sh, r, C_SEQ), shape,
                        cell(sh, r, C_FLUTE), cell(sh, r, C_DIA), cell(sh, r, C_SHANK),
                        cell(sh, r, C_COAT), cell(sh, r, C_NOTE),
                        cell(sh, r, C_WORKER), cell(sh, r, C_DONE),
                        int(qty), num(cell(sh, r, C_UNIT_SEC)), num(cell(sh, r, C_TOTAL_SEC)),
                    ])
    return jobs, meters, warns


def main(years):
    OUT.mkdir(parents=True, exist_ok=True)
    all_jobs, all_meters, all_warns = [], [], []
    for y in years:
        jobs, meters, warns = parse_year(y)
        print(f'{y}: 작업 {len(jobs):>5}건 / 계기행 {len(meters):>3}건'
              + (f' / ⚠️ 경고 {len(warns)}건' if warns else ' / ✅ 이상 없음'))
        all_jobs += jobs
        all_meters += meters
        all_warns += [f'{y}: {w}' for w in warns]

    with open(OUT / 'jobs_all.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(COLS); w.writerows(all_jobs)
    with open(OUT / 'meter_all.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['연', '월', '일', '설비', '계기A', '계기B', '차이'])
        w.writerows(all_meters)

    print(f'\n합계: 작업 {len(all_jobs)}건 / 수량 {sum(r[13] for r in all_jobs):,}개')
    print(f'출력: {OUT}')
    if all_warns:
        print(f'\n⚠️ 경고 {len(all_warns)}건:')
        for w in all_warns[:20]:
            print('  -', w)


if __name__ == '__main__':
    args = [int(a) for a in sys.argv[1:] if a.isdigit()]
    main(args or list(range(2022, datetime.date.today().year + 1)))
