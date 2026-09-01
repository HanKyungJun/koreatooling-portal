#!/usr/bin/env python3
"""
wiki/overview.md 통계 자동 갱신
실행: python scripts/update_overview.py
     python scripts/update_overview.py --dry-run   (미리보기만, 파일 미수정)
출력: wiki/overview.md 의 "페이지 통계" 테이블 + "성장 추이" 줄 갱신
"""
import re
import sys
import argparse
from datetime import date
from pathlib import Path

# ── 경로 ──────────────────────────────────────────────────────────────────────
BASE     = Path(__file__).resolve().parent.parent
WIKI     = BASE / "wiki"
OVERVIEW = WIKI / "overview.md"

# overview.md · index.md · log.md · _handoff/ 는 통계에서 제외
EXCLUDE_FILES = {"index.md", "overview.md", "log.md"}
EXCLUDE_DIRS  = {"_handoff"}

# 카테고리 표시명 (폴더명 → 한글 레이블)
CATEGORY_LABELS = {
    "machines":          "machines",
    "materials":         "materials",
    "tools":             "tools (연삭조건·카탈로그·수명·코어)",
    "tools/wheels":      "tools/wheels (휠·스택)",
    "tools/wheels/catalog": "tools/wheels/catalog (카탈로그 분석)",
    "gcode":             "gcode",
    "cadcam":            "cadcam",
    "comparisons":       "comparisons",
    "troubleshoot":      "troubleshoot",
    "reports":           "reports",
    "projects":          "projects",
    "scripts":           "scripts",
    "standards":         "standards",
}

# 카테고리 출력 순서
CATEGORY_ORDER = [
    "machines",
    "materials",
    "tools",
    "tools/wheels",
    "tools/wheels/catalog",
    "gcode",
    "cadcam",
    "comparisons",
    "troubleshoot",
    "reports",
    "projects",
    "scripts",
    "standards",
]


def count_pages() -> dict[str, int]:
    """wiki/ 하위 .md 파일을 폴더별로 집계 (제외 목록 반영)."""
    counts: dict[str, int] = {k: 0 for k in CATEGORY_ORDER}

    for md in WIKI.rglob("*.md"):
        # _handoff/ 제외
        if any(part in EXCLUDE_DIRS for part in md.parts):
            continue
        if md.name in EXCLUDE_FILES:
            continue

        # wiki/ 기준 상대 경로
        rel = md.relative_to(WIKI)
        parts = rel.parts  # e.g. ('tools', 'wheels', 'catalog', 'foo.md')

        # 가장 깊은 매칭 카테고리 찾기 (tools/wheels/catalog > tools/wheels > tools)
        matched = None
        for depth in range(min(len(parts) - 1, 3), 0, -1):
            key = "/".join(parts[:depth])
            if key in counts:
                matched = key
                break

        if matched:
            counts[matched] += 1

    return counts


def build_table(counts: dict[str, int]) -> tuple[str, int]:
    """마크다운 통계 테이블 문자열과 총합 반환."""
    lines = [
        "| 카테고리 | 페이지 수 |",
        "|---------|---------|",
    ]
    total = 0
    for key in CATEGORY_ORDER:
        n = counts.get(key, 0)
        if n == 0:
            continue
        label = CATEGORY_LABELS.get(key, key)
        lines.append(f"| **{label}** | {n} |")
        total += n
    lines.append(f"| **합계 (콘텐츠)** | **{total}** |")
    return "\n".join(lines), total


def update_overview(dry_run: bool = False) -> None:
    today = date.today().isoformat()
    counts = count_pages()
    new_table, total = build_table(counts)

    text = OVERVIEW.read_text(encoding="utf-8")

    # ── 1) frontmatter updated 날짜 갱신 ──────────────────────────────────────
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)

    # ── 2) "마지막 갱신:" 줄 갱신 ──────────────────────────────────────────────
    text = re.sub(
        r"> 마지막 갱신:.*",
        f"> 마지막 갱신: {today} (자동 갱신 — update_overview.py)",
        text,
    )

    # ── 3) 통계 테이블 교체 ────────────────────────────────────────────────────
    # "## 페이지 통계" 섹션의 테이블 전체를 교체
    text = re.sub(
        r"(## 페이지 통계.*?\n)\n\|.*?(?=\n\n|\n>|\n##)",
        lambda m: m.group(1) + "\n" + new_table,
        text,
        flags=re.DOTALL,
    )

    # ── 4) 성장 추이 줄 갱신 ─────────────────────────────────────────────────
    text = re.sub(
        r"> \*\*성장 추이\*\*:.*",
        f"> **성장 추이**: 현재 **{total}페이지** ({today} 기준)",
        text,
    )

    if dry_run:
        print("=== DRY RUN — overview.md 변경 예정 내용 ===")
        print(f"  날짜: {today}")
        print(f"  총 페이지: {total}")
        print("\n카테고리별:")
        for key in CATEGORY_ORDER:
            n = counts.get(key, 0)
            if n:
                print(f"  {key:35s}: {n}")
        print("\n[파일 미수정]")
        return

    OVERVIEW.write_text(text, encoding="utf-8")
    print(f"✅ overview.md 갱신 완료 ({today}, 총 {total}페이지)")
    for key in CATEGORY_ORDER:
        n = counts.get(key, 0)
        if n:
            print(f"  {key:35s}: {n}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="wiki/overview.md 통계 자동 갱신")
    parser.add_argument("--dry-run", action="store_true", help="파일 수정 없이 미리보기만")
    args = parser.parse_args()
    update_overview(dry_run=args.dry_run)
