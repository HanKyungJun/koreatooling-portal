# -*- coding: utf-8 -*-
"""
7d883bd 커밋에 실수로 포함된 손상된 빈 파일(깨진 바이너리 이름)을 워킹트리와
git 인덱스에서 제거하는 스크립트.

사용법 (PowerShell, cnc-wiki 폴더에서):
    python cleanup_stray_files.py

git rm 만 수행하고 커밋/푸시는 하지 않습니다. 실행 후 직접 확인하고
git commit / git push 하세요.
"""
import subprocess
import sys

OLD = "5d906c8"
NEW = "7d883bd"

out = subprocess.run(
    ["git", "diff", "--name-status", "-z", OLD, NEW],
    capture_output=True, cwd=".",
)
raw = out.stdout
parts = raw.split(b"\x00")
# parts alternate: status, path, status, path, ...
pairs = []
i = 0
while i < len(parts) - 1:
    status = parts[i]
    path = parts[i + 1]
    if status:
        pairs.append((status, path))
    i += 2

to_remove = [p for (s, p) in pairs if s == b"A"]

print(f"삭제 대상 {len(to_remove)}개 (git add . 로 잘못 포함된 손상 파일):")
for p in to_remove:
    print(" -", p)

if not to_remove:
    print("삭제 대상 없음 — 종료")
    sys.exit(0)

confirm = input("\n위 파일들을 git rm -f 로 제거할까요? (y/N): ").strip().lower()
if confirm != "y":
    print("취소됨")
    sys.exit(0)

cmd = ["git", "rm", "-f", "--"] + to_remove
res = subprocess.run(cmd)
if res.returncode != 0:
    print("git rm 실패 — 수동으로 확인하세요")
    sys.exit(1)

print("\n완료. 다음을 실행해 커밋/푸시하세요:")
print('  git commit -m "잘못 커밋된 손상 파일 제거"')
print("  git push")
