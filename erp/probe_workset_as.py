#!/usr/bin/env python3
"""
재연마A/S 현황 — work_set ID 탐침  v2
──────────────────────────────────────
v1 실패 원인(2026-09-04): 대조군에 파라미터를 3개만 보내 500 이 났다.
  기존 수주() 는 파라미터를 15개 보낸다. 화면 ID 가 아니라 파라미터 부족이었다.
  또 raise_for_status() 가 500 응답 "본문의 SOAP fault" 를 버리고 있었다.

v2 변경:
  - HTTP 상태와 무관하게 응답 본문을 읽어 faultstring / ExceptionMessage 를 출력
  - 대조군을 3개로 나눠 "판별 기준" 을 먼저 만든다
      A. 정식 호출(수주)                -> 연결·인증 정상 확인
      B. 존재하는 화면 + 빈 파라미터     -> "화면은 있는데 파라미터 부족" 일 때의 메시지
      C. 없는 화면      + 빈 파라미터     -> "화면 자체가 없을" 때의 메시지
    B 와 C 의 메시지가 다르면, 그 차이로 후보를 판별할 수 있다.

실행:  python erp/probe_workset_as.py
       python erp/probe_workset_as.py sdb100_jae_g20 sdb110_jae_g00

성격:  읽기 전용(FillDataSetEx 조회). 등록/수정/삭제 없음.
"""
import sys, re, gzip, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import trico_client as tc
from trico_client import TricoClient

CONTROL_OK  = "sdb100_jae_g10"      # 재연마수주 등록 — 존재 확정
CONTROL_BAD = "zzz999_nope_g99"     # 존재하지 않음

CANDIDATES = [
    "sdb100_jae_g00", "sdb100_jae_g20", "sdb100_jae_g30",
    "sdb110_jae_g00", "sdb110_jae_g10",
    "sdb120_jae_g00", "sdb120_jae_g10",
    "sdb200_jae_g00",
    "sdb100_as_g00", "sdb100_jae_as_g00", "sdb100_jaeas_g00",
    "as100_jae_g00",
    "PPC100_jae_g00", "PPC110_jae_g00", "PPC130_jae_g00",
    "lem100_jae_g00", "lem110_jae_g00",
]


def raw_call(client, work_set, params):
    """HTTP 상태와 무관하게 본문을 읽어 돌려준다 (500 의 fault 를 버리지 않는다)."""
    env = client._envelope(client._data_con_xml(work_set, params)).encode("utf-8")
    try:
        r = client.session.post(
            tc.SVC_URL, data=env,
            headers={"SOAPAction": '"http://tempuri.org/ITricoService/FillDataSetEx"'},
            timeout=20,
        )
    except Exception as e:
        return None, f"[전송실패] {type(e).__name__}: {e}"

    body = r.content
    try:
        body = gzip.decompress(body)
    except Exception:
        pass
    text = body.decode("utf-8", errors="replace")

    fault  = re.search(r"<[^>]*faultstring[^>]*>(.*?)</", text, re.S)
    detail = re.search(r"<[^>]*ExceptionMessage[^>]*>(.*?)</", text, re.S)
    msg = ""
    if fault:
        msg = fault.group(1).strip()
    if detail:
        msg += (" | " if msg else "") + detail.group(1).strip()
    if not msg:
        msg = "(fault 메시지 없음)" if r.status_code != 200 else "(정상 응답)"
    return r.status_code, re.sub(r"\s+", " ", msg)[:300]


def main():
    args    = sys.argv[1:]
    targets = args if args else CANDIDATES
    client  = TricoClient()

    print("=" * 74)
    print("A) 정식 호출 — 연결·인증 확인 (파라미터 전체를 보내는 수주 화면)")
    print("=" * 74)
    try:
        df = client.수주(fr_dt="2026-08-01")
        print(f"  [정상] {len(df)}행 / {len(df.columns)}열 — 접속과 인증에 문제 없음")
    except Exception as e:
        print(f"  [중단] 정식 호출조차 실패 -> {str(e)[:250]}")
        print("         ERP 접속·인증 문제입니다. 탐침을 진행할 수 없습니다.")
        return 1

    print()
    print("=" * 74)
    print("B/C) 판별 기준 만들기 — 빈 파라미터로 '있는 화면' vs '없는 화면' 비교")
    print("=" * 74)
    sb, mb = raw_call(client, CONTROL_OK,  {})
    print(f"  B. 있는 화면 {CONTROL_OK}")
    print(f"     HTTP {sb}  |  {mb}")
    sc, mc = raw_call(client, CONTROL_BAD, {})
    print(f"  C. 없는 화면 {CONTROL_BAD}")
    print(f"     HTTP {sc}  |  {mc}")
    print()
    if mb != mc:
        print("  ==> B 와 C 의 메시지가 다릅니다. 이 차이로 후보를 판별할 수 있습니다.")
        print(f"      '있는 화면' 의 신호: {mb[:120]}")
    else:
        print("  ==> B 와 C 가 같습니다. 메시지만으로는 구분되지 않으니,")
        print("      아래 결과는 참고용이며 개발사 확인이 가장 확실합니다.")

    print()
    print("=" * 74)
    print(f"D) 후보 {len(targets)}건 — 빈 파라미터로 응답 형태만 본다")
    print("=" * 74)
    like_exists = []
    for i, ws in enumerate(targets, 1):
        st, msg = raw_call(client, ws, {})
        mark = ""
        if mb != mc and msg == mb:
            mark = "  <<< '있는 화면' 과 동일한 응답"
            like_exists.append(ws)
        print(f"  [{i:2}/{len(targets)}] {ws:24} HTTP {st}  {msg[:110]}{mark}")
        time.sleep(0.4)

    print()
    print("=" * 74)
    if like_exists:
        print(f"결과: '존재하는 화면' 과 같은 응답을 보인 후보 {len(like_exists)}건")
        for ws in like_exists:
            print(f"  - {ws}")
        print()
        print("다음: 이 ID 를 알려주시면 파라미터를 맞춰 실제 조회까지 진행합니다.")
    else:
        print("결과: 판별되는 후보 없음 — 추측으로 더 찍지 않습니다.")
        print()
        print("가장 확실한 다음 수단 (개발사에 한 줄):")
        print('  "생산 > 생산관리 > 재연마A/S 현황 화면의 workSet_CD 와')
        print('   조회 파라미터 이름을 알려주실 수 있을까요?')
        print('   기존 재연마수주 등록(sdb100_jae_g10)처럼 FillDataSetEx 로')
        print('   조회하려고 합니다."')
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
