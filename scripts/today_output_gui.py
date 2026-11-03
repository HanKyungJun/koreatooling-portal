"""재연마 NC 생산량 상세 — 창 프로그램 (ERP 작업실적 읽기 전용 · 수동 새로고침).

실행: cnc-wiki 폴더의 「생산량보기.bat」 더블클릭  (또는  pythonw scripts\\today_output_gui.py)
  - 새로고침(F5)을 누를 때만 ERP 를 읽는다(자동 갱신 없음 — 2026-11-02 한경준님 결정).
  - F5 = 빠른 조회: 지난 날은 일일보고 저장본(erp/snapshot), 오늘(저장본 이후)만 ERP. 「전체 다시 읽기」(Shift+F5) = 이번 달 전체 ERP.
  - 같은 달 안에서 날짜를 앞으로 옮기면 이미 읽은 결과를 다시 쓴다(ERP 재조회 없음). 최신은 F5.
  - 계산은 scripts/today_output.py 의 compute() 와 같다(콘솔 화면과 같은 숫자).
  - 결과 파일을 쓰지 않는다. 「표 복사」는 지금 보이는 표를 클립보드로(엑셀에 붙여넣기용).
  - 시험: python scripts\\today_output_gui.py --date 2026-10-30 --csv erp\\snapshot\\pw_nc_2026-10-01_2026-10-30.csv
신뢰도: 수량 = ERP 입력값(속보값) · 추정 시간 = 표준공수 DB 중앙값 × 개수(추정값 · 참고용)
2026-11-02 Cowork 신설.
"""
import sys, datetime, threading, traceback, argparse, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

KST = datetime.timezone(datetime.timedelta(hours=9))

# 회사 문서 B 안 색(코고툴 디자인 시스템 · 사내 문서 절)
BLACK = '#231f20'
ORANGE = '#e8581c'
LAVENDER = '#e4e0f0'
BOX = '#d7d2e9'
CREAM = '#fffbe5'
BAD_BG = '#fde4dc'
CARD = '#f7f6fa'
GRAY = '#6b6b6b'
STRIPE = '#f2f0f7'     # 짝수 줄 배경(줄무늬)
GRID = '#cfc9e0'       # 열 구분선
WHITE = '#ffffff'


def _hm(m):
    m = int(round(m or 0))
    return f'{m // 60}시간 {m % 60:02d}분' if m >= 60 else f'{m}분'


def _isna(v):
    try:
        return v is None or v != v
    except Exception:
        return False


class App:
    def __init__(self, root, csv=None, date=None):
        self.root, self.csv = root, csv
        self.cache = None            # (연월, 조회 끝날, 원본 df, 조회 시각, 출처, 걸린 초)
        self._grid_job = {}          # 세로선 다시 그리기 예약(창 크기 바꿀 때 몰아서 한 번)
        self.busy = False
        self.to = None               # today_output 모듈(늦게 읽음 — 창을 먼저 띄우려고)
        root.title('재연마 NC 생산량 — ERP 작업실적')
        root.geometry('1320x820')
        root.minsize(1000, 600)
        root.configure(bg=WHITE)
        fams = set(tkfont.families())
        self.ff = next((x for x in ('맑은 고딕', 'Malgun Gothic', 'Noto Sans CJK KR') if x in fams), 'TkDefaultFont')
        self._style()
        self._build()
        d = datetime.date.fromisoformat(date) if date else datetime.datetime.now(KST).date()
        self.date_var.set(d.isoformat())
        root.bind('<F5>', lambda e: self.refresh(force=True))
        root.bind('<Shift-F5>', lambda e: self.refresh(force=True, full=True))
        root.after(100, lambda: self.refresh(force=True))

    # ── 모양 ──
    def _style(self):
        s = ttk.Style()
        try:
            s.theme_use('clam')
        except tk.TclError:
            pass
        f = self.ff
        s.configure('.', font=(f, 10), background=WHITE)
        s.configure('TFrame', background=WHITE)
        s.configure('TLabel', background=WHITE)
        s.configure('TCheckbutton', background=WHITE)
        s.configure('TButton', padding=(10, 4))
        s.configure('Accent.TButton', background=BLACK, foreground=WHITE)
        s.map('Accent.TButton', background=[('active', '#3a3536'), ('disabled', '#9a9696')])
        s.configure('Treeview', rowheight=26, font=(f, 10), background=WHITE, fieldbackground=WHITE)
        s.configure('Treeview.Heading', font=(f, 10, 'bold'), background=LAVENDER, foreground=BLACK, relief='flat')
        s.map('Treeview.Heading', background=[('active', BOX)])
        s.map('Treeview', background=[('selected', BOX)], foreground=[('selected', BLACK)])
        s.configure('TNotebook', background=WHITE, borderwidth=0)
        s.configure('TNotebook.Tab', font=(f, 10), padding=(14, 6), background='#f1f0f4')
        s.map('TNotebook.Tab', background=[('selected', WHITE)], foreground=[('selected', ORANGE)])

    def _build(self):
        f = self.ff
        top = tk.Frame(self.root, bg=BLACK)
        top.pack(fill='x')
        tk.Label(top, text='▶', bg=BLACK, fg=ORANGE, font=(f, 13, 'bold')).pack(side='left', padx=(16, 4), pady=8)
        tk.Label(top, text='재연마 NC 생산량', bg=BLACK, fg=WHITE, font=(f, 15, 'bold')).pack(side='left', pady=8)
        tk.Label(top, text='ERP 작업실적 · 속보값(입력분만)', bg=BLACK, fg='#c9c5c6', font=(f, 10)).pack(side='left', padx=12)
        self.status = tk.Label(top, text='', bg=BLACK, fg='#c9c5c6', font=(f, 10))
        self.status.pack(side='right', padx=16)

        bar = ttk.Frame(self.root, padding=(16, 10, 16, 4))
        bar.pack(fill='x')
        ttk.Button(bar, text='◀ 전날', command=lambda: self.shift(-1)).pack(side='left')
        self.date_var = tk.StringVar()
        e = ttk.Entry(bar, textvariable=self.date_var, width=12, font=(f, 12), justify='center')
        e.pack(side='left', padx=6)
        e.bind('<Return>', lambda ev: self.refresh())
        ttk.Button(bar, text='다음날 ▶', command=lambda: self.shift(1)).pack(side='left')
        ttk.Button(bar, text='오늘', command=self.today).pack(side='left', padx=(6, 0))
        self.btn = ttk.Button(bar, text='새로고침 (F5)', style='Accent.TButton', command=lambda: self.refresh(force=True))
        self.btn.pack(side='left', padx=(14, 0))
        self.btn_full = ttk.Button(bar, text='전체 다시 읽기', command=lambda: self.refresh(force=True, full=True))
        self.btn_full.pack(side='left', padx=(6, 0))
        self.topmost = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text='항상 위', variable=self.topmost,
                        command=lambda: self.root.attributes('-topmost', self.topmost.get())).pack(side='left', padx=14)
        ttk.Button(bar, text='표 복사 (엑셀 붙여넣기용)', command=self.copy_table).pack(side='right')

        # 요약 카드
        cards = ttk.Frame(self.root, padding=(16, 6, 16, 2))
        cards.pack(fill='x')
        self.card = {}
        for i, (k, lab) in enumerate([('qty', '합계'), ('ok', '양품'), ('bad', '불량'), ('avg', '월평균 대비'),
                                      ('est', '추정 가공시간'), ('last', '마지막 실적 입력')]):
            c = tk.Frame(cards, bg=CARD, highlightbackground=BOX, highlightthickness=1)
            c.grid(row=0, column=i, sticky='nsew', padx=(0 if i == 0 else 8, 0))
            cards.columnconfigure(i, weight=1, uniform='card')
            tk.Label(c, text=lab, bg=CARD, fg=GRAY, font=(f, 9)).pack(anchor='w', padx=12, pady=(8, 0))
            v = tk.Label(c, text='-', bg=CARD, fg=BLACK, font=(f, 20, 'bold'))
            v.pack(anchor='w', padx=12)
            sub = tk.Label(c, text='', bg=CARD, fg=GRAY, font=(f, 9))
            sub.pack(anchor='w', padx=12, pady=(0, 8))
            self.card[k] = (v, sub)
        self.info = ttk.Label(self.root, text='', foreground=GRAY, padding=(16, 4, 16, 0))
        self.info.pack(fill='x')

        # 아래 경고 줄을 먼저 붙여야 창을 줄여도 안 잘린다
        foot = tk.Frame(self.root, bg=CREAM, highlightbackground='#e9dfa8', highlightthickness=1)
        foot.pack(side='bottom', fill='x', padx=16, pady=(2, 12))
        warn = tk.Label(foot, bg=CREAM, fg=BLACK, font=(f, 9), justify='left', anchor='w',
                 text='경고: 수량은 ERP 에 입력된 만큼만 나오는 속보값입니다. 추정 시간은 표준공수 DB 중앙값 × 개수로 낸 '
                      '추정값(참고용)이며 실제 가공시간이 아닙니다.  시각 = 실적 시작 입력(fr_tm) · * = 다음 날 이후 입력 · '
                      '분홍 줄 = 불량 있음 · 회색 글자 · 「기타」 탭 = 표준공수 DB 에 맞는 품목이 없어 추정 시간에서 빠진 품목')
        warn.pack(fill='x', padx=10, pady=5)
        foot.bind('<Configure>', lambda e: warn.config(wraplength=max(300, e.width - 24)))

        # 탭
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill='both', expand=True, padx=16, pady=(6, 4))
        self.trees = {}
        self.trees['rows'] = self._tree('목록', [
            ('no', 'No', 44, 'e'), ('mc', '설비', 80, 'center'), ('tm', '시각', 64, 'center'), ('mng', '관리번호', 110, 'w'),
            ('item', '품목(날/형상/지름/소재)', 200, 'w'), ('coat', '코팅', 110, 'w'), ('ang', '각도', 60, 'center'),
            ('ok', '양품', 60, 'e'), ('bad', '불량', 60, 'e'), ('sec', '초/개', 70, 'e'), ('est', '추정(분)', 80, 'e'),
            ('basis', '표준 기준', 130, 'w'), ('wo', '작업지시', 110, 'center')])
        gcols = [('k', '구분', 160, 'w'), ('rows', '줄', 60, 'e'), ('ok', '양품', 70, 'e'), ('bad', '불량', 60, 'e'),
                 ('qty', '합계', 70, 'e'), ('pct', '비율', 70, 'e'), ('est', '추정 시간', 110, 'e'), ('bar', '', 420, 'w')]
        for k, lab in (('shape', '형상'), ('band', '지름'), ('coat', '코팅'), ('hour', '시간')):
            self.trees[k] = self._tree(lab, gcols)
        self.trees['badrows'] = self._tree('불량', [
            ('tm', '시각', 64, 'center'), ('mng', '관리번호', 110, 'w'), ('item', '품목', 210, 'w'), ('coat', '코팅', 110, 'w'),
            ('ok', '양품', 60, 'e'), ('bad', '불량', 60, 'e'), ('wo', '작업지시', 120, 'center'), ('nm', 'ERP 품목명', 320, 'w')])
        self.trees['nostd'] = self._tree('기타', [
            ('mng', '관리번호', 110, 'w'), ('nm', 'ERP 품목명', 360, 'w'), ('qty', '개수', 70, 'e'), ('basis', '사유', 300, 'w')])

    def _tree(self, title, cols):
        fr = ttk.Frame(self.nb)
        self.nb.add(fr, text=title)
        tv = ttk.Treeview(fr, columns=[c[0] for c in cols], show='headings', selectmode='extended')
        for key, lab, w, anc in cols:
            tv.heading(key, text=lab, command=lambda k=key, t=tv: self.sort(t, k))
            tv.column(key, width=w, minwidth=40, anchor=anc, stretch=(key in ('item', 'nm', 'bar', 'basis')))
        sb = ttk.Scrollbar(fr, orient='vertical', command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')          # 스크롤바를 먼저 붙여야 창을 줄여도 안 밀려남
        tv.pack(side='left', fill='both', expand=True)
        tv.tag_configure('odd', background=STRIPE)
        tv.tag_configure('bad', background=BAD_BG)
        tv.tag_configure('sub', background=LAVENDER, font=(self.ff, 10, 'bold'))
        tv.tag_configure('nostd', foreground=GRAY)
        tv.cols, tv.title_ = cols, title
        tv.vlines = []
        tv.bind('<Configure>', lambda e, t=tv: self._grid_later(t))
        tv.bind('<ButtonRelease-1>', lambda e, t=tv: self._grid_later(t), add='+')
        return tv

    def _grid_later(self, tv):
        """창 크기를 끄는 동안 이벤트가 수십 번 오므로 마지막 한 번만 그린다(60 ms 몰기)."""
        job = self._grid_job.get(tv)
        if job:
            self.root.after_cancel(job)
        self._grid_job[tv] = self.root.after(60, lambda: self._grid(tv))

    def _grid(self, tv):
        """열 경계에 1 px 세로선(ttk 표는 격자선이 없어 직접 그린다). 선은 지우지 않고 옮겨 쓴다."""
        self._grid_job.pop(tv, None)
        xs, x, w = [], 0, tv.winfo_width()
        for c in tv['columns'][:-1]:
            x += int(tv.column(c, 'width'))
            if x >= w - 2:
                break
            xs.append(x)
        while len(tv.vlines) < len(xs):
            tv.vlines.append(tk.Frame(tv, bg=GRID, width=1))
        for i, ln in enumerate(tv.vlines):
            if i < len(xs):
                ln.place(x=xs[i] - 1, y=0, width=1, relheight=1)
            else:
                ln.place_forget()

    @staticmethod
    def _stripe(tv):
        """한 줄 걸러 배경색(불량 · 소계 줄은 제 색 유지)."""
        for n, i in enumerate(tv.get_children('')):
            tags = [t for t in tv.item(i, 'tags') if t != 'odd']
            if n % 2 and not ({'bad', 'sub'} & set(tags)):
                tags.append('odd')
            tv.item(i, tags=tags)

    # ── 동작 ──
    def _date(self):
        try:
            return datetime.date.fromisoformat(self.date_var.get().strip())
        except ValueError:
            messagebox.showwarning('날짜', '날짜는 YYYY-MM-DD 형식으로 넣어 주세요.')
            return None

    def shift(self, n):
        d = self._date()
        if d:
            self.date_var.set((d + datetime.timedelta(days=n)).isoformat())
            self.refresh()

    def today(self):
        self.date_var.set(datetime.datetime.now(KST).date().isoformat())
        self.refresh()

    def refresh(self, force=False, full=False):
        d = self._date()
        if not d or self.busy:
            return
        c = self.cache
        if not force and c and c[0] == (d.year, d.month) and c[1] >= d:
            self._render(d, c[2], c[3], c[4], reused=True, secs=c[5])
            return
        self.busy = True
        self.btn.state(['disabled'])
        self.btn_full.state(['disabled'])
        self.status.config(fg='#ffd27a', text=f'{d} 조회 중… ' + ('이번 달 전체 ERP — 1분 가까이 걸릴 수 있음' if full
                                                                 else '저장본 + 오늘분 ERP'))
        threading.Thread(target=self._work, args=(d, full), daemon=True).start()

    def _work(self, d, full=False):
        try:
            if self.to is None:
                import today_output as to
                self.to = to
            info = {}
            t0 = time.perf_counter()
            df = self.to.load(d, self.csv, full=full, info=info)
            secs = time.perf_counter() - t0
            at = datetime.datetime.now(KST)
            src = info.get('src', 'ERP')
            self.root.after(0, lambda: self._done(d, df, at, src, secs))
        except Exception as e:
            msg, tb = f'{type(e).__name__}: {e}', traceback.format_exc()
            self.root.after(0, lambda: self._fail(msg, tb))

    def _done(self, d, df, at, src, secs=None):
        self.busy = False
        self.btn.state(['!disabled'])
        self.btn_full.state(['!disabled'])
        self.cache = ((d.year, d.month), d, df, at, src, secs)
        try:
            self._render(d, df, at, src, secs=secs)
        except Exception as e:
            self._fail(f'{type(e).__name__}: {e}', traceback.format_exc())

    def _fail(self, msg, tb):
        self.busy = False
        self.btn.state(['!disabled'])
        self.btn_full.state(['!disabled'])
        self.status.config(text=f'조회 실패 — {msg[:80]}', fg='#ff9b8a')
        messagebox.showerror('ERP 조회 실패', f'{msg}\n\n사내망 · ERP 접속 상태를 확인하고 F5 로 다시 시도하세요.\n\n{tb[-1200:]}')

    def _clear(self):
        for tv in self.trees.values():
            tv.delete(*tv.get_children())
        for v, sub in self.card.values():
            v.config(text='-', fg=BLACK)
            sub.config(text='')
        self.info.config(text='')
        self.nb.tab(5, text='불량')
        self.nb.tab(6, text='기타')

    def _render(self, d, df_raw, at, src='ERP', reused=False, secs=None):
        to = self.to
        self._clear()
        self.status.config(fg='#c9c5c6', text=f'{d} · {src} · 조회 {at:%H:%M:%S} KST'
                           + (f' · {secs:.1f} s' if secs is not None else '')
                           + (' · 받아 둔 결과(최신은 F5)' if reused else ''))
        if df_raw is None or not len(df_raw):
            self.info.config(text='이번 달 실적 없음')
            return
        df = df_raw[df_raw['work_dt'].map(to._day) <= d]
        df, t = to.prepare(df, d)
        if not len(t):
            self.info.config(text=f'{d} 에 입력된 실적 없음 (휴무일이거나 아직 입력 전)')
            return
        r = to.compute(d, df, t)
        C = self.card
        C['qty'][0].config(text=f"{r['qty']:,} 개")
        C['qty'][1].config(text=f"작업지시 {r['wo']} 건 · 실적 {r['rows']} 줄")
        C['ok'][0].config(text=f"{r['ok']:,} 개")
        C['ok'][1].config(text=f"품목 {r['items']} 종 · 수주 {r['so']} 건")
        C['bad'][0].config(text=f"{r['bad']:,} 개", fg=(ORANGE if r['bad'] else BLACK))
        C['bad'][1].config(text=f"불량률 {r['rate']:.1f} %")
        if r['avg']:
            C['avg'][0].config(text=f"{r['qty'] / r['avg'] * 100:.0f} %")
            C['avg'][1].config(text=f"{d.month}월 평균 {r['avg']:,.0f} 개 (이전 {r['prev_days']}일)")
        else:
            C['avg'][1].config(text='이번 달 첫 작업일')
        if r['est_tot']:
            C['est'][0].config(text=_hm(r['est_tot']))
            C['est'][1].config(text='추정값 · 참고용' + (f" · 표준 없음 {r['no_std']} 줄 제외" if r['no_std'] else ''))
        else:
            C['est'][1].config(text='표준공수 DB 읽기 실패' if r['std_err'] else '-')
        C['last'][0].config(text=r['last_input'][11:16] or '-')
        C['last'][1].config(text=r['last_input'][:10])
        info = (f"{d.month}월 누계(작업일 {r['m_days']}일)  양품 {r['m_ok']:,} 개 · 불량 {r['m_bad']:,} 개 · "
                f"불량률 {r['m_bad'] / max(1, r['m_ok'] + r['m_bad']) * 100:.1f} %")
        if r['prev_day']:
            info += f"     전 작업일 {r['prev_day']}  {r['prev_qty']:,} 개"
        if r['std_err']:
            info += f"     표준공수 DB 읽기 실패: {r['std_err'][:60]}"
        self.info.config(text=info)

        # 실적 목록(설비별 · 시각 순 + 설비 소계)
        tv = self.trees['rows']
        n = 0
        for mc, g in t.sort_values(['mc_cd', 'tm', 'mdt_s']).groupby('mc_cd', sort=True):
            for _, x in g.iterrows():
                n += 1
                tags = (['bad'] if x['bad'] > 0 else []) + (['nostd'] if _isna(x['sec']) else [])
                tv.insert('', 'end', tags=tags, values=(
                    n, mc, x['tm'] + ('*' if x['late'] else ''), x['mng_no'], x['item'], x['coat'], x['angle'],
                    int(x['ok']), int(x['bad']) or '', '-' if _isna(x['sec']) else f"{x['sec']:.0f}",
                    f"{x['est_min']:.0f}" if x['est_min'] else '-',
                    str(x['basis']).replace(' · 라핑 근사', '(라핑근사)'), x['wo_no']))
            est = g['est_min'].sum()
            tv.insert('', 'end', tags=('sub',), values=(
                '', mc, '', '소계', f'{len(g)} 줄 · 합계 {int(g["qty"].sum()):,} 개', '', '', f"{int(g['ok'].sum()):,}",
                int(g['bad'].sum()), '', f'{est:.0f}' if est else '-', _hm(est) if est else '', ''))

        # 나눠 보기
        for k in ('shape', 'band', 'coat', 'hour'):
            g = r['groups'][k]
            tv = self.trees[k]
            mx = max(1, g['qty'].max())
            for key, x in g.iterrows():
                tv.insert('', 'end', tags=(('bad',) if x['bad'] > 0 else ()), values=(
                    f'{key}시' if k == 'hour' else (f'{key} mm' if k == 'band' and key != '규격 밖' else key), int(x['rows']), f"{int(x['ok']):,}", int(x['bad']),
                    f"{int(x['qty']):,}", f"{x['pct']:.0f} %", _hm(x['est']) if x['est'] else '-',
                    '█' * max(1, int(round(x['qty'] / mx * 40)))))

        b = t[t['bad'] > 0]
        for _, x in b.iterrows():
            self.trees['badrows'].insert('', 'end', tags=('bad',), values=(
                x['tm'], x['mng_no'], x['item'], x['coat'], int(x['ok']), int(x['bad']), x['wo_no'], x['itm_nm']))
        self.nb.tab(5, text=f'불량 ({len(b)})')
        xs = t[t['sec'].isna()]
        for _, x in xs.iterrows():
            self.trees['nostd'].insert('', 'end', values=(x['mng_no'], x['itm_nm'], int(x['qty']), x['basis']))
        self.nb.tab(6, text=f'기타 ({len(xs)})')
        for tv in self.trees.values():
            self._stripe(tv)

    def sort(self, tv, key):
        rev = getattr(tv, 'rev_', {}).get(key, False)
        kids = tv.get_children('')
        items = [i for i in kids if 'sub' not in tv.item(i, 'tags')]
        subs = [i for i in kids if 'sub' in tv.item(i, 'tags')]

        def val(i):
            v = str(tv.set(i, key)).replace(',', '').replace('%', '').replace('*', '').strip()
            try:
                return (0, float(v), '')
            except ValueError:
                return (1, 0.0, v)
        items.sort(key=val, reverse=rev)
        for n, i in enumerate(items + subs):
            tv.move(i, '', n)
        self._stripe(tv)
        tv.rev_ = {**getattr(tv, 'rev_', {}), key: not rev}

    def copy_table(self):
        tv = list(self.trees.values())[self.nb.index('current')]
        lines = ['\t'.join(c[1] or '막대' for c in tv.cols)]
        for i in tv.get_children(''):
            lines.append('\t'.join(str(v) for v in tv.item(i, 'values')))
        self.root.clipboard_clear()
        self.root.clipboard_append('\n'.join(lines))
        self.status.config(text=f'「{tv.title_}」 표 {len(lines) - 1} 줄 복사함 — 엑셀에 붙여넣기', fg='#c9c5c6')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date')
    ap.add_argument('--csv')
    a = ap.parse_args()
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)     # 고해상도 화면 글자 흐림 방지
        except Exception:
            pass
    root = tk.Tk()
    try:
        App(root, csv=a.csv, date=a.date)
    except Exception:
        messagebox.showerror('시작 실패', traceback.format_exc()[-1500:])
        raise
    root.mainloop()


if __name__ == '__main__':
    main()
