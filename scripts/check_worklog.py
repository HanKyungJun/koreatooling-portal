"""
월간 작업일지 파일 존재 여부 확인 스크립트.
파일이 없으면 stdout에 알림 메시지를 출력하고 exit code 1로 종료.
파일이 있으면 조용히 exit code 0으로 종료.
스케줄 태스크에서 이 스크립트를 실행하고 결과에 따라 카카오톡 메모를 전송.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from datetime import datetime

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKLOG_DIR = os.path.join(BASE_DIR, 'raw', '출하현황')

def main():
    today = datetime.now()
    year, month = today.year, today.month

    folder = os.path.join(WORKLOG_DIR, f'재연마 작업일지({year})')
    fname  = f'재연마_월간생산일지 ({month}월).xls'
    fpath  = os.path.join(folder, fname)

    if os.path.exists(fpath):
        sys.exit(0)

    rel_path = os.path.join(f'raw\\출하현황\\재연마 작업일지({year})\\', fname)
    print(f'⚠️ {month}월 작업일지 없음\n'
          f'{fname} 파일이 확인되지 않습니다.\n'
          f'경로: {rel_path}')
    sys.exit(1)

if __name__ == '__main__':
    main()
