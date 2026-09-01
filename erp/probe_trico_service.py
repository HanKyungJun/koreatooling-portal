"""
Trico WCF 탐침 v4
─────────────────
확정: namespace=http://tempuri.org/  interface=ITricoService
목표 1) 전체 메서드명 확인
목표 2) FillDataSet 파라미터 구조 확인
"""

import requests, re

SVC_URL = "http://erp.toolkorea.co.kr:8101/TricoService/TricoService.svc"
NS      = "http://tempuri.org/"
IFACE   = "ITricoService"

HEADERS_BASE = {
    "Content-Type": "text/xml; charset=utf-8",
    "Accept":       "text/xml",
}


def action(method):
    return f'"{NS}{IFACE}/{method}"'


def envelope(method, body=""):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="{NS}">
  <soap:Body><tns:{method}>{body}</tns:{method}></soap:Body>
</soap:Envelope>"""


def call(method, body=""):
    r = requests.post(SVC_URL,
                      data=envelope(method, body).encode("utf-8"),
                      headers={**HEADERS_BASE, "SOAPAction": action(method)},
                      timeout=8)
    xml = r.text
    fc  = re.search(r'<[^>]*faultcode[^>]*>(.*?)</', xml, re.S)
    fs  = re.search(r'<[^>]*faultstring[^>]*>(.*?)</', xml, re.S)
    det = re.search(r'<[^>]*(?:ExceptionMessage|Message)[^>]*>(.*?)</', xml, re.S)
    return {
        "status":      r.status_code,
        "faultcode":   (fc.group(1) if fc else "").strip(),
        "faultstring": (fs.group(1) if fs else "").strip(),
        "detail":      (det.group(1) if det else "").strip(),
    }


# ════════════════════════════════════════════════════════════════
# 목표 1: 메서드명 전체 탐색
# ════════════════════════════════════════════════════════════════
METHODS = [
    # 로그인
    "Login", "UserLogin", "GetLogin", "SetLogin", "CheckLogin",
    "DoLogin", "LoginCheck", "Authenticate", "Auth", "GetLoginInfo",
    "ValidateLogin", "GetUserInfo",
    # 데이터 조회
    "FillDataSet", "FillDataTable",
    "GetDataSet", "GetDataTable",
    "ExecuteQuery", "Execute", "RunQuery",
    "SelectData", "GetData", "QueryData",
    "RunSP", "ExecuteSP", "ExecuteStoredProc",
    # 세션
    "CreateSession", "GetSession", "SetSession",
    "Ping", "Test", "Echo",
]

print("[ 목표 1: 메서드명 탐색 ]")
print(f"{'METHOD':30s}  STATUS  RESULT")
print("─" * 80)
hits = []
for m in METHODS:
    res = call(m)
    if "ActionNotSupported" in res["faultcode"] or "ContractFilter" in res["faultstring"]:
        marker = "❌"
    else:
        marker = "✅ HIT"
        hits.append((m, res))
    print(f"{m:30s}  [{res['status']}]   {marker}  {res['faultstring'][:60]}")

print(f"\n확인된 메서드: {[m for m,_ in hits]}\n")


# ════════════════════════════════════════════════════════════════
# 목표 2: FillDataSet 파라미터 구조 탐색
# ════════════════════════════════════════════════════════════════
print("[ 목표 2: FillDataSet 파라미터 탐색 ]")

param_candidates = [
    # 파라미터 이름 조합 시도
    ("<tns:catalog>TRICO</tns:catalog><tns:cmdText>SELECT 1</tns:cmdText>",
     "catalog+cmdText"),
    ("<tns:dbName>TRICO</tns:dbName><tns:query>SELECT 1</tns:query>",
     "dbName+query"),
    ("<tns:catalog>TRICO</tns:catalog><tns:cmdText>SELECT 1</tns:cmdText><tns:Gzip_YN>false</tns:Gzip_YN>",
     "catalog+cmdText+Gzip_YN"),
    ("<tns:strCatalog>TRICO</tns:strCatalog><tns:strCmdText>SELECT 1</tns:strCmdText>",
     "strCatalog+strCmdText"),
    ("<tns:userID>100007</tns:userID><tns:catalog>TRICO</tns:catalog><tns:cmdText>SELECT 1</tns:cmdText>",
     "userID+catalog+cmdText"),
]

for body, label in param_candidates:
    res = call("FillDataSet", body)
    print(f"\n  파라미터: {label}")
    print(f"  faultcode  : {res['faultcode'][:80]}")
    print(f"  faultstring: {res['faultstring'][:120]}")
    if res["detail"]:
        print(f"  detail     : {res['detail'][:150]}")

print("\n탐침 완료. 결과를 Cowork에 붙여넣어 주세요.")
