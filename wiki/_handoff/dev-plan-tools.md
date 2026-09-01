# 독립 실행 도구 개발 계획서
작성일: 2026-06-10

---

## 전제 조건 (이미 완료)
- [x] `raw/출하현황/` 워크트리 → 루트 복원
- [ ] `재연마_월간생산일지 (6월).xls` 추가 필요 (수동)

---

## 도구 1 — generate.py 루트 복원 + GitHub Pages 충돌 수정

### 문제
- `generate.py`가 `.claude/worktrees/hardcore-hermann-b67cf1/`에 있고 루트에 없음
- GitHub Pages push 거부: remote에 로컬에 없는 commit 존재 (fetch first)

### 작업
1. 워크트리의 `generate.py` → cnc-wiki 루트로 복사
2. GitHub Pages 스크립트 내 push 로직에 `git pull --rebase` 선행 추가
3. push 실패 시 로컬 파일만 생성하고 오류 로그에 기록 (기존 동작 유지)

### 파일
- `C:\Users\TOOLKOREA\Desktop\cnc-wiki\generate.py`
- 변경 범위: GitHub Pages 업로드 함수 15~20줄

### 테스트
```powershell
cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
python generate.py --local   # GitHub 없이 로컬만 확인
```

---

## 도구 2 — 월간 작업일지 체크 알림

### 목적
매월 초 또는 매일 아침, 해당 월의 `재연마_월간생산일지 (N월).xls` 파일이 없으면 카카오톡 메모 알림

### 작업
1. `scripts/check_worklog.py` 신규 작성 (30줄 이내)
   - 오늘 날짜 기준 `raw/출하현황/재연마 작업일지(YYYY)/재연마_월간생산일지 (M월).xls` 존재 여부 확인
   - 파일 없으면 카카오톡 `KakaotalkChat-MemoChat` 호출
   - 있으면 조용히 종료
2. Cowork 스케줄 태스크: 평일 오전 8시 10분 실행

### 파일
- `scripts/check_worklog.py` (신규)
- Cowork 스케줄: `worklog-file-check` (신규)

### 알림 예시
```
⚠️ 6월 작업일지 없음
재연마_월간생산일지 (6월).xls 파일이 확인되지 않습니다.
경로: raw\출하현황\재연마 작업일지(2026)\
```

---

## 도구 3 — 연삭 테스트 Excel → Wiki 변환기

### 목적
엑셀 양식에 테스트 결과 입력 → Python 스크립트 실행 → `measurements/` 폴더에 wiki .md 파일 자동 생성

### 입력 Excel 양식 항목 (신규 생성)
| 항목 | 예시 |
|------|------|
| 테스트 날짜 | 2026-06-10 |
| 소재 | SKH51 (HSS) |
| 휠 규격 | D125×T10×H32 |
| 휠 사양 | CBN B126 V 100% |
| 주축 RPM | 4,800 |
| 휠 Vc (m/s) | 31.4 |
| 이송 속도 (mm/min) | 200 |
| 절입 깊이 ae (mm) | 0.01 |
| 측정 Ra (μm) | 0.42 |
| 측정 장비 | 미쓰토요 SJ-210 |
| 결과 판정 | 합격 / 불합격 / 추가테스트 |
| 비고 | 자유 텍스트 |

### 출력 .md 파일 (wiki/measurements/)
- 파일명: `YYYY-MM-DD_소재_휠규격.md`
- 프론트매터 + 본문 자동 생성
- 신뢰도: 실측 검증 자동 태그

### 작업
1. `templates/grinding_test_input.xlsx` 엑셀 양식 생성
2. `scripts/excel_to_wiki.py` 작성
   - xlrd/openpyxl로 Excel 읽기
   - wiki 표준 프론트매터 생성
   - `measurements/` 폴더에 저장
3. 실행 배치 파일 `run_excel_to_wiki.bat`

### 실행 방법
```powershell
# 엑셀에 데이터 입력 후 저장, 그 다음
python scripts\excel_to_wiki.py templates\grinding_test_input.xlsx
```

### 파일
- `templates/grinding_test_input.xlsx` (신규)
- `scripts/excel_to_wiki.py` (신규)
- `run_excel_to_wiki.bat` (신규)

---

## 우선순위 및 순서

| 순서 | 도구 | 예상 시간 | 이유 |
|------|------|-----------|------|
| 1 | generate.py 복원 + push 수정 | 30분 | 매일 오류 발생 중 |
| 2 | 월간 작업일지 체크 알림 | 20분 | 6월 파일 추가 후 바로 필요 |
| 3 | Excel → Wiki 변환기 | 1~2시간 | 양식 설계 필요 |

---

## 추가 아이디어 (킵)

- **휠 수명 추적기**: 드레싱 횟수·사용시간 누적 → 교체 알림
- **G코드 파라미터 검증기**: 위험 이송속도/절입 감지 후 경고
- **불량 원인 패턴 분석**: defect.html 데이터 → 월간 불량 원인 Top5 자동 집계
- **거래처별 납기 현황 알림**: 출하현황 xlsx 기반 주 1회 요약 카카오 전송
