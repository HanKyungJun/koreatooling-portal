---
name: "wiki-lint"
description: "[위키 검수] 프론트매터·출처 누락·고아 페이지·빨간 링크를 점검합니다. \"위키 검수\", \"lint 돌려줘\", \"품질 점검\" 으로 실행합니다."
---

# wiki-lint 스킬

`wiki/` 폴더 전체를 스캔해서 품질 문제를 체크리스트로 출력합니다.

## 위키 경로

`device_bash` 에서 `$HOME/mnt/cnc-wiki/wiki` (PC 쪽 원래 위치: `C:\Users\TOOLKOREA\Desktop\cnc-wiki\wiki\`).
세션마다 마운트 경로가 바뀌므로 `/sessions/...` 같은 절대경로를 쓰지 않습니다(daily-report-check §① 과 같은 원칙 —
2026-09-08 옛 경로 때문에 점검이 조용히 0건을 낸 사례).

점검 제외 폴더: `wiki/_handoff/`(핸드오프) · `wiki/_private/`(실명 원본 — 공개본과 겹쳐 같은 문제가 두 번 잡힘) ·
`wiki/_backup/`(백업). `.bak_*` 파일은 확장자가 `.md` 가 아니라 자동으로 빠집니다.
`wiki/reports/09_업무일정/주간브리핑/` 은 예약 작업이 매주 만드는 기록물이라 ③ 고아 · ④ index 미등재 ·
① `sources` 누락을 지적하지 않습니다(CLAUDE.md §8-4 · decisions 2026-09-23 (2)). 다른 항목은 그대로 봅니다.

---

## 점검 항목 (5가지)

### ① 프론트매터 누락·불완전

각 `.md` 파일을 읽어 YAML 프론트매터(`---` 블록)가 있는지 확인합니다.

누락 항목:
- `type` 필드 없음
- `updated` 필드 없음
- `sources` 필드 없음 (빈 배열 `[]`는 허용, 완전 누락만 체크)
- `tags` 필드 없음

`wiki/_handoff/`, `wiki/index.md`, `wiki/log.md`, `wiki/overview.md`는 점검 제외합니다.

### ② 출처 없는 수치

본문에 숫자 + 단위 패턴(RPM, m/s, mm, μm, bar, %, mm³/(mm·s) 등)이 있는데
`[XXX-YYY]` 형식의 인용 ID가 없는 문장을 찾습니다. 같은 줄에 신뢰도 표기(제조사 기준 · 실측 검증 · 사내 경험값 ·
추정값 · 확인 필요)가 있으면 통과로 봅니다. **어림 검사**라 표 안 수치 · 출하 수량처럼 출처가 표 위에 한 번 적힌
경우도 잡힙니다 — 파일별 줄 수만 보고하고, 한 줄씩 고칠지는 사용자가 고른 파일만 `sed -n` 으로 열어 판단합니다.

단, 아래는 제외합니다:
- 날짜 (YYYY-MM-DD)
- 섹션 번호 (§1, §2 등)
- 버전 표기 (v1, v2)
- 코드 블록(``` 내부)

### ③ 고아 페이지 (인바운드 링크 0개)

`wiki/` 전체에서 `[[페이지명]]` 또는 `[[페이지명|텍스트]]` 패턴을 수집합니다.
어떤 파일에서도 링크되지 않은 페이지를 고아 페이지로 표시합니다.
(`wiki/index.md`에서의 링크는 인바운드로 카운트합니다.)

### ④ index.md 미등재

`wiki/index.md`를 읽고, `wiki/` 하위에 존재하는 `.md` 파일 중
index.md에 언급되지 않은 파일을 찾습니다. 「언급」은 index.md 의 위키링크로 그 파일에 닿거나 전체 경로가 적힌 경우만 —
파일 이름 글자만 겹치는 것(`README` 가 `repairs/README` 에 들어 있음 등)은 등재로 보지 않습니다.

제외 대상: `wiki/index.md` 자체, `wiki/log.md`, `wiki/overview.md`, `wiki/_handoff/` 폴더

### ⑤ 빨간 링크 (언급만 되고 파일 없음)

`[[페이지명]]` 링크 대상 중 실제로 존재하지 않는 파일을 찾습니다.
가장 가까운 실제 파일명을 제안합니다 (파일명 유사도 기준).
링크 해석은 Obsidian 과 같게 — `[[이름]]` 은 파일명, `[[폴더/이름]]` 은 경로 끝 일치. `<!-- -->` 주석 안 링크(양식 예시)는 세지 않습니다. 첨부 링크(`.xlsx` · `.csv` ·
`.docx`)는 파일이 있으면 통과. `wiki/log.md` 안의 빨간 링크는 이력 기록이라 따로 개수만 적고 고치지 않습니다.

---

## 출력 형식

```
## 위키 품질 점검 결과 — YYYY-MM-DD

총 점검 파일: N개 | 문제 발견: M건

---

### ① 프론트매터 누락·불완전
[문제 없음] 또는:
- ❌ `wiki/tools/example.md` — `type` 필드 누락
- ⚠️ `wiki/materials/sus304.md` — `sources` 필드 없음

### ② 출처 없는 수치 (추정값 미표기 포함)
[문제 없음] 또는:
- ⚠️ `wiki/cadcam/연삭-테스트.md` 12행 — "Ra 0.4 μm" (출처·신뢰도 미표기)
- ⚠️ `wiki/tools/wheels/휠-20도-Ø125-1-1.md` 34행 — "3,050 rpm" (출처 없음)

### ③ 고아 페이지
[없음] 또는:
- 🔴 `wiki/gcode/g83-드릴사이클.md` — 다른 페이지에서 링크 없음

### ④ index.md 미등재
[없음] 또는:
- ➕ `wiki/projects/d8-4날-실험.md` — index.md에 없음

### ⑤ 빨간 링크
[없음] 또는:
- 🔗 `[[휠-연삭조건]]` (wiki/tools/wheels/휠-20도.md 내) — 파일 없음
  → 혹시 `휠-20도-Ø125-1-1.md`를 의미하나요?

---

### 권고 조치 요약
1. [우선순위 높음] ...
2. [우선순위 중간] ...
```

---

## 실행 방법

파일마다 `Read` 로 여는 방식은 쓰지 않습니다(190개 넘는 파일을 하나씩 읽어 느리고 비쌈). 아래 한 번의
`device_bash` 실행으로 5가지를 모두 셉니다(2026-11-16 실측: 190개 · 약 5 s). 폴더가 연결되지 않아 `cd` 가 실패하면
점검하지 말고 사용자에게 알립니다.

```bash
cd "$HOME/mnt/cnc-wiki" && python3 - <<'PY'
import os, re, difflib
from collections import Counter, defaultdict
W = "wiki"
SKIP_DIRS = {"_handoff", "_private", "_backup"}        # 핸드오프 · 실명 원본 · 백업
SKIP_TOP = {"index.md", "log.md", "overview.md"}
BRIEF = "wiki/reports/09_업무일정/주간브리핑/"         # 자동 생성 — 고아 · 미등재 · sources 누락 제외(CLAUDE.md §8-4)
files = []
for root, ds, fs in os.walk(W):
    ds[:] = [d for d in ds if not (root == W and d in SKIP_DIRS) and not d.startswith(".")]
    files += [os.path.join(root, f).replace("\\", "/") for f in fs if f.endswith(".md")]
files.sort()
rel = {f[len(W) + 1:-3]: f for f in files}              # "tools/wheels/index" → 파일
stems = defaultdict(list)
for r in rel: stems[os.path.basename(r)].append(r)
text = {f: open(f, encoding="utf-8", errors="replace").read().lstrip("﻿") for f in files}
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
UNIT = re.compile(r"\d[\d,.]*\s?(RPM|rpm|m/s|mm/min|mm/rev|mm³|μm|um|mm|bar|%|°|N·m|kW)(?![A-Za-z])")
CITE = re.compile(r"\[[A-Z]{2,}-[^\]]+\]|제조사 기준|실측 검증|사내 경험값|추정값|확인 필요")
fm_bad, nums, inbound, red, idx_hit = [], defaultdict(list), Counter(), [], set()
NOTE = re.compile(r"<!--.*?-->", re.S)                  # 주석 안 양식 예시 링크는 세지 않음
for f, t in text.items():
    top = f.count("/") == 1 and os.path.basename(f) in SKIP_TOP
    fm, body = None, t
    if t.startswith("---") and (e := t.find("\n---", 3)) > 0:
        fm, body = t[3:e], t[e + 4:]
    if not top:
        miss = [k for k in ("type", "updated", "sources", "tags") if not fm or not re.search(rf"^{k}\s*:", fm, re.M)]
        if f.startswith(BRIEF) and fm is not None: miss = [k for k in miss if k != "sources"]
        if miss: fm_bad.append((f, "프론트매터 없음" if fm is None else ", ".join(miss) + " 없음"))
        code = False
        for n, line in enumerate(body.split("\n"), 1):
            if line.strip().startswith("```"): code = not code; continue
            s = re.sub(r"\d{4}-\d{2}-\d{2}|§\d+|\bv\d+(\.\d+)?", "", line)
            if not code and UNIT.search(s) and not CITE.search(line): nums[f].append(n)
    for m in LINK.finditer(NOTE.sub("", t)):
        tgt = m.group(1).strip()
        if not tgt.endswith("/") and os.path.isfile(f"{W}/{tgt}"): continue      # 첨부(xlsx · csv · docx)
        tgt = tgt.removesuffix(".md")
        hit = [tgt] if tgt in rel else [r for r in rel if r.endswith("/" + tgt)] if "/" in tgt else stems.get(tgt, [])
        if not hit and (os.path.isfile(f"{W}/{tgt}.md") or os.path.isfile(f"{W}/_handoff/{tgt}.md")): continue
        if f == f"{W}/index.md": idx_hit.update(hit)
        if hit:
            for h in hit:
                if rel[h] != f: inbound[h] += 1
        else:
            sug = difflib.get_close_matches(os.path.basename(tgt), list(stems), 1, 0.6)
            red.append((f, tgt, sug[0] if sug else "-"))
idx = text.get(f"{W}/index.md", "")
pages = [r for r in rel if not (r.count("/") == 0 and r + ".md" in SKIP_TOP) and not rel[r].startswith(BRIEF)]
orph = [rel[r] for r in pages if inbound[r] == 0]
noidx = [rel[r] for r in pages if r not in idx_hit and r not in idx]   # 링크로 걸렸거나 전체 경로가 적힌 것만 등재로 봄
red_log = [x for x in red if x[0] == f"{W}/log.md"]; red = [x for x in red if x[0] != f"{W}/log.md"]
print(f"점검 파일 {len(files)}개 (제외 폴더: {', '.join(sorted(SKIP_DIRS))})")
print(f"① 프론트매터 {len(fm_bad)}건"); [print(f"  - {a} — {b}") for a, b in fm_bad]
top15 = sorted(nums.items(), key=lambda x: -len(x[1]))[:15]
print(f"② 출처 · 신뢰도 없는 수치 줄 {sum(map(len, nums.values()))}개 / 파일 {len(nums)}개 — 많은 순 15개")
[print(f"  - {a} — {len(v)}줄 (예: {', '.join(map(str, v[:3]))}행)") for a, v in top15]
print(f"③ 고아 {len(orph)}건"); [print(f"  - {a}") for a in orph]
print(f"④ index.md 미등재 {len(noidx)}건"); [print(f"  - {a}") for a in noidx]
print(f"⑤ 빨간 링크 {len(red)}건 (+ log.md 이력 안 {len(red_log)}건 — 이력이라 고치지 않음)")
[print(f"  - [[{b}]] ({a}) → " + (f"혹시 {c}?" if c != "-" else "비슷한 파일 없음")) for a, b, c in red]
PY
```

1. 위 출력을 「출력 형식」으로 옮겨 보고합니다. 「0건」은 스크립트가 끝까지 돌고 `점검 파일 N개` 가 나왔을 때만
   씁니다(출력이 비거나 오류면 0건이라 하지 않음).
2. 문제가 많을 경우 (20건 이상) 파일별로 요약해서 표로 제공합니다.
3. 특정 파일의 줄 내용이 필요하면 그 파일만 `sed -n 'N,Mp'` 로 엽니다.

---

## 주의사항

- `raw/` 폴더는 점검 대상이 아닙니다.
- 자동 수정은 하지 않습니다. 수정은 사용자 확인 후 별도로 진행합니다.
- 점검 결과를 바탕으로 수정할 페이지가 있으면 `wiki-new-page` 또는 직접 `Edit` 도구로 처리합니다.
- 출처 등재가 필요하면 `source-add` 스킬을 사용합니다.