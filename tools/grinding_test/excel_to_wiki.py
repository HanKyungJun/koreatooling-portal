"""
연삭 테스트 Excel → Wiki .md 변환기
사용법: run.bat  또는  python excel_to_wiki.py [엑셀파일경로]
       파일 미지정 시 같은 폴더의 grinding_test_input.xlsx 사용
"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import openpyxl
from datetime import datetime

HERE      = os.path.dirname(os.path.abspath(__file__))        # tools/grinding_test/
ROOT      = os.path.dirname(os.path.dirname(HERE))            # cnc-wiki/
TMPL_PATH = os.path.join(HERE, 'grinding_test_input.xlsx')    # 같은 폴더
OUT_DIR   = os.path.join(ROOT, 'wiki', 'measurements')        # cnc-wiki/wiki/measurements/

FIELDS = [
    'test_date', 'material', 'wheel_spec', 'wheel_grade',
    'spindle_rpm', 'wheel_vc', 'feed_rate', 'depth_ae',
    'ra_measured', 'measure_tool', 'result', 'notes',
]

LABEL_KO = {
    'test_date':    '테스트 날짜',
    'material':     '소재',
    'wheel_spec':   '휠 규격',
    'wheel_grade':  '휠 사양',
    'spindle_rpm':  '주축 RPM',
    'wheel_vc':     '휠 Vc (m/s)',
    'feed_rate':    '이송 속도 (mm/min)',
    'depth_ae':     '절입 깊이 ae (mm)',
    'ra_measured':  '측정 Ra (μm)',
    'measure_tool': '측정 장비',
    'result':       '결과 판정',
    'notes':        '비고',
}

RESULT_TAG = {'합격': 'pass', '불합격': 'fail', '추가테스트': 'retest'}


def read_excel(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    data = {}
    for i, key in enumerate(FIELDS):
        val = ws.cell(row=i + 3, column=3).value  # C열 3행~(1행=제목, 2행=헤더)
        data[key] = str(val).strip() if val is not None else ''
    return data


def safe_filename(s):
    return re.sub(r'[\\/:*?"<>|×]', '', s).replace(' ', '_')


def build_markdown(d):
    date_str    = d.get('test_date', '')
    material    = d.get('material', '')
    wheel_spec  = d.get('wheel_spec', '')
    result      = d.get('result', '')
    result_en   = RESULT_TAG.get(result, 'unknown')
    result_icon = {'합격': '✅', '불합격': '❌', '추가테스트': '🔄'}.get(result, '❓')

    frontmatter = (
        '---\n'
        f'date: {date_str}\n'
        f'material: "{material}"\n'
        f'wheel_spec: "{wheel_spec}"\n'
        f'wheel_grade: "{d.get("wheel_grade", "")}"\n'
        f'spindle_rpm: {d.get("spindle_rpm", "")}\n'
        f'wheel_vc: {d.get("wheel_vc", "")}\n'
        f'feed_rate: {d.get("feed_rate", "")}\n'
        f'depth_ae: {d.get("depth_ae", "")}\n'
        f'ra_measured: {d.get("ra_measured", "")}\n'
        f'measure_tool: "{d.get("measure_tool", "")}"\n'
        f'result: {result_en}\n'
        f'tags: [측정, {material}, {result_en}]\n'
        '---\n'
    )

    body = (
        f'# 연삭 테스트 — {date_str} ({material} / {wheel_spec})\n\n'
        f'## 테스트 조건\n\n'
        f'| 항목 | 값 |\n|------|----|\n'
    )
    for key in ['material', 'wheel_spec', 'wheel_grade',
                'spindle_rpm', 'wheel_vc', 'feed_rate', 'depth_ae']:
        body += f'| {LABEL_KO[key]} | {d.get(key, "-")} |\n'

    body += (
        f'\n## 측정 결과\n\n'
        f'| 항목 | 값 |\n|------|----|\n'
        f'| 측정 Ra (μm) | **{d.get("ra_measured", "-")}** |\n'
        f'| 측정 장비 | {d.get("measure_tool", "-")} |\n'
        f'| 결과 판정 | {result_icon} **{result}** |\n'
    )

    notes = d.get('notes', '').strip()
    if notes:
        body += f'\n## 비고\n\n{notes}\n'

    body += f'\n---\n*생성: {datetime.now().strftime("%Y-%m-%d %H:%M")} — excel_to_wiki.py*\n'
    return frontmatter + '\n' + body


def main():
    xlsx_path = sys.argv[1] if len(sys.argv) > 1 else TMPL_PATH

    if not os.path.exists(xlsx_path):
        print(f'❌ 파일을 찾을 수 없습니다: {xlsx_path}')
        sys.exit(1)

    print(f'읽는 중: {xlsx_path}')
    data = read_excel(xlsx_path)

    date_str   = data.get('test_date', datetime.now().strftime('%Y-%m-%d'))
    material   = safe_filename(data.get('material', 'unknown'))
    wheel_spec = safe_filename(data.get('wheel_spec', 'unknown'))

    fname   = f'{date_str}_{material}_{wheel_spec}.md'
    outpath = os.path.join(OUT_DIR, fname)

    os.makedirs(OUT_DIR, exist_ok=True)
    md = build_markdown(data)
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f'✅ 저장 완료: wiki/measurements/{fname}')


if __name__ == '__main__':
    main()
