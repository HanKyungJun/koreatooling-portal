"""
Trico ERP → Excel 자동 스크랩  v3.0  (핫키 방식)
──────────────────────────────────────────────
사용법:
  python trico_scraper.py

실행하면 백그라운드에서 대기.
Trico 창에서 조회 완료 후 F10 누르면 스크랩 실행.
ESC 누르면 스크립트 종료.

설치:
  pip install pyautogui pywin32 keyboard openpyxl
"""

import os, sys, time, glob
from pathlib import Path
from datetime import datetime

import pyautogui
import win32gui, win32con
import keyboard

pyautogui.FAILSAFE = True
pyautogui.PAUSE    = 0.05

# ── 저장 폴더 ─────────────────────────────────────────────────────────────────
SAVE_DIR = Path(r"C:\Users\TOOLKOREA\Desktop\cnc-wiki\outputs\trico_exports")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# ── 설정 ─────────────────────────────────────────────────────────────────────
CFG = {
    "grid_y_ratio":     0.62,  # 창 높이 중 그리드 Y 비율
    "xlsx_submenu_idx": 2,     # 서브메뉴: 0=인쇄, 1=미리보기, 2=저장Excel(xlsx)
    "hotkey":           "f10", # 스크랩 핫키
}


# ══════════════════════════════════════════════════════════════════════════════
# 창 찾기
# ══════════════════════════════════════════════════════════════════════════════
def find_trico_hwnd():
    keywords = ["코고툴", "코리아툴링", "Trico", "TRICO"]
    found = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if any(k in t for k in keywords):
                found.append(hwnd)
    win32gui.EnumWindows(cb, None)
    return found[0] if found else None


def get_grid_pos(hwnd):
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    x = (l + r) // 2
    y = t + int((b - t) * CFG["grid_y_ratio"])
    return x, y


# ══════════════════════════════════════════════════════════════════════════════
# 스크랩 실행
# ══════════════════════════════════════════════════════════════════════════════
def do_scrape():
    hwnd = find_trico_hwnd()
    if not hwnd:
        print("❌ Trico 창 없음")
        return

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 스크랩 시작 ─ {win32gui.GetWindowText(hwnd)}")

    cx, cy = get_grid_pos(hwnd)

    # ── 1. 우클릭 ─────────────────────────────────────────────────────────
    # 이미 Trico가 포커스 상태 (사용자가 F10 누른 시점)
    # SetForegroundWindow 호출하지 않음 → 팝업 메뉴 유지
    print(f"  우클릭 ({cx}, {cy})")
    pyautogui.rightClick(cx, cy)
    time.sleep(0.6)

    # ── 2. 키보드 탐색 (포커스 변경 없음) ────────────────────────────────
    # '인쇄 및 저장'이 첫 번째 항목 → Home으로 선택
    print("  Home → 인쇄 및 저장 선택")
    pyautogui.press("home");  time.sleep(0.25)

    # Right → 서브메뉴 열기
    print("  Right → 서브메뉴")
    pyautogui.press("right"); time.sleep(0.45)

    # Down N번 → 저장 Excel (xlsx)
    pyautogui.press("home"); time.sleep(0.15)
    for i in range(CFG["xlsx_submenu_idx"]):
        print(f"  Down {i+1}")
        pyautogui.press("down"); time.sleep(0.15)

    # Enter 실행
    print("  Enter → 저장 실행")
    pyautogui.press("enter"); time.sleep(1.2)

    # ── 3. 저장 다이얼로그 처리 ───────────────────────────────────────────
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname    = f"trico_{ts}.xlsx"
    out_path = SAVE_DIR / fname

    print(f"  파일명 입력: {fname}")
    pyautogui.hotkey("ctrl", "a"); time.sleep(0.1)
    pyautogui.typewrite(str(out_path), interval=0.025)
    time.sleep(0.1)
    pyautogui.press("enter"); time.sleep(1.5)

    # ── 4. 결과 확인 ──────────────────────────────────────────────────────
    if out_path.exists():
        sz = out_path.stat().st_size // 1024
        print(f"  ✅ 저장 완료: {out_path}  ({sz} KB)")
        return out_path

    # 폴백: 최근 10초 안에 저장된 파일 찾기
    recent = sorted(SAVE_DIR.glob("*.xlsx"), key=os.path.getmtime, reverse=True)
    if recent and (time.time() - os.path.getmtime(recent[0])) < 10:
        print(f"  ✅ 저장 완료 (감지): {recent[0]}")
        return Path(recent[0])

    print("  ❌ 파일 저장 실패")
    print("     → CFG[xlsx_submenu_idx] 값을 바꿔보세요 (현재:", CFG["xlsx_submenu_idx"], ")")
    print("     → 저장 다이얼로그가 열렸으면 Esc 로 닫고 다시 시도")
    return None


# ══════════════════════════════════════════════════════════════════════════════
# 진입점
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    hotkey = CFG["hotkey"]
    print(f"Trico 스크랩 대기 중...")
    print(f"  {hotkey.upper()} : 스크랩 실행  (Trico 창에서 누르세요)")
    print(f"  ESC : 종료\n")

    keyboard.add_hotkey(hotkey, do_scrape, suppress=True)
    keyboard.wait("esc")
    print("종료.")
