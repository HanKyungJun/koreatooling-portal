# SECURITY_NOTES.md — cnc-wiki 보안 정리 메모

이 파일은 기능 작업과 보안 작업이 섞이지 않도록, 나중에 분리해서 처리할 보안 TODO를 모아두는 메모입니다.

> **2026-05-11 업데이트**: 보안 정리 1차 작업 완료. 아래 ✅ 표시 항목은 처리됨, ⚠️ 표시 항목은 한경준님 직접 조치 필요.

## 우선 정리할 항목

- `generate.py`
  - ✅ GitHub 토큰을 코드에서 제거하고 `os.getenv('GITHUB_TOKEN')`으로 변경 (2026-05-11)
  - ⚠️ **한경준님 직접 조치**: 이미 git commit `2f51bcd`에 포함된 토큰을 GitHub에서 폐기·재발급 필요
    - URL: https://github.com/settings/tokens
    - 폐기 대상: `ghp_Y6EOvm...xpQ` 로 시작하는 토큰
    - 새 토큰을 `.env` 파일의 `GITHUB_TOKEN=` 에 입력
  - ✅ `STAFF_PASS`를 환경변수로 분리 (기본값 '1234' 유지, .env에서 덮어쓰기 가능)

- `app.py`
  - ✅ `.gitignore`에 `client_secret*.json`, `token*.json`, `sheets_id.json`, `.env` 추가 (2026-05-11)
  - ✅ `FORM_SHEET_ID`를 환경변수로 이동 (2026-05-11)
  - ⚠️ **한경준님 직접 조치**: 위 JSON 파일들이 이미 commit에 포함됨. 로컬 git만 쓰면 외부 노출 없으나, GitHub push 예정이면 다음 중 선택:
    - **(a) 단순 추적 중단** (이미 적용): `git rm --cached` 실행 → 이후 commit부터는 추적 안 됨. 단 과거 commit에는 남음.
    - **(b) 이력 완전 제거**: BFG Repo-Cleaner 또는 `git filter-branch`로 git 이력 재작성. 복잡하고 위험.
    - **(c) repo 재초기화**: `.git/` 삭제 후 `git init` 다시. 이력 손실 (현재 4 commit만 있어 부담 적음).
  - ⚠️ Google OAuth 토큰 재발급 권장 (보수적 대응):
    - https://console.cloud.google.com → 해당 프로젝트 → API 및 서비스 → 사용자 인증 정보
    - 기존 OAuth 클라이언트 시크릿 무효화 후 새로 생성
    - 새 `client_secret_*.json` 다운로드 → 같은 폴더에 교체

- `setup_sheets.py`, `scripts/*.py`
  - [ ] Google OAuth 파일명을 공통 설정으로 분리 (미진행, 향후 작업)
  - [ ] 토큰 파일은 로컬 실행 결과물로만 취급 (.gitignore로 이미 제외됨, 코드 수정 미진행)

## 외부 공유 전 체크 (GitHub repo 공개·Netlify 배포 등)

- [ ] ⚠️ GitHub 토큰 재발급 완료 (한경준님 조치 필요)
- [ ] ⚠️ Google OAuth 토큰/시크릿 재발급 검토 (한경준님 조치 필요)
- [x] ✅ `.gitignore` 구성 완료 (2026-05-11)
- [x] ✅ 코드 안 비밀번호·토큰 제거 (generate.py, app.py 완료. scripts/* 향후)
- [ ] Netlify/GitHub 배포물에 내부 파일이 포함되지 않는지 확인 (배포 시점에 확인)
- [ ] `scripts/*.py` 의 OAuth 파일명 설정 통일 (향후)

## 사용자 작업 절차 (2026-05-11 정리 후)

1. **GitHub 토큰 재발급** (위 ⚠️ 항목)
2. **`.env` 파일 생성**:
   ```powershell
   cd C:\Users\TOOLKOREA\Desktop\cnc-wiki
   copy .env.example .env
   notepad .env
   ```
3. `.env` 파일에서 `GITHUB_TOKEN=` 줄의 값을 새로 발급받은 토큰으로 교체. 다른 값(STAFF_PASS, FORM_SHEET_ID 등)도 실제 값으로 채움.
4. **python-dotenv 설치** (한 번만):
   ```powershell
   pip install python-dotenv
   ```
5. **민감 파일 git 추적 중단**:
   ```powershell
   git rm --cached client_secret_*.json
   git rm --cached token.json token_readonly.json token_sheets.json
   git rm --cached sheets_id.json
   ```
   (파일 자체는 디렉터리에 그대로 남음 — git 추적만 중단)
6. **테스트**: `python generate.py --local` 실행해서 에러 없이 작동 확인
7. **Commit**: 변경 사항 통합 commit (PowerShell 명령은 Cowork가 제공)

## 원칙

- 기능 개선과 보안 정리는 커밋/작업 단위를 나눕니다.
- 비밀값은 답변, 문서, 로그에 그대로 적지 않습니다.
- 공개 저장소를 만들기 전에는 현재 폴더 전체를 그대로 올리지 않습니다.
- `.env` 파일은 **절대 git에 포함되지 않습니다** (.gitignore로 보장).
- `.env.example`은 git에 포함되어 다른 협업자/환경에 참고가 됨 (실제 값은 비어있음).
