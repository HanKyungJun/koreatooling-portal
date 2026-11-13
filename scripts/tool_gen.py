# -*- coding: utf-8 -*-
"""tool_gen.py — 공구 도면 · 3D 생성기 (cnc-wiki, 2026-11-12 Cowork)

사양 한 줄 → ① 도면 DXF · PDF · PNG ② SolidCraft 3D 레시피(JSON, 단계별 기대 부피) ③ 사양 · 계산값 JSON.
3D 는 Claude 가 레시피대로 SolidCraft(MCP)에서 만든다 — 한 단계 90 s 제한 때문에 단계마다 저장
(wiki/cadcam/CAD-3D-프로그램-역할-정의.md §4-7).

입력 예:  EM 4날 D6 d6 L50 Lc9 R0.5 넥5.7×18 헬릭스35
  EM          엔드밀(현재 유일 지원)
  N날 · NF    날 수 2 ~ 4
  D · d       날경 · 생크경 (생크는 항상 d)
  L · Lc      전장 · 날장
  R<값> · 볼  코너 R / 볼(R = D/2). 없으면 평(스퀘어)
  넥A×B       넥 지름 A × 유효장 B(날 끝 → 넥 끝)
  헬릭스β     나선각(°), 뒤에 「좌」 = 왼나선 (기본 오른나선)
  선택: 코어NN(심압 %D) · 테이퍼NN(편측 °, 기본 15) · C<값>(생크 끝 모따기) · 번호XXX

모양 확인용 — 날 끝 형상(갭 · 끝날 여유각 · 경사각) · 홈 끝맺음 없음. 공구 형상 기준은 ANCA ToolRoom.
사용: python tool_gen.py "<사양>" --tpl <도면양식_A4가로_공구용_v1.dxf> --out <출력 상위 폴더> [--date YYYY-MM-DD] [--sc-root <Windows 경로>]
"""
import argparse, json, math, os, re, sys, datetime

VERSION = "1.6 (2026-11-13)"

# ───────────────────────── 1. 사양 해석 ─────────────────────────
class Impossible(Exception):
    """사양이 형상으로 성립하지 않음 — 우회안 없이 「불가능」으로 끝낸다."""

def _num(s):
    return float(s.replace(",", "."))

def parse_spec(text):
    t = text.strip().replace("x", "×").replace("X", "×").replace("*", "×")
    toks = t.split()
    sp = {"raw": text.strip(), "kind": None, "z": None, "D": None, "d": None, "L": None, "Lc": None,
          "R": None, "ball": False, "neck": None, "helix": None, "hand": "R",
          "core_pct": None, "taper_deg": 13.0, "C": None, "number": None, "neck_step": True, "D_tol": None, "section": "rake", "rake": 6.0, "flute_pct": 55.0}
    unknown = []
    for tok in toks:
        u = tok.upper()
        m = None
        if u in ("EM", "엔드밀"):
            sp["kind"] = "EM"
        elif (m := re.fullmatch(r"(\d)(날|F)", u)):
            sp["z"] = int(m.group(1))
        elif tok in ("볼", "BALL") or u == "BALL":
            sp["ball"] = True
        elif (m := re.fullmatch(r"LC([\d.]+)", u)):
            sp["Lc"] = _num(m.group(1))
        elif (m := re.fullmatch(r"D([\d.]+)([a-z]\d+)?", tok)):
            sp["D"] = _num(m.group(1))
            sp["D_tol"] = m.group(2)
        elif (m := re.fullmatch(r"d([\d.]+)", tok)):
            sp["d"] = _num(m.group(1))
        elif (m := re.fullmatch(r"L([\d.]+)", u)):
            sp["L"] = _num(m.group(1))
        elif (m := re.fullmatch(r"R([\d.]+)", u)):
            sp["R"] = _num(m.group(1))
        elif (m := re.fullmatch(r"넥([\d.]+)×([\d.]+)", tok)):
            sp["neck"] = (_num(m.group(1)), _num(m.group(2)))
        elif (m := re.fullmatch(r"(헬릭스|H|β)([\d.]+)°?(좌|L|우|R)?", u)):
            sp["helix"] = _num(m.group(2))
            if m.group(3) in ("좌", "L"):
                sp["hand"] = "L"
        elif tok == "단면원호":
            sp["section"] = "circle"
        elif (m := re.fullmatch(r"경사(-?[\d.]+)°?", tok)):
            sp["rake"] = _num(m.group(1))
        elif (m := re.fullmatch(r"홈각([\d.]+)%?", tok)):
            sp["flute_pct"] = _num(m.group(1))
        elif (m := re.fullmatch(r"코어([\d.]+)%?", tok)):
            sp["core_pct"] = _num(m.group(1))
        elif (m := re.fullmatch(r"테이퍼([\d.]+)°?", tok)):
            sp["taper_deg"] = _num(m.group(1))
        elif tok == "넥단직각":
            sp["neck_step"] = False
        elif (m := re.fullmatch(r"C([\d.]+)", u)):
            sp["C"] = _num(m.group(1))
        elif (m := re.fullmatch(r"번호(.+)", tok)):
            sp["number"] = m.group(1)
        else:
            unknown.append(tok)
    if unknown:
        raise Impossible("읽을 수 없는 항목: " + " ".join(unknown))
    for k, name in (("kind", "공구 종류(EM)"), ("z", "날 수"), ("D", "D"), ("d", "d"), ("L", "L"), ("Lc", "Lc"), ("helix", "헬릭스")):
        if sp[k] is None:
            raise Impossible(f"{name} 가 없습니다")
    return sp

# 홈 단면(모양 확인용 추정값): 원호 홈 1개 = 반지름 rf 원, 중심 거리 a = 심압/2 + rf
#   2날 = SMP-01(심압 60 %D · R 0.35D) · 4날 = SMP-02(심압 65 %D · R 1.3/6 D) · 3날 = 중간값
FLUTE_RULE = {2: (60.0, 0.35), 3: (62.0, 0.27), 4: (65.0, 1.3 / 6.0)}
H6_UM = [(3, 6), (6, 8), (10, 9), (18, 11), (30, 13), (50, 16)]   # ISO 286-2 h6 (IT6) — 「이하」 기준
# 축 공차 등급 한계 편차(μm, 위 · 아래) — 「이하」 기준. JIS B 0401(= ISO 286-2) 발췌표 [VEN-MIKI-JISB0401] 로 대조한 구간만.
#   3 mm 이하 e8 은 발췌표에 없어 넣지 않음(확인 필요).
SHAFT_TOL = {"h6": [(6, 0, -8), (10, 0, -9), (18, 0, -11), (30, 0, -13), (50, 0, -16)],
             "e8": [(6, -20, -38), (10, -25, -47), (18, -32, -59), (30, -40, -73), (50, -50, -89)]}

def shaft_tol(cls, size):
    """(위 편차, 아래 편차) mm. 3 초과 ~ 50 이하만."""
    if cls not in SHAFT_TOL:
        raise Impossible(f"공차 등급 {cls} 는 표에 없음 — 지원: {', '.join(SHAFT_TOL)} (확인 필요)")
    if size <= 3:
        raise Impossible(f"{cls} {size} mm — 3 mm 이하 구간은 대조한 표에 없음(확인 필요)")
    for up, es, ei in SHAFT_TOL[cls]:
        if size <= up:
            return es / 1000.0, ei / 1000.0
    raise Impossible(f"{cls} {size} mm — 50 mm 초과")

def h6(d):
    for up, um in H6_UM:
        if d <= up:
            return um / 1000.0
    raise Impossible(f"d {d} mm 는 h6 표(≤ 50 mm) 밖")

def derive(sp):
    D, d, L, Lc, z = sp["D"], sp["d"], sp["L"], sp["Lc"], sp["z"]
    if z not in FLUTE_RULE:
        raise Impossible(f"날 수 {z} — 지원 범위 2 ~ 4날")
    if min(D, d, L, Lc) <= 0:
        raise Impossible("치수는 0 보다 커야 합니다")
    if not (0 < sp["helix"] < 60):
        raise Impossible(f"헬릭스 {sp['helix']}° — 0 ~ 60° 범위 밖")
    shape = "square"
    R = sp["R"]
    if sp["ball"] or (R is not None and abs(R - D / 2) < 1e-9):
        if R is not None and abs(R - D / 2) > 1e-9:
            raise Impossible(f"볼 R{R} ≠ D/2 ({D / 2}) — 볼은 R = D/2 만 가능")
        shape, R = "ball", D / 2
    elif R is not None:
        if R >= D / 2:
            raise Impossible(f"코너 R{R} ≥ D/2 ({D / 2}) — 코너 R 은 D/2 보다 작아야 함")
        shape = "corner"
    else:
        R = 0.0
    if shape == "ball" and Lc < R:
        raise Impossible(f"볼 날장 Lc {Lc} < R {R}")
    if Lc >= L:
        raise Impossible(f"날장 Lc {Lc} ≥ 전장 L {L}")
    core_pct, rf_ratio = FLUTE_RULE[z]
    if sp["core_pct"]:
        core_pct = sp["core_pct"]
    rf = rf_ratio * D
    a = core_pct / 100.0 * D / 2 + rf
    if not (a - rf < D / 2 < a + rf):
        raise Impossible("홈 원이 외경과 만나지 않음 — 코어 % 확인")
    if 2 * a * math.sin(math.pi / z) <= 2 * rf:
        raise Impossible("홈끼리 겹침 — 코어 % 를 키우거나 날 수를 줄여야 함")
    C = sp["C"] if sp["C"] is not None else (0.5 if d >= 8 else 0.3 if d >= 4 else 0.2)
    tan_t = math.tan(math.radians(sp["taper_deg"]))
    # 생크 쪽 반경 윤곽 (z, r) — Lc 부터
    prof = []
    neck = sp["neck"]
    if neck:
        ND, NL = neck
        if ND >= D or ND >= d:
            raise Impossible(f"넥 Ø{ND} 가 D {D} · d {d} 보다 작아야 함")
        if NL <= Lc:
            raise Impossible(f"유효장 {NL} ≤ 날장 {Lc}")
        zt = NL + (d / 2 - ND / 2) / tan_t
        st = (D - ND) / 2 if sp["neck_step"] else 0.0      # 넥 → 날부 45° 단(실물 4KCR: 반경 0.08)
        if NL <= Lc + st:
            raise Impossible(f"유효장 {NL} 이 날장 + 넥 단({Lc + st:.2f}) 이하")
        prof = ([(Lc, D / 2), (Lc + st, ND / 2)] if st > 0 else [(Lc, ND / 2)]) + [(NL, ND / 2), (zt, d / 2)]
    elif abs(D - d) > 1e-9:
        zt = Lc + abs(d / 2 - D / 2) / tan_t
        prof = [(Lc, D / 2), (zt, d / 2)]
    else:
        zt = Lc
        prof = [(Lc, d / 2)]
    if zt >= L - C - 0.5:
        raise Impossible(f"생크 테이퍼 끝 {zt:.2f} 이 전장 {L} 안에 들어가지 않음")
    prof += [(L - C, d / 2), (L, d / 2 - C)]
    lead = math.pi * D / math.tan(math.radians(sp["helix"]))
    twist = 360.0 * (Lc + 2.0) / lead * (1 if sp["hand"] == "R" else -1)
    g = dict(shape=shape, R=R, z=z, D=D, d=d, L=L, Lc=Lc, core_pct=core_pct, core_d=core_pct / 100.0 * D,
             rf=rf, a=a, C=C, lead=lead, twist=twist, shank=prof, zt=zt, neck=neck,
             helix=sp["helix"], hand=sp["hand"], taper_deg=sp["taper_deg"], h6=h6(d), neck_step=sp["neck_step"],
             D_tol=sp["D_tol"], D_dev=shaft_tol(sp["D_tol"], D) if sp["D_tol"] else None,
             section=sp["section"], rake=sp["rake"])
    if g["section"] == "rake":
        if not (-10 <= g["rake"] <= 25):
            raise Impossible(f"경사각 {g['rake']}° — −10 ~ 25° 범위 밖")
        g["flute_pct"] = sp["flute_pct"]
        if not (30 <= g["flute_pct"] <= 85):
            raise Impossible(f"홈각 {g['flute_pct']} % — 피치의 30 ~ 85 % 범위 밖")
        g["rk"] = rake_geom(D / 2, g["core_d"] / 2, z, g["rake"], g["flute_pct"])
        if shape != "square":
            # v1.6 실측(2026-11-13): 홈 곡선을 이어진 원호(접선 연결)로 두면 불리언(교차 · 빼기)이 모두 「no result」
            # — 평 원기둥 빼기도 실패. 꺾인 직선(꺾은선)으로 두면 홈 1개 빼기 3.8 ~ 5.8 s 성공.
            # → 코너 R · 볼은 홈 곡선을 꺾은선 N 구간으로(곡선과 차이 ≤ 0.4 %D 가 되는 가장 작은 N).
            g["rk"]["poly"], g["rk_poly_n"], g["rk_poly_dev"] = rk_poly(g["rk"], D)
    g["vol"] = volumes(g)
    return g

# ───────────────────────── 2. 부피 계산 ─────────────────────────
def lens(r, a, rf):
    """원점 반지름 r 원 ∩ 중심거리 a 반지름 rf 원 의 넓이."""
    if r <= 0 or a >= r + rf:
        return 0.0
    if a <= abs(r - rf):
        return math.pi * min(r, rf) ** 2
    c1 = max(-1.0, min(1.0, (a * a + r * r - rf * rf) / (2 * a * r)))
    c2 = max(-1.0, min(1.0, (a * a + rf * rf - r * r) / (2 * a * rf)))
    k = 0.5 * math.sqrt(max(0.0, (-a + r + rf) * (a + r - rf) * (a - r + rf) * (a + r + rf)))
    return r * r * math.acos(c1) + rf * rf * math.acos(c2) - k

def tip_r(g, zz):
    D, R = g["D"], g["R"]
    if g["shape"] == "corner" and zz < R:
        return D / 2 - R + math.sqrt(max(0.0, R * R - (R - zz) ** 2))
    if g["shape"] == "ball" and zz < R:
        return math.sqrt(max(0.0, R * R - (R - zz) ** 2))
    return D / 2

def simpson(f, x0, x1, n=4000):
    if x1 <= x0:
        return 0.0
    h = (x1 - x0) / n
    s = f(x0) + f(x1)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * f(x0 + i * h)
    return s * h / 3

# ───────── 날 단면 v1.5: 경사면 직선 + 원호 (모양 확인용 · 추정값) ─────────
# 날 하나(피치 Θ = 360°/z) 를 반시계 방향으로: 날 끝 P(각 0) → 랜드 원호(외경) → Q(각 Θ − 홈각) →
# 원호 B(Q 를 지나 심압 원에 바깥 접 · 경사면 직선에 접) → 접점 T → 경사면 직선 → 다음 날 끝 P'(각 Θ).
# 경사각 γ = 날 끝에서 반경선과 경사면이 이루는 각(+ = 날 몸체 쪽으로 기울어 날이 예리) [STD-ISO3002-1] 정의 범주.
# 근거: 단면을 경사각 · 심압 반지름 · 홈각 3개로 정하는 방식 [ACA-FANG2020-WHEEL] · [ACA-WANG2014-THESIS].
# 기본값 경사 6° = 4날 D6 사례 1건 [ACA-KIMJH2005-KSPE](추정값) · 홈각 = 피치의 60 %(추정값).
def _v(a, b, k=1.0):
    return (a[0] + k * b[0], a[1] + k * b[1])

BOTTOM_POS = 0.30     # 홈 바닥(심압 접점) 위치 — 홈 구간 중 경사면 쪽에서 30 % (추정값, CIM3D 2날 메시 모양 참고)
RAKE_FOOT = 0.15      # 경사면 아래 끝 높이 — 심압에서 (R − rc) 의 15 % 위 (추정값)

def rake_geom(R, rc, z, rake_deg, flute_pct, n_pts=8):      # 점 8개(9점) — 많으면 SolidCraft 교차가 90 s 넘음(24개 실측)
    """날 하나(피치 Θ): 랜드(외경, 날 끝 P_k → Q) → 홈 곡선(Q → 바닥 K(심압) → A, 매끈한 스플라인) → 경사면 직선(A → 다음 날 끝 P).
    경사각 γ = 날 끝에서 반경선과 경사면 사이(+ = 날 몸체 쪽으로 기울어 예리). 홈각 = Q ~ P (피치의 %)."""
    Th = 2 * math.pi / z
    phf = Th * flute_pct / 100.0
    g_ = math.radians(rake_deg)
    P = (R * math.cos(Th), R * math.sin(Th))
    rh = (math.cos(Th), math.sin(Th)); th_ = (-math.sin(Th), math.cos(Th))
    u = (-rh[0] * math.cos(g_) + th_[0] * math.sin(g_), -rh[1] * math.cos(g_) + th_[1] * math.sin(g_))
    rA = rc + RAKE_FOOT * (R - rc)
    bq = P[0] * u[0] + P[1] * u[1]; cq = R * R - rA * rA
    disc = bq * bq - cq
    if disc < 0:
        raise Impossible("경사면이 홈 바닥 높이까지 내려가지 못함 — 경사각 확인")
    sv = -bq - math.sqrt(disc)
    A = (P[0] + sv * u[0], P[1] + sv * u[1])
    phA = math.atan2(A[1], A[0]) % (2 * math.pi)
    phQ = Th - phf
    if not (phQ + 0.15 * phf < phA < Th + 0.5 * (Th - phf)):    # 경사각 + 이면 A 가 날 끝보다 조금 뒤(파고듦)
        raise Impossible("경사면 아래 끝이 홈 구간 밖 — 경사각 · 홈각 확인")
    phK = phA - (phA - phQ) * BOTTOM_POS
    curve = []
    for i in range(n_pts + 1):
        ph = phQ + (phA - phQ) * i / n_pts
        if ph <= phK:
            v = (ph - phQ) / (phK - phQ); r = rc + (R - rc) * (0.5 + 0.5 * math.cos(math.pi * v))
        else:
            v = (ph - phK) / (phA - phK); r = rc + (rA - rc) * (0.5 - 0.5 * math.cos(math.pi * v))
        curve.append((r * math.cos(ph), r * math.sin(ph)))
    curve[-1] = A
    # 원호 근사: 점 3개씩 원호(스플라인 쓸기 교차는 SolidCraft 에서 90 s 초과 — 2026-11-13 실측 3회)
    arcs = [(curve[i], curve[i + 1], curve[i + 2]) for i in range(0, len(curve) - 2, 2)]
    return dict(Th=Th, phf=phf, P=P, Q=curve[0], A=A, curve=curve, arcs=arcs, u=u, R=R, rc=rc, phK=phK, rA=rA)

def circle3(p0, p1, p2):
    ax, ay = p0; bx, by = p1; cx, cy = p2
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)

def arc3_points(p0, p1, p2, n=40):
    (ux, uy), r = circle3(p0, p1, p2)
    a0 = math.atan2(p0[1] - uy, p0[0] - ux); a1 = math.atan2(p1[1] - uy, p1[0] - ux); a2 = math.atan2(p2[1] - uy, p2[0] - ux)
    s01 = (a1 - a0) % (2 * math.pi); s02 = (a2 - a0) % (2 * math.pi)
    sweep = s02 if s01 < s02 else -((a0 - a2) % (2 * math.pi))
    return [(ux + r * math.cos(a0 + sweep * i / n), uy + r * math.sin(a0 + sweep * i / n)) for i in range(n + 1)]

def rk_rot(p, ang):
    c, s_ = math.cos(ang), math.sin(ang)
    return (p[0] * c - p[1] * s_, p[0] * s_ + p[1] * c)

def rk_dense(rk, n=40):
    """홈 곡선(원호 근사)을 촘촘한 점으로 — 부피 · 그림 · SolidCraft 형상이 같은 원호.
    v1.6: 꺾은선(poly)이 있으면 그 점(코너 R · 볼 — 3D 와 같은 꺾은선)."""
    if rk.get("poly"):
        return list(rk["poly"])
    return rk_dense_arcs(rk, n)

def rk_dense_arcs(rk, n=40):
    out = []
    for i, (p0, p1, p2) in enumerate(rk["arcs"]):
        pts = arc3_points(p0, p1, p2, n)
        out += pts if i == 0 else pts[1:]
    return out

def _segdist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    u = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2)) if L2 > 0 else 0.0
    return math.hypot(p[0] - a[0] - u * dx, p[1] - a[1] - u * dy)

def rk_poly(rk, D, tol_pct=0.4):
    """홈 곡선 → 꺾은선 점(Q … A). 곡선과의 최대 차이 ≤ tol_pct %D 인 가장 작은 구간 수(6 ~ 16)."""
    dense = rk_dense_arcs(rk, 60)
    for N in (6, 8, 10, 12, 16):
        idx = [round(i * (len(dense) - 1) / N) for i in range(N + 1)]
        pl = [dense[i] for i in idx]
        dev = max(min(_segdist(q, pl[i], pl[i + 1]) for i in range(N)) for q in dense)
        if dev <= tol_pct / 100.0 * D or N == 16:
            return pl, N, dev

def rk_polygon(rk, z, n_arc=96):
    """외경 R 단면 윤곽(반시계): 랜드 → 홈 곡선 → (경사면 직선) → 다음 날 랜드."""
    pts = []
    land = rk["Th"] - rk["phf"]
    dense = rk_dense(rk)
    for k in range(z):
        base = k * rk["Th"]
        for i in range(n_arc):
            t = base + land * i / n_arc
            pts.append((rk["R"] * math.cos(t), rk["R"] * math.sin(t)))
        pts += [rk_rot(p_, base) for p_ in dense]
    return pts

def volumes(g):
    if g.get("section") == "rake":
        from shapely.geometry import Polygon, Point
        poly = Polygon(rk_polygon(g["rk"], g["z"]))
        D, Lc, R = g["D"], g["Lc"], g["R"]
        zr = R if g["shape"] != "square" else 0.0
        area = lambda r: poly.intersection(Point(0, 0).buffer(r, 512)).area if r > 0 else 0.0
        full = poly.area
        body = simpson(lambda q: area(tip_r(g, q)), 0, zr, 200) + full * (Lc - zr)
        rev = simpson(lambda q: math.pi * tip_r(g, q) ** 2, 0, zr) + math.pi * (D / 2) ** 2 * (Lc - zr)
        shank = 0.0
        pts = g["shank"]
        for (z0, r0), (z1, r1) in zip(pts, pts[1:]):
            shank += math.pi * (z1 - z0) * (r0 * r0 + r0 * r1 + r1 * r1) / 3
        return dict(revolve=rev, flute_one=(rev - body) / g["z"], after_flutes=[rev, body], shank=shank,
                    total=body + shank, section_area=full)
    return volumes_circle(g)

def volumes_circle(g):
    D, Lc, R, a, rf, z = g["D"], g["Lc"], g["R"], g["a"], g["rf"], g["z"]
    zr = R if g["shape"] != "square" else 0.0
    # 회전체(날부)
    rev = simpson(lambda q: math.pi * tip_r(g, q) ** 2, 0, zr) + math.pi * (D / 2) ** 2 * (Lc - zr)
    # 홈 1개가 빼는 부피 (나선 비틀림은 단면 넓이를 바꾸지 않음 — 원판이 축대칭)
    one = simpson(lambda q: lens(tip_r(g, q), a, rf), 0, zr) + lens(D / 2, a, rf) * (Lc - zr)
    shank = 0.0
    pts = g["shank"]
    for (z0, r0), (z1, r1) in zip(pts, pts[1:]):
        shank += math.pi * (z1 - z0) * (r0 * r0 + r0 * r1 + r1 * r1) / 3
    stages = [rev - k * one for k in range(z + 1)]
    return dict(revolve=rev, flute_one=one, after_flutes=stages, shank=shank, total=stages[-1] + shank,
                section_area=math.pi * (D / 2) ** 2 - z * lens(D / 2, a, rf))

# ───────────────────────── 3. 이름 ─────────────────────────
def fmt(v):
    return ("%.3f" % v).rstrip("0").rstrip(".")

def names(sp, g):
    shape_k = {"square": "평", "corner": "코너R", "ball": "볼"}[g["shape"]]
    stem = f"EM{g['z']}F_D{fmt(g['D'])}"
    if g["shape"] == "corner":
        stem += f"R{fmt(g['R'])}"
    if g["shape"] == "ball":
        stem += "B"
    stem += f"_d{fmt(g['d'])}_L{fmt(g['L'])}"
    if g["neck"]:
        stem += f"_N{fmt(g['neck'][0])}x{fmt(g['neck'][1])}"
    number = sp["number"] or stem.replace("_", "-")
    title = f"{g['z']}날 {shape_k} 엔드밀 D{fmt(g['D'])}"
    if g["shape"] == "corner":
        title += f" R{fmt(g['R'])}"
    title += f" × d{fmt(g['d'])} × L{fmt(g['L'])}"
    if g["neck"]:
        title += " 넥"
    return stem, number, title, shape_k

# ───────────────────────── 4. 도면 ─────────────────────────
ISO5455 = [50.0, 20.0, 10.0, 5.0, 2.0, 1.0, 0.5, 0.2]   # ISO 5455 권장 축척(확대 · 실척 · 축소)
FRAME = (20.0, 10.0, 287.0, 200.0)
RESERVED = {"표제란": (107.0, 10.0, 287.0, 52.0), "개정란": (167.0, 52.0, 287.0, 80.0), "사양표": (207.0, 80.0, 287.0, 153.0)}
NOTES_BOX = (20.0, 10.0, 107.0, 52.0)
ROW = 7.0   # 치수선 줄 간격(mm, 용지)

def scale_txt(s):
    return f"{fmt(s)}:1" if s >= 1 else f"1:{fmt(1 / s)}"

def overlap(b1, b2, gap=0.0):
    return not (b1[2] + gap <= b2[0] or b2[2] + gap <= b1[0] or b1[3] + gap <= b2[1] or b2[3] + gap <= b1[1])

def plan_layout(g):
    """그리기 전에 각 뷰의 차지 영역을 계산해 겹침 · 틀 밖을 검사하고 축척을 고른다."""
    D, d, L = g["D"], g["d"], g["L"]
    rmax = max(D, d) / 2
    below_rows = 2 if g["neck"] else 1
    tried = []
    for s in ISO5455:
        y_axis = FRAME[3] - 3.0 - (D / 2 * s + ROW + 4.0)   # 위: 날장 치수줄 + 글자
        top = FRAME[3] - 3.0
        bot = y_axis - rmax * s - below_rows * ROW - 3.5
        # 끝면도: 정면도 축과 같은 높이(3각법), 지름 ≤ 30 mm(용지) · 위 글자 포함 틀 안
        se = next((q for q in ISO5455 if D * q <= 30.0 and y_axis + D * q / 2 + 3 <= FRAME[3] - 1), None)
        if se is None:
            tried.append((s, ["끝면도"]))
            continue
        ev_c = (24.0 + D * se / 2 + 2, y_axis)
        ev_box = (ev_c[0] - D * se / 2 - 3, ev_c[1] - D * se / 2 - 9, ev_c[0] + D * se / 2 + 3, ev_c[1] + D * se / 2 + 3)
        x0 = ev_box[2] + 14.0
        box = (x0 - 4.0, bot, x0 + L * s + 16.0, top)        # 오른쪽 16 = 모따기 지시
        bad = []
        if box[2] > FRAME[2] - 2 or box[1] < FRAME[1]:
            bad.append("틀 밖")
        for k, r in RESERVED.items():
            if overlap(box, r, 1.0):
                bad.append(k)
        if overlap(box, ev_box, 2.0):
            bad.append("끝면도")
        lbl = (x0, bot - 5.5, x0 + 26, bot)                 # 「정면도 (축척)」 글자 — 정면도 왼쪽 아래
        if lbl[1] < FRAME[1] or any(overlap(lbl, r, 1.0) for r in RESERVED.values()):
            bad.append("정면도 이름")
        tried.append((s, bad))
        if not bad:
            break
    else:
        raise Impossible("정면도가 A4 양식에 들어가는 ISO 5455 축척이 없음 — " + "; ".join(f"{scale_txt(s)}: {','.join(b)}" for s, b in tried))
    lay = dict(s=s, x0=x0, y_axis=y_axis, front_box=box, se=se, ev_c=ev_c, ev_box=ev_box, tried=tried)
    # 상세도(코너 R · 볼): R 이 용지에서 10 ~ 25 mm 되는 최대 축척
    if g["shape"] != "square":
        sd = next((q for q in ISO5455 if g["R"] * q <= 22.0), ISO5455[-1])
        w = (g["R"] + max(1.5 * g["R"], 0.6)) * sd
        h = (g["R"] + max(1.2 * g["R"], 0.6)) * sd
        dc = (40.0, 92.0)                                        # 상세도 원점(날 끝 · 외경 기준)
        dbox = (dc[0] - 14.0, dc[1] - 6.0, dc[0] + w + 6.0, dc[1] + g["R"] * sd + 12.0)
        if dbox[3] > lay["front_box"][1] - 2:
            raise Impossible("상세도가 정면도와 겹침")
        for k, r in list(RESERVED.items()) + [("주기", NOTES_BOX)]:
            if overlap(dbox, r, 1.0):
                raise Impossible(f"상세도가 {k} 와 겹침")
        lay.update(sd=sd, dc=dc, dbox=dbox)
    return lay

def text_w(t, h):
    """글자 폭 추정(mm): 한글 0.95h · 그 밖 0.6h — 칸 넘침 방지용."""
    return h * sum(0.95 if ord(ch) > 0x2E80 else 0.68 for ch in t)

GDT_TOL = 0.005   # 사내 명칭도 2016(raw/도면 작업/사내도면_2016) — 사내 경험값

def _free_x(busy, w, lo, hi, want):
    """[lo, hi] 안에서 busy 구간과 안 겹치는 폭 w 자리 중 want 에 가장 가까운 시작 x (없으면 None)."""
    cands = [lo, want] + [b + 2 for _, b in busy]
    best = None
    for x in cands:
        x = max(lo, x)
        if x + w > hi:
            continue
        if any(not (x + w <= a or x >= b) for a, b in busy):
            continue
        if best is None or abs(x - want) < abs(best - want):
            best = x
    return best

def gdt(m, g, X0, Y0, s, top, busy):
    """날부 원주 흔들림 0.005 A · 생크 원통도 0.005 · 데이텀 A(생크). 윗줄 빈자리에 넣고, 못 넣으면 주기로 돌린다."""
    D, d, L, Lc, C = g["D"], g["d"], g["L"], g["Lc"], g["C"]
    yc = top + ROW            # 윗줄 중심
    H, W = 5.0, 21.0
    out = []

    def L_(a, b):
        m.add_line(a, b, dxfattribs={"layer": "DIM"})

    def frame(x, sym):
        y0 = yc - H / 2
        m.add_lwpolyline([(x, y0), (x + W, y0), (x + W, y0 + H), (x, y0 + H)], close=True, dxfattribs={"layer": "DIM"})
        L_((x + 6, y0), (x + 6, y0 + H)); L_((x + 16, y0), (x + 16, y0 + H))
        cx, cy = x + 3, yc
        if sym == "runout":       # 원주 흔들림 ↗
            L_((cx - 1.6, cy - 1.6), (cx + 1.6, cy + 1.6))
            m.add_solid([(cx + 1.6, cy + 1.6), (cx + 0.4, cy + 1.3), (cx + 1.3, cy + 0.4)], dxfattribs={"layer": "DIM"})
        else:                     # 원통도 ⌭
            m.add_circle((cx, cy), 1.0, dxfattribs={"layer": "DIM"})
            L_((cx - 1.9, cy - 1.7), (cx - 0.1, cy + 1.7)); L_((cx + 0.1, cy - 1.7), (cx + 1.9, cy + 1.7))
        m.add_text(f"{GDT_TOL:.3f}", height=2.3, dxfattribs={"layer": "DIM", "style": "KOR", "insert": (x + 6.8, cy - 1.1)})
        if sym == "runout":
            m.add_text("A", height=2.3, dxfattribs={"layer": "DIM", "style": "KOR", "insert": (x + 17.7, cy - 1.1)})

    def leader(p_from, p_to):
        L_(p_from, p_to)
        ang = math.atan2(p_from[1] - p_to[1], p_from[0] - p_to[0])
        a1 = (p_to[0] + 1.8 * math.cos(ang + 0.3), p_to[1] + 1.8 * math.sin(ang + 0.3))
        a2 = (p_to[0] + 1.8 * math.cos(ang - 0.3), p_to[1] + 1.8 * math.sin(ang - 0.3))
        m.add_solid([p_to, a1, a2], dxfattribs={"layer": "DIM"})

    hi = X0 + L * s + 14
    # 원주 흔들림: 날부 위
    xr = _free_x(busy, W, X0 + Lc * s * 0.2, hi, X0 + Lc * s + 4)
    if xr is not None:
        frame(xr, "runout")
        tx = X0 + Lc * s * 0.55
        leader((xr + 2, yc - H / 2), (tx, top))
        busy.append((xr - 1, xr + W + 1))
    else:
        out.append(f" · 날부 원주 흔들림 {GDT_TOL:.3f} A")
    # 데이텀 A + 원통도: 생크 위 (원통도 틀이 안 들어가면 데이텀만 그리고 원통도는 주기로)
    x_sh0, x_sh1 = X0 + g["zt"] * s + 2, X0 + (L - C) * s - 2
    ysh = Y0 + d / 2 * s

    def datum(bx):
        m.add_lwpolyline([(bx, yc - 2.5), (bx + 5, yc - 2.5), (bx + 5, yc + 2.5), (bx, yc + 2.5)], close=True, dxfattribs={"layer": "DIM"})
        m.add_text("A", height=2.5, dxfattribs={"layer": "DIM", "style": "KOR", "insert": (bx + 1.4, yc - 1.2)})
        L_((bx + 2.5, yc - 2.5), (bx + 2.5, ysh + 2.2))
        m.add_solid([(bx + 1.0, ysh), (bx + 4.0, ysh), (bx + 2.5, ysh + 2.2)], dxfattribs={"layer": "DIM"})

    xs = _free_x(busy, 6 + 3 + W, x_sh0, min(hi, x_sh1 + W), (x_sh0 + x_sh1) / 2 - 15)
    if xs is not None and xs + 3 <= x_sh1:
        datum(xs)
        fx = xs + 9
        frame(fx, "cyl")
        leader((fx + 4, yc - H / 2), (min(max(fx + 4, x_sh0), x_sh1), ysh))
        busy.append((xs - 1, fx + W + 1))
    else:
        xd = _free_x(busy, 6, x_sh0, x_sh1, (x_sh0 + x_sh1) / 2)
        if xd is not None:
            datum(xd)
            busy.append((xd - 1, xd + 6))
            out.append(f" · 생크 원통도 {GDT_TOL:.3f}")
        else:
            out.append(f" · 생크(데이텀 A) 원통도 {GDT_TOL:.3f}")
    return out

def build_dxf(sp, g, tpl, date, stem, number, title, shape_k):
    import ezdxf
    lay = plan_layout(g)
    doc = ezdxf.readfile(tpl)
    m = doc.modelspace()
    if "TG" not in doc.dimstyles:
        ds = doc.dimstyles.new("TG")
    ds = doc.dimstyles.get("TG")
    for k, v in dict(dimtxt=2.5, dimasz=2.0, dimexo=0.8, dimexe=1.2, dimgap=0.7, dimdec=3, dimzin=8, dimtad=1,
                     dimtih=0, dimtoh=0, dimtxsty="KOR", dimclrd=4, dimclre=4, dimclrt=4, dimdsep=ord(".")).items():
        ds.dxf.set(k, v)

    def set_text(old, new, width=None):
        hit = [e for e in m.query("TEXT") if e.dxf.text == old]
        if not hit:
            raise RuntimeError(f"양식에 '{old}' 없음")
        hit[0].dxf.text = new
        if width:
            hit[0].dxf.height = min(hit[0].dxf.height, width / text_w(new, 1.0))

    def txt(s, x, y, h=2.5, layer="NOTE", rot=0.0):
        return m.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "KOR", "insert": (x, y)})

    def line(a, b, layer="OUTLINE"):
        m.add_line(a, b, dxfattribs={"layer": layer})

    def dim_h(p1, p2, y, s, text):
        m.add_linear_dim(base=(p1[0], y), p1=p1, p2=p2, angle=0, text=text, dimstyle="TG",
                         dxfattribs={"layer": "DIM"}, override={"dimlfac": 1.0 / s}).render()

    def dim_v(p1, p2, x, s, text, tol=None):
        dm = m.add_linear_dim(base=(x, p1[1]), p1=p1, p2=p2, angle=90, text=text, dimstyle="TG",
                              dxfattribs={"layer": "DIM"}, override={"dimlfac": 1.0 / s})
        if tol:      # (위 편차, 아래 편차) mm — 쌓은 공차 글자
            dm.set_tolerance(upper=tol[0], lower=-tol[1], hfactor=0.7, align=0, dec=3)
        dm.render()

    # 양식 칸
    set_text("S (생크경)", "d (생크경)")
    set_text("(도면명)", title, 112.0)
    set_text("(도면번호)", number)
    set_text("1:1", scale_txt(lay["s"]))
    set_text("YYYY-MM-DD", date)
    vm = re.search(r"_v(\d+)$", stem)
    if vm:
        set_text("v1", "v" + vm.group(1))
    set_text("(파일명)", stem + ".dxf", 54.0)

    D, d, L, Lc, R, s = g["D"], g["d"], g["L"], g["Lc"], g["R"], lay["s"]
    X0, Y0 = lay["x0"], lay["y_axis"]
    f = lambda x, y: (X0 + s * x, Y0 + s * y)

    # ── 정면도 외곽 (윗반 → 아랫반 대칭) ──
    b = -math.tan(math.radians(22.5))
    up = []   # (x, y, bulge to next)
    if g["shape"] == "square":
        up += [(0, 0, 0), (0, D / 2, 0)]
    elif g["shape"] == "corner":
        up += [(0, 0, 0), (0, D / 2 - R, b), (R, D / 2, 0)]
    else:
        up += [(0, 0, b), (R, D / 2, 0)]
    if Lc > up[-1][0] + 1e-9:
        up.append((Lc, D / 2, 0))
    for zq, rq in g["shank"]:
        if abs(zq - up[-1][0]) < 1e-9 and abs(rq - up[-1][1]) < 1e-9:
            continue
        up.append((zq, rq, 0))
    up.append((L, 0, 0))
    low = []
    for i in range(len(up) - 1, -1, -1):
        x, y, _ = up[i]
        bb = up[i - 1][2] if i > 0 else 0
        low.append((x, -y, bb))
    pts = up[:-1] + low[:-1]
    m.add_lwpolyline([(*f(x, y), 0, 0, bb) for x, y, bb in pts], format="xyseb", close=True, dxfattribs={"layer": "OUTLINE"})
    # 단 · 경계선
    xs = [Lc] + [zq for zq, _ in g["shank"][1:-1]] + [L - g["C"]]
    for xq in sorted(set(round(v, 6) for v in xs)):
        rq = max(rr for zq, rr in [(Lc, D / 2)] + g["shank"] if abs(zq - xq) < 1e-6)
        line(f(xq, rq), f(xq, -rq), "THIN" if abs(xq - Lc) < 1e-9 and not g["neck"] and D == d else "OUTLINE")
    # 나선 홈 선(보이는 쪽)
    x_start = R if g["shape"] != "square" else 0.0
    lead = g["lead"]
    for k in range(g["z"]):
        seg = []
        for i in range(401):
            x = x_start + (Lc - x_start) * i / 400
            th = 2 * math.pi * x / lead * (1 if g["hand"] == "R" else -1) + 2 * math.pi * k / g["z"]
            if math.sin(th) > 0:
                seg.append(f(x, (D / 2) * math.cos(th)))
            else:
                if len(seg) > 1:
                    m.add_lwpolyline(seg, dxfattribs={"layer": "THIN"})
                seg = []
        if len(seg) > 1:
            m.add_lwpolyline(seg, dxfattribs={"layer": "THIN"})
    line(f(-3 / s, 0), f(L + 3 / s, 0), "CENTER")
    rows_below = 2 if g["neck"] else 1
    txt(f"정면도 ({scale_txt(s)})", X0, Y0 - max(D, d) / 2 * s - rows_below * ROW - 3.5 - 4.0, 3.0)
    busy = [(X0 - 3, X0 + Lc * s + 3)]
    # 치수
    top = Y0 + D / 2 * s
    rmax = max(D, d) / 2 * s
    dim_h(f(0, D / 2), f(Lc, D / 2), top + ROW, s, "<> (날장)")
    row = 1
    if g["neck"]:
        dim_h(f(0, -D / 2), f(g["neck"][1], -g["neck"][0] / 2), Y0 - rmax - ROW * row, s, "<> (유효장)")
        row += 1
    dim_h(f(0, -D / 2), f(L, -(d / 2 - g["C"])), Y0 - rmax - ROW * row, s, "<> (전장 L)")
    xD = Lc * 0.62 if g["shape"] != "ball" else max(R * 1.3, Lc * 0.7)
    dim_v(f(xD, -D / 2), f(xD, D / 2), f(xD, 0)[0], s, "D %%c<>" + (f" {g['D_tol']}" if g["D_tol"] else ""), g["D_dev"])
    if g["neck"]:
        xn = (Lc + g["neck"][1]) / 2
        dim_v(f(xn, -g["neck"][0] / 2), f(xn, g["neck"][0] / 2), f(xn, 0)[0], s, "%%c<> (넥)")
    xd = L - g["C"] - min(0.12 * (L - g["zt"]), 6.0)
    dim_v(f(xd, -d / 2), f(xd, d / 2), f(xd, 0)[0], s, "d %%c<> h6", (0.0, -g["h6"]))
    pc = f(L - g["C"] / 2, d / 2 - g["C"] / 2)
    m.add_lwpolyline([pc, (pc[0] + 4, pc[1] + 5), (pc[0] + 10, pc[1] + 5)], dxfattribs={"layer": "DIM"})
    txt(f"C{fmt(g['C'])}", pc[0] + 4.5, pc[1] + 5.6, 2.5, "DIM")
    if g["neck"] or D != d:
        zq0, rq0 = g["shank"][-4] if g["neck"] else g["shank"][0]
        pm = f((zq0 + g["zt"]) / 2, (rq0 + d / 2) / 2)
        m.add_lwpolyline([pm, (pm[0] + 3, pm[1] + 6), (pm[0] + 10, pm[1] + 6)], dxfattribs={"layer": "DIM"})
        txt(f"{fmt(g['taper_deg'])}°", pm[0] + 3.5, pm[1] + 6.6, 2.3, "DIM")
        busy.append((pm[0] - 1, pm[0] + 11))
    busy.append((pc[0] - 1, pc[0] + 11))
    gdt_notes = gdt(m, g, X0, Y0, s, top, busy)

    # ── 끝면도 (날 끝 형상 생략 → 날부 단면과 같은 모양) ──
    se, c = lay["se"], lay["ev_c"]
    Rp, a, rf, z = D / 2 * se, g["a"] * se, g["rf"] * se, g["z"]
    if g.get("section") == "rake":
        rk = g["rk"]; Th = rk["Th"]
        dense = rk_dense(rk)
        S_ = lambda p_: (c[0] + se * p_[0], c[1] + se * p_[1])
        for k in range(z):
            bk = k * Th
            m.add_arc(c, Rp, math.degrees(bk), math.degrees(bk + Th - rk["phf"]), dxfattribs={"layer": "OUTLINE"})
            m.add_lwpolyline([S_(rk_rot(p_, bk)) for p_ in dense], dxfattribs={"layer": "OUTLINE"})
            m.add_line(S_(rk_rot(rk["A"], bk)), S_(rk_rot(rk["P"], bk)), dxfattribs={"layer": "OUTLINE"})
        a = rf = None
    for k in (range(z) if a is not None else []):
        phi = math.degrees(math.acos((Rp ** 2 + a ** 2 - rf ** 2) / (2 * Rp * a)))
        px, py = Rp * math.cos(math.radians(phi)), Rp * math.sin(math.radians(phi))
        psi = math.degrees(math.atan2(py, px - a))
        th = 360.0 * k / z
        m.add_arc(c, Rp, th + phi, th + 360.0 / z - phi, dxfattribs={"layer": "OUTLINE"})
        cc = (c[0] + a * math.cos(math.radians(th)), c[1] + a * math.sin(math.radians(th)))
        m.add_arc(cc, rf, th + psi, th + 360.0 - psi, dxfattribs={"layer": "OUTLINE"})
    m.add_circle(c, g["core_d"] / 2 * se, dxfattribs={"layer": "HIDDEN"})
    line((c[0] - Rp - 3, c[1]), (c[0] + Rp + 3, c[1]), "CENTER")
    line((c[0], c[1] - Rp - 3), (c[0], c[1] + Rp + 3), "CENTER")
    txt(f"끝면도 ({scale_txt(se)})", c[0] - 10, c[1] - Rp - 8, 3.0)

    # ── 상세도 (코너 R · 볼) ──
    if g["shape"] != "square":
        sd, dc = lay["sd"], lay["dc"]
        q = lambda x, y: (dc[0] + sd * x, dc[1] + sd * (y - (D / 2 - R - 0.0)))
        ext = max(1.5 * R, 0.6)
        if g["shape"] == "corner":
            pts2 = [(0, D / 2 - R - ext * 0.8, 0), (0, D / 2 - R, b), (R, D / 2, 0), (R + ext, D / 2, 0)]
        else:
            pts2 = [(0, 0, b), (R, D / 2, 0), (R + ext, D / 2, 0)]
            q = lambda x, y: (dc[0] + sd * x, dc[1] + sd * y)
        m.add_lwpolyline([(*q(x, y), 0, 0, bb) for x, y, bb in pts2], format="xyseb", dxfattribs={"layer": "OUTLINE"})
        # 끊김선
        xe, ye = q(R + ext, D / 2)
        yb = q(0, pts2[0][1])[1]
        m.add_lwpolyline([(xe, yb), (xe + 0.8, yb + (ye - yb) * 0.35), (xe - 0.8, yb + (ye - yb) * 0.65), (xe, ye + 0.5)], dxfattribs={"layer": "THIN"})
        line(q(0, pts2[0][1]) if g["shape"] == "corner" else q(-0.15 * R, 0), (xe, yb), "THIN" if g["shape"] == "corner" else "CENTER")
        cen = q(R, D / 2 - R)
        m.add_radius_dim(center=cen, radius=R * sd, angle=135, dimstyle="TG", text="<>",
                         dxfattribs={"layer": "DIM"}, override={"dimlfac": 1.0 / sd, "dimtad": 0}).render()
        txt(f"상세 A ({scale_txt(sd)}) — {'코너 R' if g['shape'] == 'corner' else '볼 R'}", dc[0] - 8, q(0, D / 2)[1] + 8, 3.0)
        k45 = math.sqrt(0.5)
        pa = f(R - R * k45, D / 2 - R + R * k45)
        ra = max(2.0, R * s * 0.9)
        m.add_circle(pa, ra, dxfattribs={"layer": "THIN"})
        txt("A", pa[0] - ra - 2.5, pa[1] + ra * 0.5, 2.5)

    # ── 사양표 · 주기 ──
    def spec_row(label, val):
        t = [e for e in m.query("TEXT") if e.dxf.text == label][0]
        m.add_text(val, height=min(2.3, 46.0 / text_w(val, 1.0)), dxfattribs={"layer": "TB_VALUE", "style": "KOR", "insert": (239.0, t.dxf.insert.y)})
    hand_k = "오른나선" if g["hand"] == "R" else "왼나선"
    neck_v = f"Ø{fmt(g['neck'][0])} × {fmt(g['neck'][1])}  (DN × LU)" if g["neck"] else "—"
    rv = {"square": "—", "corner": f"코너 R{fmt(R)}  (RE)", "ball": f"볼 R{fmt(R)}  (RE)"}[g["shape"]]
    dtxt = f"Ø{fmt(D)}" + (f" {g['D_tol']} ({g['D_dev'][0]:+.3f}/{g['D_dev'][1]:+.3f})" if g["D_tol"] else "")
    for k, v in {"공구 종류": f"{shape_k} 엔드밀" + (" (넥)" if g["neck"] else ""), "날 수": f"{g['z']}  (NOF)",
                 "D (날경)": dtxt + "  (DC)", "d (생크경)": f"Ø{fmt(d)} h6  (DMM)", "L (전장)": f"{fmt(L)}  (OAL)", "날장": f"{fmt(Lc)}  (APMX)",
                 "목경 × 목길이": neck_v, "볼 R / 코너 R": rv, "나선각": f"{fmt(g['helix'])}° {hand_k}  (FHA)",
                 "소재 (등급)": "초경 (확인 필요)", "코팅": "확인 필요", "비고": "생성기 초안"}.items():
        spec_row(k, v)
    notes = [f"[주기] 단위 mm · 모양 확인용 초안 ({date})",
             "1. 날 끝 형상(갭 · 끝날 여유각 · 경사각) · 홈 끝맺음 생략",
             f"2. d h6 = 0 / −{g['h6']:.3f}" + (f" · D {g['D_tol']} = {g['D_dev'][0]:+.3f} / {g['D_dev'][1]:+.3f}".replace("-", "−") if g["D_tol"] else "") + " (ISO 286-2)",
             f"3. 나선각 {fmt(g['helix'])}° {hand_k} · 리드 {g['lead']:.2f} (= π×{fmt(D)}÷tan{fmt(g['helix'])}°)",
             (f"4. 홈 단면 경사면 직선(경사각 {fmt(g['rake'])}°) + 곡선 · 심압 Ø{g['core_d']:.2f} ({fmt(g['core_pct'])} %D) · 홈각 {fmt(g['flute_pct'])} % (추정값)"
              if g.get("section") == "rake" else f"4. 홈 단면 원호 R{g['rf']:.2f} · 심압 Ø{g['core_d']:.2f} ({fmt(g['core_pct'])} %D, 추정값)"
)]
    if g["neck"]:
        notes.append(f"5. 넥 단 45°{' (반경 %.2f)' % ((D - g['neck'][0]) / 2) if g['neck_step'] else ' 없음'} · 넥 → 생크 테이퍼 편측 {fmt(g['taper_deg'])}° (길이 {g['zt'] - g['neck'][1]:.2f}, 참고)")
    elif D != d:
        notes.append(f"5. 날부 → 생크 테이퍼 편측 {fmt(g['taper_deg'])}° (길이 {g['zt'] - Lc:.2f}, 참고)")
    else:
        notes.append(f"5. 생크 끝 C{fmt(g['C'])} (추정값)")
    notes += [f"6. 3D STEP 솔리드 2개(날부 · 생크) · 부피 {g['vol']['total']:,.2f} mm³",
              "7. 기하공차 0.005 = 사내 2016 도면 관례" + "".join(gdt_notes),
              "8. 지시 없는 공차 ISO 2768-m · 사양표 괄호 = ISO 13399 기호"]
    for i, s_ in enumerate(notes):
        hn = min(2.3, 83.0 / text_w(s_, 1.0))
        txt(s_, 22.0, 47.5 - i * 4.25, hn)
    return doc, lay, notes

def post_check(doc, lay):
    """그린 뒤 실제 엔티티 범위가 틀 안인지 확인 (양식 엔티티 제외)."""
    from ezdxf import bbox
    m = doc.modelspace()
    mine = [e for e in m if e.dxf.layer in ("OUTLINE", "THIN", "CENTER", "HIDDEN", "DIM", "NOTE")]
    ext = bbox.extents(mine)
    ok = ext.extmin.x >= FRAME[0] and ext.extmin.y >= FRAME[1] and ext.extmax.x <= FRAME[2] and ext.extmax.y <= FRAME[3]
    return ok, (round(ext.extmin.x, 1), round(ext.extmin.y, 1), round(ext.extmax.x, 1), round(ext.extmax.y, 1))

def render(doc, png, pdf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy, LineweightPolicy
    from ezdxf.fonts import fonts
    # 한글 글꼴: 양식의 malgun.ttf 가 없으면 Noto Sans CJK 로 대신 (그림 · PDF 전용, DXF 는 그대로)
    cands = [p for p in font_manager.findSystemFonts() if os.path.basename(p).lower() in ("malgun.ttf", "notosanscjk-regular.ttc", "notosanscjkkr-regular.otf", "nanumgothic.ttf")]
    if cands and not any(os.path.basename(p).lower() == "malgun.ttf" for p in cands):
        fname = os.path.basename(cands[0])
        for st in ("KOR", "KOR_B"):
            if st in doc.styles:
                doc.styles.get(st).dxf.font = fname
    lw = {"OUTLINE": 50, "TB_FRAME": 50, "TB_LINE": 35, "THIN": 18, "CENTER": 18, "HIDDEN": 18, "DIM": 18, "TB_THIN": 18}
    for ly in doc.layers:
        if ly.dxf.name in lw:
            ly.dxf.lineweight = lw[ly.dxf.name]
    fig = plt.figure(figsize=(297 / 25.4, 210 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK,
                        lineweight_policy=LineweightPolicy.ABSOLUTE, lineweight_scaling=1.0)
    Frontend(ctx, MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace(), finalize=True)
    ax.set_xlim(0, 297); ax.set_ylim(0, 210); ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(png, dpi=200, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)

# ───────────────────────── 5. SolidCraft 레시피 ─────────────────────────
def recipe_staged(g, stem, sc_dir):
    """SolidCraft batch 단계 목록. 각 단계의 commands 를 batch 의 commands 로, expect 를 expect 로 그대로 넣는다.
    2026-11-12 실측: 날부 회전체 + 홈 경로 + 홈1 을 한 단계로(약 10 ~ 12 s), 홈 2 ~ 4 는 하나씩(10 ~ 38 s, 저장 포함),
    생크 + 스케치 숨김 + 저장 + STEP 내보내기 마지막 단계(약 2 ~ 3 s). 한 단계 90 s 제한(역할 정의 §4-7)."""
    D, L, Lc, R = g["D"], g["L"], g["Lc"], g["R"]
    YZ = {"origin": [0, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}
    wd = sc_dir + "\\_작업\\"
    tip = [{"command": "sketch.create", "params": {"plane": YZ, "name": "TipProfile"}}]
    if g["shape"] == "square":
        tip.append({"command": "sketch.line", "params": {"points": [[0, 0], [D / 2, 0], [D / 2, Lc], [0, Lc]], "closed": True}})
    elif g["shape"] == "corner":
        tip += [{"command": "sketch.line", "params": {"points": [[0, Lc], [0, 0], [D / 2 - R, 0]]}},
                {"command": "sketch.arc.center_point", "params": {"center": [D / 2 - R, R], "start": [D / 2 - R, 0], "end": [D / 2, R]}},
                {"command": "sketch.line", "params": {"points": [[D / 2, R], [D / 2, Lc], [0, Lc]]}}]
    else:
        tip += [{"command": "sketch.arc.center_point", "params": {"center": [0, R], "start": [0, 0], "end": [R, R]}}]
        tail = [[R, R]] + ([[R, Lc]] if Lc > R + 1e-9 else []) + [[0, Lc], [0, 0]]
        tip.append({"command": "sketch.line", "params": {"points": tail}})
    tip += [{"command": "sketch.finish", "params": {}},
            {"command": "solid.revolve", "params": {"sketch": "TipProfile", "axis": "Z", "operation": "new_body",
                                                     "body_name": "FluteBody", "name": "Tip"}},
            {"command": "sketch.create", "params": {"plane": YZ, "name": "FlutePath"}},
            {"command": "sketch.line", "params": {"points": [[0, -1], [0, Lc + 1]]}},
            {"command": "sketch.finish", "params": {}}]
    v = g["vol"]
    stages = []
    for k in range(g["z"]):
        th = 2 * math.pi * k / g["z"]
        cmds = tip if k == 0 else []
        cmds = cmds + [
            {"command": "sketch.create", "params": {"plane": {"origin": [0, 0, -1], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": f"Flute{k + 1}"}},
            {"command": "sketch.circle.center", "params": {"center": [round(g["a"] * math.cos(th), 6) + 0.0, round(g["a"] * math.sin(th), 6) + 0.0], "radius": round(g["rf"], 6)}},
            {"command": "sketch.finish", "params": {}},
            {"command": "solid.sweep", "params": {"sketch": f"Flute{k + 1}", "path_sketch": "FlutePath", "path": ["l1"],
                                                  "twist": f"{g['twist']:.4f} deg", "operation": "cut", "targets": ["FluteBody"], "name": f"Flute{k + 1}Cut"}},
            {"command": "save", "params": {"path": f"{wd}{stem}_s{k + 1}_flute{k + 1}.sc"}}]
        stages.append({"name": f"{k + 1}_{'날부회전체+' if k == 0 else ''}홈{k + 1}", "commands": cmds,
                       "expect": {"volume_mm3": round(v["after_flutes"][k + 1], 4), "bodies": 1}})
    sk = [[0, Lc]] + [[round(r, 6), round(zq, 6)] for zq, r in g["shank"]] + [[0, L]]
    rm = max(D, g["d"]) / 2
    stages.append({"name": f"{g['z'] + 1}_생크+저장+STEP", "commands": [
        {"command": "sketch.create", "params": {"plane": YZ, "name": "ShankProfile"}},
        {"command": "sketch.line", "params": {"points": sk, "closed": True}},
        {"command": "sketch.finish", "params": {}},
        {"command": "solid.revolve", "params": {"sketch": "ShankProfile", "axis": "Z", "operation": "new_body", "body_name": "ShankBody", "name": "Shank"}},
        {"command": "browser.visibility", "params": {"visible": False, "folder": "sketches"}},
        {"command": "save", "params": {"path": f"{sc_dir}\\{stem}.sc"}},
        {"command": "export", "params": {"path": f"{sc_dir}\\{stem}.step"}}],
        "expect": {"volume_mm3": round(v["total"], 4), "bodies": 2,
                   "bbox": {"min": [-rm, -rm, 0], "max": [rm, rm, L]}}})
    return {"tool_gen": VERSION, "design_name": stem, "sc_dir": sc_dir, "stages": stages,
            "screenshot": {"view": "iso", "grid": False, "axes": False, "width": 960, "height": 540, "path": f"{sc_dir}\\{stem}_3D.png"},
            "how": "new_design(name=design_name) → 단계마다 batch(commands, expect, timings=true, verbose=false) → screenshot. "
                   "실패 · 90 s 끊김이면 _작업 의 마지막 저장본을 open 하고 다음 단계부터.",
            "check": "FreeCAD: Part.Shape.read(step) → 솔리드 2 · isValid · 부피 · optimalBoundingBox"}

def section_cmds(g, Ro, z0, name="Section"):
    if g.get("section") == "rake":
        return section_cmds_rake(g, Ro, z0, name)
    return section_cmds_circle(g, Ro, z0, name)

def section_cmds_rake(g, Ro, z0, name="Section"):
    """v1.5 단면: 랜드 원호(Ro) → [Ro>R 면 반경 직선] → 홈 곡선 스플라인 → 경사면 직선(Ro 까지 연장)."""
    rk, z = g["rk"], g["z"]
    R = rk["R"]
    rd = lambda p_: [round(p_[0], 6) + 0.0, round(p_[1], 6) + 0.0]
    dense = rk_dense(rk)
    u = rk["u"]
    P0 = rk["P"]
    if Ro > R + 1e-9:
        bq = -(P0[0] * u[0] + P0[1] * u[1]); cq = R * R - Ro * Ro
        se = -bq + math.sqrt(bq * bq - cq)                 # P 에서 -u 방향으로 Ro 까지
        E0 = (P0[0] - se * u[0], P0[1] - se * u[1])
        F0 = (rk["Q"][0] * Ro / R, rk["Q"][1] * Ro / R)
    else:
        E0, F0 = P0, rk["Q"]
    Th = rk["Th"]
    c = [{"command": "sketch.create", "params": {"plane": {"origin": [0, 0, z0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": name}}]
    for k in range(z):
        b = k * Th
        Ek = rk_rot(E0, b - Th)            # 이 날의 날 끝(앞 날 경사면 연장점)
        Fk = rk_rot(F0, b); Qk = rk_rot(rk["Q"], b)
        Ak = rk_rot(rk["A"], b); En = rk_rot(E0, b)
        land_id = 1 + k * (1 + len(rk["arcs"]))
        c.append({"command": "sketch.arc.center_point", "params": {"center": [0, 0], "start": rd(Ek), "end": rd(Fk)}})
        if Ro > R + 1e-9:
            c.append({"command": "sketch.line", "params": {"points": [rd(Fk), rd(Qk)]}})
            first = f"l{2 * k + 1}.end"            # 반경 직선 끝(=Q) 에 잇는다(점 참조 — 안 이으면 닫힌 윤곽 안 됨, 실측)
        else:
            first = f"a{land_id}.end"
        aid = land_id
        for j, (p0, p1, p2) in enumerate(rk["arcs"]):
            aid += 1
            c.append({"command": "sketch.arc.three_point", "params": {"start": first if j == 0 else f"a{aid - 1}.end",
                                                                       "through": rd(rk_rot(p1, b)), "end": rd(rk_rot(p2, b))}})
        c.append({"command": "sketch.line", "params": {"points": [f"a{aid}.end", rd(En)]}})
    c.append({"command": "sketch.finish", "params": {}})
    return c

def gap_cmds_rake(g, k, Ro, z0=-1.0):
    """v1.6 코너 R · 볼: 홈 k 의 빈 공간(꺾은선 홈 곡선 + 경사면 직선 + Ro 원호) 스케치 → 비틀어 쓸어 빼기.
    실측(2026-11-13, D6 R0.5 4날): 홈 1개 5.8 s. 이어진 원호 곡선은 빼기 실패(57.8 s 후 no result)."""
    rk = g["rk"]
    R, Th = rk["R"], rk["Th"]
    rd = lambda p_: [round(p_[0], 6) + 0.0, round(p_[1], 6) + 0.0]
    P0, u = rk["P"], rk["u"]
    bq = -(P0[0] * u[0] + P0[1] * u[1]); cq = R * R - Ro * Ro
    se = -bq + math.sqrt(bq * bq - cq)
    E0 = (P0[0] - se * u[0], P0[1] - se * u[1])
    F0 = (rk["Q"][0] * Ro / R, rk["Q"][1] * Ro / R)
    b = k * Th
    # 홈 시작점 Q 는 외경 R 위에 있다 → 꼭짓점을 R 위(또는 바로 밖)에 두면 쓸었을 때 외경 원통과 겹치거나 스치듯 만나
    # 빼기가 실패(54.7 s 후 no result)하거나 재시도로 87.9 s(실측 2026-11-13). Q 를 반지름 방향 1 % 안쪽(Qi)으로 —
    # F → Qi 는 반지름 직선이라 외경을 직각으로 지나가고 Q 자리(랜드 끝)는 그대로. 부피 차이 무시 수준(삼각형 ≈ 0.005 mm²).
    Qi = (rk["Q"][0] * 0.99, rk["Q"][1] * 0.99)
    pts = [rk_rot(F0, b), rk_rot(Qi, b)] + [rk_rot(p_, b) for p_ in rk["poly"][1:]] + [rk_rot(E0, b)]
    name = f"Gap{k + 1}"
    return [{"command": "sketch.create", "params": {"plane": {"origin": [0, 0, z0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": name}},
            {"command": "sketch.line", "params": {"points": [rd(q) for q in pts]}},
            {"command": "sketch.arc.center_point", "params": {"center": [0, 0], "start": rd(pts[-1]), "end": rd(pts[0]), "clockwise": True}},
            {"command": "sketch.finish", "params": {}},
            {"command": "solid.sweep", "params": {"sketch": name, "path_sketch": "FlutePath", "path": ["l1"],
                                                  "twist": f"{g['twist']:.4f} deg", "operation": "cut", "targets": ["FluteBody"],
                                                  "name": f"Flute{k + 1}Cut"}}]

def section_cmds_circle(g, Ro, z0, name="Section"):
    """날부 단면(반지름 Ro 원호 = 외경, 홈 원호 = 오목) 닫힌 윤곽 1장 — 평면 z = z0."""
    a, rf, z = g["a"], g["rf"], g["z"]
    phi = math.acos((Ro * Ro + a * a - rf * rf) / (2 * Ro * a))
    P = lambda ang: [round(Ro * math.cos(ang), 6) + 0.0, round(Ro * math.sin(ang), 6) + 0.0]
    c = [{"command": "sketch.create", "params": {"plane": {"origin": [0, 0, z0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": name}}]
    for k in range(z):
        th, th2 = 2 * math.pi * k / z, 2 * math.pi * (k + 1) / z
        c.append({"command": "sketch.arc.center_point", "params": {"center": [0, 0], "start": P(th + phi), "end": P(th2 - phi)}})
        C = [round(a * math.cos(th2), 6) + 0.0, round(a * math.sin(th2), 6) + 0.0]
        c.append({"command": "sketch.arc.center_point", "params": {"center": C, "start": P(th2 - phi), "end": P(th2 + phi), "clockwise": True}})
    c.append({"command": "sketch.finish", "params": {}})
    return c

def recipe(g, stem, sc_dir):
    """SolidCraft batch 1회로 끝나는 레시피 (v1.2, 2026-11-12 속도 개선).
    평: 날부 단면 1장을 비틀어 쓸기(불리언 0번) — 실측 0.5 s(2날 D10, 저장 · STEP 포함).
    코너 R · 볼: 날 끝 회전체 ∩ 외경을 0.55D 로 키운 단면 쓸기(불리언 1번) — 실측 4날 15 s · 3날 볼 21 s.
    (옛 방식 = 홈마다 빼기 4번: 43 ~ 87 s · batch 4 ~ 6번.) 교차가 실패하면 fallback_stages(옛 방식)로."""
    D, L, Lc, R = g["D"], g["L"], g["Lc"], g["R"]
    YZ = {"origin": [0, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}
    sgn = 1 if g["hand"] == "R" else -1
    cmds = []
    if g["shape"] == "square":
        cmds += section_cmds(g, D / 2, 0.0)
        cmds += [{"command": "sketch.create", "params": {"plane": YZ, "name": "FlutePath"}},
                 {"command": "sketch.line", "params": {"points": [[0, 0], [0, Lc]]}},
                 {"command": "sketch.finish", "params": {}},
                 {"command": "solid.sweep", "params": {"sketch": "Section", "path_sketch": "FlutePath", "path": ["l1"],
                                                       "twist": f"{sgn * 360.0 * Lc / g['lead']:.4f} deg", "operation": "new_body",
                                                       "body_name": "FluteBody", "name": "Flutes"}}]
    else:
        tip = [{"command": "sketch.create", "params": {"plane": YZ, "name": "TipProfile"}}]
        if g["shape"] == "corner":
            tip += [{"command": "sketch.line", "params": {"points": [[0, Lc], [0, 0], [D / 2 - R, 0]]}},
                    {"command": "sketch.arc.center_point", "params": {"center": [D / 2 - R, R], "start": [D / 2 - R, 0], "end": [D / 2, R]}},
                    {"command": "sketch.line", "params": {"points": [[D / 2, R], [D / 2, Lc], [0, Lc]]}}]
        else:
            tip += [{"command": "sketch.arc.center_point", "params": {"center": [0, R], "start": [0, 0], "end": [R, R]}},
                    {"command": "sketch.line", "params": {"points": [[R, R]] + ([[R, Lc]] if Lc > R + 1e-9 else []) + [[0, Lc], [0, 0]]}}]
        tip += [{"command": "sketch.finish", "params": {}},
                {"command": "solid.revolve", "params": {"sketch": "TipProfile", "axis": "Z", "operation": "new_body", "body_name": "FluteBody", "name": "Tip"}}]
        path = [{"command": "sketch.create", "params": {"plane": YZ, "name": "FlutePath"}},
                {"command": "sketch.line", "params": {"points": [[0, -1], [0, Lc + 1]]}},
                {"command": "sketch.finish", "params": {}}]
        if g.get("section") == "rake":
            return recipe_rake_cut(g, stem, sc_dir, tip + path)
        Ro = min(0.55 * D, (D / 2 + g["a"] + g["rf"]) / 2)      # 외경보다 크게 — 외경 면이 겹치면 교차 실패(실측)
        cmds += tip + section_cmds(g, Ro, -1.0) + path
        cmds += [{"command": "solid.sweep", "params": {"sketch": "Section", "path_sketch": "FlutePath", "path": ["l1"],
                                                       "twist": f"{g['twist']:.4f} deg", "operation": "intersect",
                                                       "targets": ["FluteBody"], "name": "Flutes"}}]
    sk = [[0, Lc]] + [[round(r, 6), round(zq, 6)] for zq, r in g["shank"]] + [[0, L]]
    cmds += [{"command": "sketch.create", "params": {"plane": YZ, "name": "ShankProfile"}},
             {"command": "sketch.line", "params": {"points": sk, "closed": True}},
             {"command": "sketch.finish", "params": {}},
             {"command": "solid.revolve", "params": {"sketch": "ShankProfile", "axis": "Z", "operation": "new_body", "body_name": "ShankBody", "name": "Shank"}},
             {"command": "browser.visibility", "params": {"visible": False, "folder": "sketches"}},
             {"command": "save", "params": {"path": f"{sc_dir}\\{stem}.sc"}},
             {"command": "export", "params": {"path": f"{sc_dir}\\{stem}.step"}}]
    rm = max(D, g["d"]) / 2
    old = recipe_staged(g, stem, sc_dir) if g.get("section") != "rake" else {"stages": [], "screenshot": {"view": "iso", "grid": False, "axes": False, "width": 960, "height": 540, "path": f"{sc_dir}\\{stem}_3D.png"}, "check": "FreeCAD: Part.read(step) → 솔리드 2 · isValid · 부피 · optimalBoundingBox"}
    return {"tool_gen": VERSION, "design_name": stem, "sc_dir": sc_dir,
            "stages": [{"name": "1_한번에(날부 + 생크 + 저장 + STEP)", "commands": cmds,
                        "expect": {"volume_mm3": round(g["vol"]["total"], 4), "bodies": 2,
                                   "bbox": {"min": [-rm, -rm, 0], "max": [rm, rm, L]}}}],
            "fallback_stages": old["stages"],
            "screenshot": old["screenshot"],
            "how": "new_design(name=design_name) → stages 의 batch 1회(commands, expect, timings=true, verbose=false) → screenshot. "
                   "교차(Flutes) 실패 · 90 s 끊김이면 new_design 후 fallback_stages(홈마다 빼기, 단계마다 저장)로.",
            "check": old["check"]}

def shank_cmds(g, stem, sc_dir):
    YZ = {"origin": [0, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}
    sk = [[0, g["Lc"]]] + [[round(r, 6), round(zq, 6)] for zq, r in g["shank"]] + [[0, g["L"]]]
    return [{"command": "sketch.create", "params": {"plane": YZ, "name": "ShankProfile"}},
            {"command": "sketch.line", "params": {"points": sk, "closed": True}},
            {"command": "sketch.finish", "params": {}},
            {"command": "solid.revolve", "params": {"sketch": "ShankProfile", "axis": "Z", "operation": "new_body", "body_name": "ShankBody", "name": "Shank"}},
            {"command": "browser.visibility", "params": {"visible": False, "folder": "sketches"}},
            {"command": "save", "params": {"path": f"{sc_dir}\\{stem}.sc"}},
            {"command": "export", "params": {"path": f"{sc_dir}\\{stem}.step"}}]

def recipe_rake_cut(g, stem, sc_dir, tip_path):
    """v1.6 코너 R · 볼 + 경사 단면: 날 끝 회전체에서 홈마다 빼기(꺾은선 홈 곡선). 홈 1개씩 한 단계 · 단계마다 저장.
    실측(2026-11-13): D6 R0.5 4날 = 홈별 7.2 · 27.2 · 25.3 · 약 90 s(뒤로 갈수록 느림) · D4 볼 3날 = 12.3 · 20.7 · 44.1 s.
    홈 4개를 한 스케치로 한 번에 빼기는 80 s 넘어 더 느림 → 쓰지 않음."""
    D, L = g["D"], g["L"]
    Ro = 0.55 * D
    wd = sc_dir + "\\_작업\\"
    v = g["vol"]
    one = v["flute_one"]
    stages, cur = [], list(tip_path)
    for k in range(g["z"]):
        cur += gap_cmds_rake(g, k, Ro)
        if True:
            cur.append({"command": "save", "params": {"path": f"{wd}{stem}_s{len(stages) + 1}_flute{k + 1}.sc"}})
            head = "날끝회전체+" if not stages else ""
            rng = f"홈{k + 1}"
            stages.append({"name": f"{len(stages) + 1}_{head}{rng}",
                           "commands": cur, "expect": {"volume_mm3": round(v["revolve"] - (k + 1) * one, 4), "bodies": 1}})
            cur = []
    rm = max(D, g["d"]) / 2
    stages.append({"name": f"{len(stages) + 1}_생크+저장+STEP", "commands": shank_cmds(g, stem, sc_dir),
                   "expect": {"volume_mm3": round(v["total"], 4), "bodies": 2, "bbox": {"min": [-rm, -rm, 0], "max": [rm, rm, L]}}})
    return {"tool_gen": VERSION, "design_name": stem, "sc_dir": sc_dir, "stages": stages, "fallback_stages": [],
            "screenshot": {"view": "iso", "grid": False, "axes": False, "width": 960, "height": 540, "path": f"{sc_dir}\\{stem}_3D.png"},
            "how": "new_design(name=design_name) → stages 를 차례로 batch(commands, expect, timings=true, verbose=false) → screenshot. "
                   "90 s 끊김이면 _작업 의 마지막 저장본을 open 하고 다음 단계부터. 홈 곡선 = 꺾은선 "
                   f"{g.get('rk_poly_n')} 구간(곡선과 최대 {g.get('rk_poly_dev', 0):.3f} mm).",
            "check": "FreeCAD: Part.read(step) → 솔리드 2 · isValid · 부피 · optimalBoundingBox"}

# ───────────────────────── 6. 실행 ─────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(description="공구 도면 · 3D 생성기")
    ap.add_argument("spec")
    ap.add_argument("--tpl", required=True)
    ap.add_argument("--out", required=True, help="출력 상위 폴더 (공구별 하위 폴더 생성)")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--sc-root", default=None, help="SolidCraft 가 볼 Windows 경로(출력 상위 폴더와 같은 곳)")
    ap.add_argument("--check", action="store_true", help="사양 검사 · 계산만 (파일 안 만듦)")
    ap.add_argument("--recipe-only", metavar="DIR", help="기존 폴더(DIR)의 3D 레시피만 다시 씀")
    ap.add_argument("--drawing-only", metavar="DIR", help="기존 폴더(DIR)의 도면(DXF · PDF · PNG)만 다시 씀 — 3D 는 그대로")
    a = ap.parse_args(argv)
    try:
        sp = parse_spec(a.spec)
        g = derive(sp)
        stem, number, title, shape_k = names(sp, g)
        plan_layout(g)
    except Impossible as e:
        print(json.dumps({"result": "불가능", "reason": str(e), "spec": a.spec}, ensure_ascii=False, indent=1))
        return 2
    if a.recipe_only:
        stem_v = os.path.basename(a.recipe_only.rstrip("/\\"))
        sc_dir = (a.sc_root.rstrip("\\") + "\\" + stem_v) if a.sc_root else a.recipe_only
        with open(os.path.join(a.recipe_only, stem_v + "_3d_recipe.json"), "w", encoding="utf-8") as fp:
            json.dump(recipe(g, stem_v, sc_dir), fp, ensure_ascii=False, indent=1)
        print(json.dumps({"result": "레시피만 갱신", "folder": a.recipe_only}, ensure_ascii=False))
        return 0
    if a.drawing_only:
        stem_v = os.path.basename(a.drawing_only.rstrip("/\\"))
        doc, lay, notes = build_dxf(sp, g, a.tpl, a.date, stem_v, number, title, shape_k)
        ok, ext = post_check(doc, lay)
        doc.saveas(os.path.join(a.drawing_only, stem_v + ".dxf"))
        render(doc, os.path.join(a.drawing_only, stem_v + ".png"), os.path.join(a.drawing_only, stem_v + ".pdf"))
        print(json.dumps({"result": "도면만 갱신", "folder": a.drawing_only, "inside_frame": ok}, ensure_ascii=False))
        return 0
    if a.check:
        print(json.dumps({"result": "가능", "stem": stem, "volume": g["vol"]}, ensure_ascii=False, indent=1, default=float))
        return 0
    v = 1
    while os.path.exists(os.path.join(a.out, f"{stem}_v{v}")):
        v += 1          # 같은 이름 덮어쓰기 금지 — 판 올림
    stem_v = f"{stem}_v{v}"
    od = os.path.join(a.out, stem_v)
    os.makedirs(os.path.join(od, "_작업"))
    doc, lay, notes = build_dxf(sp, g, a.tpl, a.date, stem_v, number, title, shape_k)
    ok, ext = post_check(doc, lay)
    if not ok:
        print(json.dumps({"result": "도면 확인 필요", "reason": f"그린 범위 {ext} 가 틀 {FRAME} 밖"}, ensure_ascii=False))
    doc.saveas(os.path.join(od, stem_v + ".dxf"))
    render(doc, os.path.join(od, stem_v + ".png"), os.path.join(od, stem_v + ".pdf"))
    sc_dir = (a.sc_root.rstrip("\\") + "\\" + stem_v) if a.sc_root else od
    rc = recipe(g, stem_v, sc_dir)
    with open(os.path.join(od, stem_v + "_3d_recipe.json"), "w", encoding="utf-8") as fp:
        json.dump(rc, fp, ensure_ascii=False, indent=1)
    info = {"tool_gen": VERSION, "spec_raw": sp["raw"], "stem": stem_v, "number": number, "title": title,
            "derived": {k: g[k] for k in ("shape", "z", "D", "d", "L", "Lc", "R", "core_pct", "core_d", "rf", "a", "C",
                                         "lead", "twist", "zt", "neck", "helix", "hand", "taper_deg", "h6", "D_tol", "D_dev", "shank")},
            "section": {"type": g["section"], "rake_deg": g["rake"] if g["section"] == "rake" else None,
                        "flute_pct": g.get("flute_pct") if g["section"] == "rake" else None,
                        "poly_segments": g.get("rk_poly_n"), "poly_max_dev_mm": round(g["rk_poly_dev"], 4) if g.get("rk_poly_dev") is not None else None,
                        "_주": "코너R·볼 = 홈 곡선 꺾은선(이어진 원호는 SolidCraft 불리언 실패, 2026-11-13 실측) · 홈마다 빼기" if g.get("rk_poly_n") else None},
            "iso13399": {"DC": g["D"], "DMM": g["d"], "OAL": g["L"], "APMX": g["Lc"], "NOF": g["z"], "FHA": g["helix"],
                         "DN": g["neck"][0] if g["neck"] else None, "LU": g["neck"][1] if g["neck"] else g["Lc"],
                         "RE": g["R"] if g["shape"] != "square" else None,
                         "_주": "사내 표기 ↔ ISO 13399 기호 대응 [VEN-DORMERPRAMET-ISO13399]. 날장 → APMX · 넥 없을 때 LU = 날장(추정)"},
            "volume_mm3": g["vol"], "layout": {"scale": scale_txt(lay["s"]), "end_view": scale_txt(lay["se"]),
                                                "detail": scale_txt(lay["sd"]) if "sd" in lay else None,
                                                "scale_tries": [(scale_txt(s), b) for s, b in lay["tried"]], "drawn_extent": ext, "inside_frame": ok},
            "notes": notes, "신뢰도": "치수 = 입력값 · 홈 단면 · 모따기 · 테이퍼 = 추정값(모양 확인용)"}
    with open(os.path.join(od, stem_v + "_사양.json"), "w", encoding="utf-8") as fp:
        json.dump(info, fp, ensure_ascii=False, indent=1, default=float)
    print(json.dumps({"result": "완료", "folder": od, "stem": stem_v, "scale": scale_txt(lay["s"]),
                      "volume_total_mm3": round(g["vol"]["total"], 3), "inside_frame": ok}, ensure_ascii=False, indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main())
