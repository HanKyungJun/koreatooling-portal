#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Weekly Calendar Overview — 「+N개 더」 태그를 볼 수 있게 수정 (2026-10-19)
실행: python scripts/patch_calendar_moretag_20261019.py

문제: 셀당 태그를 3개까지만 표시하고 나머지는 「+N개 더」로 접었는데,
      그 칩에 tooltip도 클릭 동작도 없어서 **숨은 항목을 볼 방법이 전혀 없었다**.
      10/27(발표자료 제출 마감)·11/10(Claude 발표 2차)처럼 놓치면 안 되는 항목이 접힘.

수정:
  1. MAX 3 → 4  (현재 최다 태그가 4개라 대부분 접히지 않게 됨)
  2. 넘치는 태그를 지우지 않고 `display:none` 으로 DOM 에 남긴다
  3. 「+N개 더」 칩에 ① 숨은 항목 전체를 title 툴팁으로 노출 ② 클릭하면 펼쳐짐
  4. 칩에 cursor:pointer — 클릭 가능하다는 것이 보이게

안전장치: 기대 원본을 정확히 1회 찾을 때만 치환. 불일치 시 아무것도 쓰지 않고 중단.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

ARTIFACT = Path(r'C:\Users\TOOLKOREA\Documents\Claude\Artifacts\weekly-calendar-overview\index.html')

# ── 1. CSS: 클릭 가능 표시 ────────────────────────────────────────────────
OLD_CSS = '''    .ev-tag.more     { background: #f5f5f7; color: #6e6e73; }'''
NEW_CSS = '''    .ev-tag.more     { background: #f5f5f7; color: #6e6e73; cursor: pointer; }
    .ev-tag.more:hover { background: #e5e5ea; color: #1d1d1f; }'''

# ── 2. 렌더링 로직 ────────────────────────────────────────────────────────
OLD_RENDER = '''    const MAX=3;
    let evTags=allTags.slice(0,MAX).map(e=>`<div class="ev-tag ${e.t}" title="${e.l}">${e.l}</div>`).join('');
    if(allTags.length>MAX) evTags+=`<div class="ev-tag more">+${allTags.length-MAX}개 더</div>`;'''

NEW_RENDER = '''    const MAX=4;
    let evTags=allTags.slice(0,MAX).map(e=>`<div class="ev-tag ${e.t}" title="${esc(e.l)}">${e.l}</div>`).join('');
    if(allTags.length>MAX){
      const rest=allTags.slice(MAX);
      /* 숨은 태그는 지우지 않고 DOM 에 남겨 둔다 — 「+N개 더」 클릭 시 펼침 */
      evTags+=rest.map(e=>`<div class="ev-tag ${e.t} ev-hidden" style="display:none" title="${esc(e.l)}">${e.l}</div>`).join('');
      evTags+=`<div class="ev-tag more" title="${esc(rest.map(e=>e.l).join(' / '))}" onclick="expandTags(this)">+${rest.length}개 더</div>`;
    }'''

# ── 3. 헬퍼 함수 2개 추가 (renderProdBadge 앞) ────────────────────────────
OLD_FUNC = '''function renderProdBadge(key){'''
NEW_FUNC = '''function esc(s){
  return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;')
                  .replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

/* 「+N개 더」 클릭 → 같은 셀의 숨은 태그를 펼치고 칩은 제거 */
function expandTags(el){
  el.parentElement.querySelectorAll('.ev-hidden')
    .forEach(n=>{ n.style.display=''; n.classList.remove('ev-hidden'); });
  el.remove();
}

function renderProdBadge(key){'''

PATCHES = [
    ('CSS — more 칩 클릭 가능 표시', OLD_CSS,    NEW_CSS),
    ('렌더링 — MAX 4 + 툴팁 + 펼치기', OLD_RENDER, NEW_RENDER),
    ('헬퍼 — esc() · expandTags()',   OLD_FUNC,   NEW_FUNC),
]


def main():
    if not ARTIFACT.exists():
        print('[patch] ERROR - artifact not found'); sys.exit(1)
    html = ARTIFACT.read_text(encoding='utf-8')

    missing = [n for n, old, _ in PATCHES if html.count(old) != 1]
    if missing:
        print('[patch] ABORT - 기대 원본을 1회 정확히 찾지 못함 (아무것도 쓰지 않음):')
        for n in missing:
            print(f'          - {n}')
        sys.exit(2)

    for n, old, new in PATCHES:
        html = html.replace(old, new, 1)
        print(f'[patch] OK - {n}')

    ARTIFACT.write_text(html, encoding='utf-8')
    print(f'[patch] DONE - {ARTIFACT}')


if __name__ == '__main__':
    main()
