"""재연마 정가 조회 — 사내 시험판 (Windows 창 프로그램, 2026-10-29 Cowork)

실행: 정가조회_실행.bat 더블클릭 (또는 pythonw 정가조회.pyw) · exe: exe만들기.bat
데이터: price_data.json — 정가만(할인율 · 거래처 단가 없음). 찾는 순서
  ① 같은 폴더의 정가조회_설정.ini 의 [데이터] 경로=  (예: 사내 공유 폴더 — 데이터만 바꾸면 모든 PC 반영)
  ② 프로그램과 같은 폴더의 price_data.json
조회 규칙은 price_core.py(= 웹 위젯 price_lookup_core.js 와 같은 규칙).
"""
import configparser
import datetime
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

if getattr(sys, 'frozen', False):          # exe 로 묶였을 때 — exe 가 있는 폴더 기준
    HERE = os.path.dirname(sys.executable)
    sys.path.insert(0, getattr(sys, '_MEIPASS', HERE))
else:
    HERE = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, HERE)
from price_core import COAT_LABEL, PriceCore, g  # noqa: E402

APP = '재연마 정가 조회'
FONT = '맑은 고딕' if sys.platform.startswith('win') else 'Noto Sans CJK KR'
SHAPES = [('평', '평(스퀘어) 엔드밀'), ('볼', '볼 엔드밀'), ('코너', '코너R 엔드밀'), ('라핑평', '라핑 평'), ('라핑볼', '라핑 볼'),
          ('라핑코너', '라핑 코너R'), ('리머', '리머'), ('드릴', '드릴')]
PARTS = [('밑날', '밑날'), ('밑옆날', '밑날 + 옆날(외경)'), ('옆날', '옆날(외경)'), ('골수리', '골수리')]
COATS = [('비코팅', '비코팅'), ('일반코팅', '일반 코팅'), ('고경도코팅', '고경도 코팅')]
MATS = [('초경', '초경'), ('HSS', 'HSS(하이스)')]
EXAMPLES = ['10파이 2날 볼 고경도', 'D6 4날 평 밑옆날 일반코팅', '드릴 6.8 HSS 비코팅 2날', '하이스 라핑 볼 16mm 두날 코팅']


def find_data():
    ini = os.path.join(HERE, '정가조회_설정.ini')
    if os.path.exists(ini):
        cp = configparser.ConfigParser()
        cp.read(ini, encoding='utf-8')
        p = cp.get('데이터', '경로', fallback='').strip().strip('"')
        if p:
            if os.path.isdir(p):
                p = os.path.join(p, 'price_data.json')
            if os.path.exists(p):
                return p
            messagebox.showwarning(APP, f'설정 파일의 데이터 경로를 찾을 수 없습니다.\n{p}\n\n프로그램 폴더의 price_data.json 을 대신 엽니다.')
    p = os.path.join(HERE, 'price_data.json')
    return p if os.path.exists(p) else None


class App(tk.Tk):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.title(f'{APP} (사내 시험판)')
        self.geometry('860x700')
        self.minsize(640, 480)
        st = ttk.Style(self)
        for w in ('TLabel', 'TButton', 'TCombobox', 'TEntry', 'TNotebook.Tab', 'Treeview'):
            st.configure(w, font=(FONT, 11))
        st.configure('Treeview', rowheight=28)
        st.configure('Treeview.Heading', font=(FONT, 10, 'bold'))
        st.configure('Title.TLabel', font=(FONT, 15, 'bold'))
        st.configure('Sub.TLabel', font=(FONT, 10), foreground='#5d6675')
        st.configure('Warn.TLabel', font=(FONT, 10), foreground='#b25b00')

        top = ttk.Frame(self, padding=(14, 12, 14, 4)); top.pack(fill='x')
        ttk.Label(top, text=APP, style='Title.TLabel').pack(anchor='w')
        ttk.Label(top, text='정가표 기준 정가(할인 적용 전) · 「확인 필요」 · 「없음」 은 담당자 확인', style='Sub.TLabel').pack(anchor='w')

        nb = ttk.Notebook(self); nb.pack(fill='x', padx=14, pady=(6, 4))
        # ── 항목 선택 ──
        f1 = ttk.Frame(nb, padding=10); nb.add(f1, text='  항목 선택  ')
        self.v = {}
        specs = [('재질', 'mat', MATS, '초경'), ('형상', 'shape', SHAPES, '평'), ('날 수', 'blade', [(str(n), f'{n}날') for n in range(1, 7)], '2'),
                 ('작업 부위', 'part', PARTS, '밑날'), ('코팅', 'coat', COATS, '비코팅')]
        self.maps = {}
        for i, (lab, k, opts, dflt) in enumerate(specs):
            r, c = divmod(i, 3)
            ttk.Label(f1, text=lab, style='Sub.TLabel').grid(row=r * 2, column=c, sticky='w', padx=4)
            self.maps[k] = {t: v for v, t in opts}
            var = tk.StringVar(value=dict(opts)[dflt])
            cb = ttk.Combobox(f1, textvariable=var, values=[t for _, t in opts], state='readonly', width=18)
            cb.grid(row=r * 2 + 1, column=c, sticky='we', padx=4, pady=(0, 8))
            self.v[k] = var
            if k == 'shape':
                cb.bind('<<ComboboxSelected>>', self._shape_changed)
        ttk.Label(f1, text='날경 Ø (mm)', style='Sub.TLabel').grid(row=2, column=2, sticky='w', padx=4)
        self.dia = tk.StringVar()
        e = ttk.Entry(f1, textvariable=self.dia, width=18); e.grid(row=3, column=2, sticky='we', padx=4, pady=(0, 8))
        e.bind('<Return>', lambda _e: self.run_pick())
        for c in range(3):
            f1.columnconfigure(c, weight=1)
        ttk.Button(f1, text='정가 보기', command=self.run_pick).grid(row=4, column=0, columnspan=3, sticky='we', padx=4, pady=(4, 0))
        # ── 문장 입력 ──
        f2 = ttk.Frame(nb, padding=10); nb.add(f2, text='  문장으로 입력  ')
        self.q = tk.StringVar()
        row = ttk.Frame(f2); row.pack(fill='x')
        qe = ttk.Entry(row, textvariable=self.q); qe.pack(side='left', fill='x', expand=True)
        qe.bind('<Return>', lambda _e: self.run_text())
        ttk.Button(row, text='조회', command=self.run_text).pack(side='left', padx=(6, 0))
        ex = ttk.Frame(f2); ex.pack(fill='x', pady=(8, 0))
        ttk.Label(ex, text='예:', style='Sub.TLabel').pack(side='left')
        for t in EXAMPLES:
            ttk.Button(ex, text=t, command=lambda t=t: (self.q.set(t), self.run_text())).pack(side='left', padx=2)
        self.nb = nb

        # ── 결과 ── (아래 줄 · 바닥글을 먼저 붙여 창이 작아도 잘리지 않게)
        d = core.data
        foot = (f"기준: {d.get('pricelist', '')} 「{d.get('sheet', '')}」 · 데이터 생성 {d.get('made', '')} · 등록 정가 {d.get('master_src', '')}\n"
                f"데이터 파일: {core.path}")
        ttk.Label(self, text=foot, style='Sub.TLabel', padding=(14, 2, 14, 10), wraplength=820, justify='left').pack(side='bottom', anchor='w')
        mid = ttk.Frame(self, padding=(14, 4)); mid.pack(fill='both', expand=True)
        self.info = ttk.Label(mid, text='', style='Sub.TLabel', wraplength=780, justify='left'); self.info.pack(anchor='w')
        self.note = ttk.Label(mid, text='', style='Warn.TLabel', wraplength=780, justify='left'); self.note.pack(anchor='w')
        cols = ('name', 'price', 'status', 'src')
        self.tv = ttk.Treeview(mid, columns=cols, show='headings', height=8)
        for c, t, w, a in (('name', '규격', 270, 'w'), ('price', '정가', 100, 'e'), ('status', '상태', 80, 'center'), ('src', '근거', 320, 'w')):
            self.tv.heading(c, text=t); self.tv.column(c, width=w, anchor=a, stretch=(c in ('name', 'src')))
        self.tv.tag_configure('ok', foreground='#1d2330')
        self.tv.tag_configure('chk', foreground='#b25b00')
        self.tv.tag_configure('no', foreground='#a12a2a')
        bar = ttk.Frame(mid); bar.pack(side='bottom', fill='x')
        self.tv.pack(fill='both', expand=True, pady=(4, 4))
        ttk.Button(bar, text='결과 복사', command=self.copy).pack(side='left')
        self.msg = ttk.Label(bar, text='', style='Sub.TLabel'); self.msg.pack(side='left', padx=8)

        self.rows = []

    def _shape_changed(self, _e=None):
        if self.maps['shape'].get(self.v['shape'].get()) == '드릴':
            self.v['blade'].set('2날'); self.v['part'].set('밑날')

    def _val(self, k):
        return self.maps[k][self.v[k].get()]

    def show(self, rows, q=None):
        self.tv.delete(*self.tv.get_children())
        self.note.configure(text='')
        self.rows = rows
        if q is not None:
            lab = (('blade', '날수'), ('shape', '형상'), ('dia', '날경'), ('mat', '재질'), ('part', '가공부'), ('coat', '코팅'))
            def fmt(k, v):
                if v is None:
                    return '—'
                return f'Ø{g(v)} mm' if k == 'dia' else f'{v}날' if k == 'blade' else COAT_LABEL.get(v, v) if k == 'coat' else v
            self.info.configure(text='해석: ' + ' · '.join(f'{t} {fmt(k, q.get(k))}' for k, t in lab))
            if q.get('missing'):
                need = ', '.join({'shape': '형상(평 · 볼 · 코너 · 라핑 · 드릴 …)', 'dia': '직경(mm)'}[m] for m in q['missing'])
                self.note.configure(text=f'{need} 을(를) 함께 입력해 주세요.')
                return
            if q.get('assumed'):
                self.note.configure(text='\n'.join('※ ' + a for a in q['assumed']))
        else:
            self.info.configure(text='')
        for r in rows:
            ok = r['status'] == 'OK' and r['price'] is not None
            tag = 'ok' if ok else ('no' if r['status'] == '없음' else 'chk')
            self.tv.insert('', 'end', values=(r['name'], f"{r['price']:,.0f}원" if ok else '-', r['status'], r['src']), tags=(tag,))
        self.msg.configure(text='')

    def run_pick(self):
        try:
            d = float(self.dia.get().replace('Ø', '').replace('ø', '').strip())
        except ValueError:
            messagebox.showinfo(APP, '날경(mm)을 숫자로 입력해 주세요.'); return
        r = self.core.price_one(int(self._val('blade')), self._val('shape'), d, self._val('mat'), self._val('part'), self._val('coat'))
        self.show([r])

    def run_text(self):
        t = self.q.get().strip()
        if t:
            res = self.core.answer(t); self.show(res['rows'], res['q'])

    def copy(self):
        if not self.rows:
            return
        lines = [f"{r['name']}\t{(format(r['price'], ',.0f') + '원') if r['status'] == 'OK' and r['price'] is not None else '담당자 확인'}" for r in self.rows]
        stamp = datetime.datetime.now().strftime('%Y-%m-%d')
        self.clipboard_clear(); self.clipboard_append('\n'.join(lines) + f'\n(재연마 정가 · 할인 적용 전 · {stamp} 조회)')
        self.msg.configure(text=f'{len(lines)}줄 복사했습니다')


def main():
    root_err = None
    path = find_data()
    if not path:
        tk.Tk().withdraw()
        messagebox.showerror(APP, 'price_data.json 을 찾을 수 없습니다.\n프로그램과 같은 폴더에 두거나 정가조회_설정.ini 에 경로를 적어 주세요.')
        return
    try:
        core = PriceCore(path)
    except Exception as e:   # 데이터 파일 손상 등
        root_err = e
    if root_err:
        tk.Tk().withdraw()
        messagebox.showerror(APP, f'데이터 파일을 읽지 못했습니다.\n{path}\n{root_err}')
        return
    App(core).mainloop()


if __name__ == '__main__':
    main()
