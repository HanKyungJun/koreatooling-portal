"""
연삭 테스트 기록 앱 — 더블클릭으로 실행
"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

HERE    = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = os.path.join(ROOT, 'wiki', 'measurements')

RESULT_TAG  = {'합격': 'pass', '불합격': 'fail', '추가테스트': 'retest'}
RESULT_ICON = {'합격': '✅', '불합격': '❌', '추가테스트': '🔄'}

COLOR_BG     = '#F0F2F5'
COLOR_HEADER = '#1A3A6B'
COLOR_WHITE  = '#FFFFFF'
COLOR_PASS   = '#E8F5E9'
COLOR_FAIL   = '#FFEBEE'
COLOR_RETEST = '#FFF8E1'
COLOR_BTN    = '#1A3A6B'
COLOR_BTN_FG = '#FFFFFF'


def safe_filename(s):
    return re.sub(r'[\\/:*?"<>|×]', '', s).replace(' ', '_')


def build_markdown(d):
    date_str    = d['test_date']
    material    = d['material']
    wheel_spec  = d['wheel_spec']
    result      = d['result']
    result_en   = RESULT_TAG.get(result, 'unknown')
    result_icon = RESULT_ICON.get(result, '❓')

    frontmatter = (
        '---\n'
        f'date: {date_str}\n'
        f'material: "{material}"\n'
        f'wheel_spec: "{wheel_spec}"\n'
        f'wheel_grade: "{d["wheel_grade"]}"\n'
        f'spindle_rpm: {d["spindle_rpm"]}\n'
        f'wheel_vc: {d["wheel_vc"]}\n'
        f'feed_rate: {d["feed_rate"]}\n'
        f'depth_ae: {d["depth_ae"]}\n'
        f'ra_measured: {d["ra_measured"]}\n'
        f'measure_tool: "{d["measure_tool"]}"\n'
        f'result: {result_en}\n'
        f'tags: [측정, {material}, {result_en}]\n'
        '---\n'
    )

    body = (
        f'# 연삭 테스트 — {date_str} ({material} / {wheel_spec})\n\n'
        '## 테스트 조건\n\n'
        '| 항목 | 값 |\n|------|----|\n'
    )
    for label, key in [
        ('소재',                'material'),
        ('휠 규격',             'wheel_spec'),
        ('휠 사양',             'wheel_grade'),
        ('주축 RPM',            'spindle_rpm'),
        ('휠 Vc (m/s)',         'wheel_vc'),
        ('이송 속도 (mm/min)',  'feed_rate'),
        ('절입 깊이 ae (mm)',   'depth_ae'),
    ]:
        body += f'| {label} | {d[key] or "-"} |\n'

    body += (
        '\n## 측정 결과\n\n'
        '| 항목 | 값 |\n|------|----|\n'
        f'| 측정 Ra (μm) | **{d["ra_measured"] or "-"}** |\n'
        f'| 측정 장비 | {d["measure_tool"] or "-"} |\n'
        f'| 결과 판정 | {result_icon} **{result}** |\n'
    )

    if d['notes'].strip():
        body += f'\n## 비고\n\n{d["notes"].strip()}\n'

    body += f'\n---\n*생성: {datetime.now().strftime("%Y-%m-%d %H:%M")} — 연삭테스트 앱*\n'
    return frontmatter + '\n' + body


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('연삭 테스트 기록')
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        self._build_ui()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')

    def _build_ui(self):
        # ── 헤더
        hdr = tk.Frame(self, bg=COLOR_HEADER, pady=12)
        hdr.pack(fill='x')
        tk.Label(hdr, text='연삭 테스트 기록', font=('Segoe UI', 13, 'bold'),
                 bg=COLOR_HEADER, fg='white').pack()

        # ── 스크롤 가능 영역
        canvas = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0, width=480, height=520)
        scroll = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        frame = tk.Frame(canvas, bg=COLOR_BG, padx=24, pady=16)
        win_id = canvas.create_window((0, 0), window=frame, anchor='nw')

        def on_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind('<Configure>', on_resize)
        frame.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox('all')))
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(
            -1 if e.delta > 0 else 1, 'units'))

        self.vars = {}
        fields = [
            ('test_date',   '테스트 날짜 *',          datetime.now().strftime('%Y-%m-%d'), 'entry',    None),
            ('material',    '소재 *',                  '',  'entry',    '예) SKH51 (HSS), SKD11'),
            ('wheel_spec',  '휠 규격 *',               '',  'entry',    '예) D125×T10×H32'),
            ('wheel_grade', '휠 사양',                 '',  'entry',    '예) CBN B126 V 100%'),
            ('spindle_rpm', '주축 RPM',                '',  'entry',    '예) 4800'),
            ('wheel_vc',    '휠 Vc (m/s)',             '',  'entry',    '예) 31.4'),
            ('feed_rate',   '이송 속도 (mm/min)',       '',  'entry',    '예) 200'),
            ('depth_ae',    '절입 깊이 ae (mm)',        '',  'entry',    '예) 0.01'),
            ('ra_measured', '측정 Ra (μm) *',          '',  'entry',    '예) 0.42'),
            ('measure_tool','측정 장비',                '',  'entry',    '예) 미쓰토요 SJ-210'),
            ('result',      '결과 판정 *',             '합격', 'combo', ['합격', '불합격', '추가테스트']),
            ('notes',       '비고',                    '',  'text',     None),
        ]

        for key, label, default, widget_type, extra in fields:
            lbl_frame = tk.Frame(frame, bg=COLOR_BG)
            lbl_frame.pack(fill='x', pady=(10, 2))
            tk.Label(lbl_frame, text=label, font=('Segoe UI', 9, 'bold'),
                     bg=COLOR_BG, fg='#444').pack(anchor='w')

            if widget_type == 'entry':
                v = tk.StringVar(value=default)
                e = tk.Entry(frame, textvariable=v, font=('Segoe UI', 10),
                             relief='flat', bd=0, bg=COLOR_WHITE,
                             highlightthickness=1, highlightbackground='#DDD',
                             highlightcolor=COLOR_HEADER)
                e.pack(fill='x', ipady=6)
                if extra:
                    tk.Label(frame, text=extra, font=('Segoe UI', 8),
                             bg=COLOR_BG, fg='#AAA').pack(anchor='w')
                self.vars[key] = v

            elif widget_type == 'combo':
                v = tk.StringVar(value=default)
                style = ttk.Style()
                style.configure('Custom.TCombobox', fieldbackground=COLOR_WHITE)
                cb = ttk.Combobox(frame, textvariable=v, values=extra,
                                  state='readonly', style='Custom.TCombobox',
                                  font=('Segoe UI', 10))
                cb.pack(fill='x', ipady=4)
                cb.bind('<<ComboboxSelected>>', self._on_result_change)
                self.vars[key] = v
                self._result_combo = cb

            elif widget_type == 'text':
                t = tk.Text(frame, font=('Segoe UI', 10), height=3,
                            relief='flat', bd=0, bg=COLOR_WHITE,
                            highlightthickness=1, highlightbackground='#DDD',
                            highlightcolor=COLOR_HEADER, wrap='word')
                t.pack(fill='x')
                self.vars[key] = t

        # ── 저장 버튼
        tk.Frame(frame, bg=COLOR_BG, height=8).pack()
        self._save_btn = tk.Button(
            frame, text='저장하기  →', font=('Segoe UI', 11, 'bold'),
            bg=COLOR_BTN, fg=COLOR_BTN_FG, relief='flat',
            activebackground='#152d55', activeforeground='white',
            cursor='hand2', pady=10, command=self._save)
        self._save_btn.pack(fill='x')
        tk.Frame(frame, bg=COLOR_BG, height=16).pack()

    def _on_result_change(self, _=None):
        result = self.vars['result'].get()
        colors = {'합격': COLOR_PASS, '불합격': COLOR_FAIL, '추가테스트': COLOR_RETEST}
        self.configure(bg=colors.get(result, COLOR_BG))

    def _get_values(self):
        d = {}
        for key, var in self.vars.items():
            if isinstance(var, tk.Text):
                d[key] = var.get('1.0', 'end-1c')
            else:
                d[key] = var.get().strip()
        return d

    def _save(self):
        d = self._get_values()

        # 필수 항목 검증
        missing = [f for f, k in [('테스트 날짜', 'test_date'), ('소재', 'material'),
                                   ('휠 규격', 'wheel_spec'), ('측정 Ra', 'ra_measured'),
                                   ('결과 판정', 'result')] if not d[k]]
        if missing:
            messagebox.showwarning('입력 오류', '필수 항목을 입력하세요:\n' + ', '.join(missing))
            return

        fname = (f'{d["test_date"]}_'
                 f'{safe_filename(d["material"])}_'
                 f'{safe_filename(d["wheel_spec"])}.md')
        outpath = os.path.join(OUT_DIR, fname)

        os.makedirs(OUT_DIR, exist_ok=True)
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(build_markdown(d))

        result_icon = RESULT_ICON.get(d['result'], '')
        messagebox.showinfo('저장 완료',
                            f'{result_icon} .md 파일이 저장되었습니다.\n\n'
                            f'wiki/measurements/{fname}')
        self._reset()

    def _reset(self):
        for key, var in self.vars.items():
            if isinstance(var, tk.Text):
                var.delete('1.0', 'end')
            elif key == 'test_date':
                var.set(datetime.now().strftime('%Y-%m-%d'))
            elif key == 'result':
                var.set('합격')
            else:
                var.set('')
        self.configure(bg=COLOR_BG)


if __name__ == '__main__':
    App().mainloop()
