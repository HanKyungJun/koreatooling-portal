"""
Trico ERP WCF 클라이언트  v2.0
────────────────────────────────
확정된 화면 3개:
  - 생산실적 등록  (PPC120_g00)
  - 재연마수주 등록 (sdb100_jae_g10)
  - 재연마 출하등록 (lem120_jae_g00)

사용 예:
    client = TricoClient()
    df = client.생산실적(fr_dt="2026-06-01", to_dt="2026-06-11")
    df = client.수주(fr_dt="2026-05-01")
    df = client.출하(fr_dt="2026-06-01")
"""

import gzip, re, requests
from datetime import date
from xml.etree import ElementTree as ET
import pandas as pd

# ── 서버 ───────────────────────────────────────────────────────────────────
SVC_URL  = "http://erp.toolkorea.co.kr:8101/TricoService/TricoService.svc"
NS_TRICO = "http://schemas.datacontract.org/2004/07/Trico.Service"
NS_SER   = "http://schemas.microsoft.com/2003/10/Serialization/Arrays"
NS_XSD   = "http://www.w3.org/2001/XMLSchema"
NS_SYS   = "http://schemas.datacontract.org/2004/07/System"

# ── 세션 컨텍스트 ──────────────────────────────────────────────────────────
DEFAULT_MACRO = {
    "<$system_cd>": "SMES",
    "<$lan_no>":    "1",
    "<$reg_id>":    "7",
    "<$user_id>":   "100007",
    "<$user_nm>":   "한경준",
    "<$user_type>": "SC700100",
    "<$emp_no>":    "",
    "<$co_cd>":     "01",
    "<$sys_cd>":    "",
    "<$div_cd>":    "",
    "<$bs_cd>":     "10",
    "<$fac_cd>":    "01",
    "<$wc_cd>":     "10",
    "<$wh_cd>":     "10",
    "<$dept_cd>":   "8100",
    "<$dept_nm>":   "생산팀",
    "<$cust_cd>":   "",
    "<$cust_nm>":   "",
}

# ── 단가/금액 차단 키워드 ────────────────────────────────────────────────────
PRICE_KEYWORDS = [
    "단가","정가","금액","가격","원가","공급가","부가세","세액",
    "할인","매출액","매입액","공급액","판매가","구매가","견적가",
    "낙찰가","계약금","잔금","선급금","청구금","지급금","수수료",
    "price","cost","amount","rate","value","fee","tax","vat",
    "discount","charge","revenue","payment","invoice","amt",
]

def is_price_col(name: str) -> bool:
    return any(k in name.lower() for k in PRICE_KEYWORDS)


# ══════════════════════════════════════════════════════════════════════════════
class TricoClient:

    def __init__(self, macro: dict = None):
        self.macro = macro or DEFAULT_MACRO
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type":    "text/xml; charset=utf-8",
            "Accept":          "text/xml",
            "Accept-Encoding": "gzip, deflate",
        })

    # ── SOAP 빌더 ─────────────────────────────────────────────────────────
    def _macro_xml(self) -> str:
        items = "".join(
            f'<b:KeyValueOfstringstring>'
            f'<b:Key>{_esc(k)}</b:Key>'
            f'<b:Value>{_esc(v)}</b:Value>'
            f'</b:KeyValueOfstringstring>'
            for k, v in self.macro.items()
        )
        return f'<a:Macro xmlns:b="{NS_SER}">{items}</a:Macro>'

    def _param_xml(self, name: str, value, size: int = 0,
                   type_: str = "NVarChar") -> str:
        if value is None:
            val_xml = f'<a:ParamaterValue i:type="b:DBNull" xmlns:b="{NS_SYS}"/>'
        else:
            val_xml = (f'<a:ParamaterValue i:type="b:string" xmlns:b="{NS_XSD}">'
                       f'{_esc(str(value))}</a:ParamaterValue>')
        return (
            f'<a:SQLArray>'
            f'<a:ParamaterDataTable i:nil="true"/>'
            f'<a:ParamaterDirection>Input</a:ParamaterDirection>'
            f'<a:ParamaterName>{_esc(name)}</a:ParamaterName>'
            f'<a:ParamaterPrecision>0</a:ParamaterPrecision>'
            f'<a:ParamaterScale>0</a:ParamaterScale>'
            f'<a:ParamaterSize>{size}</a:ParamaterSize>'
            f'{val_xml}'
            f'<a:Paramatertype>{type_}</a:Paramatertype>'
            f'<a:Paramatertypename/>'
            f'</a:SQLArray>'
        )

    def _data_con_xml(self, work_set: str, params: dict) -> str:
        macro_xml  = self._macro_xml()
        params_xml = "".join(self._param_xml(k, v) for k, v in params.items())
        return (
            f'<a:DataCon>'
            f'{macro_xml}'
            f'<a:SqlDesc i:nil="true"/>'
            f'<a:cataLog/>'
            f'<a:cmdText i:nil="true"/>'
            f'<a:cmdType>Text</a:cmdType>'
            f'<a:ex i:nil="true" xmlns:b="{NS_SYS}"/>'
            f'<a:oPm i:nil="true" xmlns:b="{NS_SER}"/>'
            f'<a:oPms i:nil="true"/>'
            f'<a:sqlArray>{params_xml}</a:sqlArray>'
            f'<a:useTransaction>false</a:useTransaction>'
            f'<a:workSet_CD>{_esc(work_set)}</a:workSet_CD>'
            f'</a:DataCon>'
        )

    def _envelope(self, *data_cons: str) -> str:
        inner = "".join(data_cons)
        return (
            f'<?xml version="1.0" encoding="utf-8"?>'
            f'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">'
            f'<s:Body>'
            f'<FillDataSetEx xmlns="http://tempuri.org/">'
            f'<dataCon xmlns:a="{NS_TRICO}"'
            f' xmlns:i="http://www.w3.org/2001/XMLSchema-instance">'
            f'{inner}'
            f'</dataCon>'
            f'</FillDataSetEx>'
            f'</s:Body>'
            f'</s:Envelope>'
        )

    # ── 요청 실행 ─────────────────────────────────────────────────────────
    def query(self, work_set: str, params: dict,
              block_price: bool = True) -> pd.DataFrame:
        dc  = self._data_con_xml(work_set, params)
        env = self._envelope(dc).encode("utf-8")

        resp = self.session.post(
            SVC_URL,
            data=env,
            headers={"SOAPAction": '"http://tempuri.org/ITricoService/FillDataSetEx"'},
            timeout=20,
        )
        resp.raise_for_status()

        raw = resp.content
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass

        xml_str = raw.decode("utf-8", errors="replace")

        if "<faultstring>" in xml_str:
            fault  = re.search(r'<[^>]*faultstring[^>]*>(.*?)</', xml_str, re.S)
            detail = re.search(r'<[^>]*ExceptionMessage[^>]*>(.*?)</', xml_str, re.S)
            raise RuntimeError(
                f"SOAP Fault: {fault.group(1) if fault else '?'}\n"
                f"Detail: {detail.group(1) if detail else ''}"
            )

        df = _parse_dataset(xml_str)

        if block_price:
            blocked = [c for c in df.columns if is_price_col(c)]
            if blocked:
                print(f"  [경고]  가격 컬럼 차단: {blocked}")
            df = df.drop(columns=blocked, errors="ignore")

        return df

    # ── 화면별 편의 메서드 ────────────────────────────────────────────────

    def 생산실적(self, fr_dt: str = None, to_dt: str = None,
                fac_cd: str = "01") -> pd.DataFrame:
        """생산실적 등록 (PPC120_g00)"""
        today = date.today().strftime("%Y-%m-%d")
        first = date.today().replace(day=1).strftime("%Y-%m-%d")
        return self.query("PPC120_g00", {
            "@to_dt":    to_dt or today,
            "@fr_dt":    fr_dt or first,
            "@fac_cd":   fac_cd,
            "@itm_cd":   None,
            "@itm_bc":   None,
            "@grp1_cd":  None,
            "@grp2_cd":  None,
            "@model_cd": None,
            "@stat_bc":  "'PP250100','PP250300'",
            "@plan_bc":  None,
            "@prc_cd":   "",
            "@wo_no":    None,
            "@pw_no":    None,
            "@so_no":    None,
            "@cust_cd":  None,
        })

    def 수주(self, fr_dt: str = None, to_dt: str = "",
             co_cd: str = "01") -> pd.DataFrame:
        """재연마수주 등록 (sdb100_jae_g10)"""
        first = date.today().replace(day=1).strftime("%Y-%m-%d")
        return self.query("sdb100_jae_g10", {
            "@to_dt":      to_dt,
            "@fr_dt":      fr_dt or first,
            "@chk_detail": "0",
            "@co_cd":      co_cd,
            "@f_so_no":    None,
            "@f_so_bs":    "'01','10'",
            "@f_cust_cd":  None,
            "@f_cust2_cd": None,
            "@f_itm_cd":   None,
            "@f_so_rid":   None,
            "@f_stat_bc":  "",
            "@f_order_nm": None,
            "@f_rmks":     None,
            "@f_cust_nm":  None,
        })

    def 출하(self, fr_dt: str = None, to_dt: str = "",
             co_cd: str = "01") -> pd.DataFrame:
        """재연마 출하등록 (lem120_jae_g00)"""
        first = date.today().replace(day=1).strftime("%Y-%m-%d")
        return self.query("lem120_jae_g00", {
            "@to_dt":      to_dt,
            "@fr_dt":      fr_dt or first,
            "@co_cd":      co_cd,
            "@f_out_bs":   None,
            "@f_de_bc":    None,
            "@f_sal_bc":   None,
            "@f_mov_no":   None,
            "@f_cust_cd":  None,
            "@f_rmks":     None,
            "@chk_detail": "0",
            "@f_itm_cd":   None,
            "@f_cust_nm":  None,
        })

    def 출하_명세(self, fr_dt: str = None, to_dt: str = "",
                 co_cd: str = "01") -> pd.DataFrame:
        """거래명세서용 출하 상세 — 단가0 플래그 포함, 금액 컬럼 제거"""
        first = date.today().replace(day=1).strftime("%Y-%m-%d")
        df = self.query("lem120_jae_g00", {
            "@to_dt":      to_dt,
            "@fr_dt":      fr_dt or first,
            "@co_cd":      co_cd,
            "@f_out_bs":   None,
            "@f_de_bc":    None,
            "@f_sal_bc":   None,
            "@f_mov_no":   None,
            "@f_cust_cd":  None,
            "@f_rmks":     None,
            "@chk_detail": "1",
            "@f_itm_cd":   None,
            "@f_cust_nm":  None,
        }, block_price=False)

        if df.empty:
            return df

        # 단가 0 여부 판별 (mov_amt=0 이고 mov_qty>0)
        def _f(v):
            try: return float(v)
            except: return 0.0
        amt  = df.get("mov_amt",  pd.Series(["0"] * len(df))).map(_f)
        qty  = df.get("mov_qty",  pd.Series(["0"] * len(df))).map(_f)
        df.insert(0, "단가0", (qty > 0) & (amt == 0.0))

        # 통화기준·원화기준 금액 컬럼 제거
        drop = ["cury_bc", "ex_rt", "vat_bc", "tran_amt", "mov_amt", "vat_amt", "tot_amt"]
        df = df.drop(columns=[c for c in drop if c in df.columns], errors="ignore")

        return df

    def 출하_영업(self, fr_dt: str = None, to_dt: str = "",
                 co_cd: str = "01") -> pd.DataFrame:
        """영업팀 출하등록 (lem120_g00)"""
        first = date.today().replace(day=1).strftime("%Y-%m-%d")
        fr = fr_dt or first
        return self.query("lem120_g00", {
            "@to_dt":       to_dt,
            "@fr_dt":       fr,
            "@co_cd":       co_cd,
            "@f_out_bs":    "'01','10'",
            "@f_de_bc":     "",
            "@f_sal_bc":    None,
            "@f_mov_no":    None,
            "@fr_dt2":      fr,
            "@to_dt2":      to_dt,
            "@f_cust_cd":   None,
            "@f_wh_cd":     "'05','10','15','20','30'",
            "@f_rmks":      None,
            "@f_so_bc":     "SD250100",
            "@f_out_rid":   None,
            "@f_reg_id":    None,
            "@chk_detail":  "0",
            "@chk_prt":     "0",
            "@chk_tran":    "0",
            "@f_itm_cd":    None,
            "@f_itm_cd2":   None,
            "@f_model_cd":  None,
            "@f_cust_nm":   None,
        })

    def 출하_영업_명세(self, fr_dt: str = None, to_dt: str = "",
                     co_cd: str = "01") -> pd.DataFrame:
        """영업팀 거래명세서용 출하 상세 — 단가0 플래그 포함, 금액 컬럼 제거"""
        first = date.today().replace(day=1).strftime("%Y-%m-%d")
        fr = fr_dt or first
        df = self.query("lem120_g00", {
            "@to_dt":       to_dt,
            "@fr_dt":       fr,
            "@co_cd":       co_cd,
            "@f_out_bs":    "'01','10'",
            "@f_de_bc":     "",
            "@f_sal_bc":    None,
            "@f_mov_no":    None,
            "@fr_dt2":      fr,
            "@to_dt2":      to_dt,
            "@f_cust_cd":   None,
            "@f_wh_cd":     "'05','10','15','20','30'",
            "@f_rmks":      None,
            "@f_so_bc":     "SD250100",
            "@f_out_rid":   None,
            "@f_reg_id":    None,
            "@chk_detail":  "1",
            "@chk_prt":     "0",
            "@chk_tran":    "0",
            "@f_itm_cd":    None,
            "@f_itm_cd2":   None,
            "@f_model_cd":  None,
            "@f_cust_nm":   None,
        }, block_price=False)

        if df.empty:
            return df

        def _f(v):
            try: return float(v)
            except: return 0.0
        amt = df.get("mov_amt", pd.Series(["0"] * len(df))).map(_f)
        qty = df.get("mov_qty", pd.Series(["0"] * len(df))).map(_f)
        df.insert(0, "단가0", (qty > 0) & (amt == 0.0))

        drop = ["cury_bc", "ex_rt", "vat_bc", "tran_amt", "mov_amt", "vat_amt", "tot_amt"]
        df = df.drop(columns=[c for c in drop if c in df.columns], errors="ignore")

        return df


# ══════════════════════════════════════════════════════════════════════════════
def _esc(s: str) -> str:
    return (s.replace("&","&amp;").replace("<","&lt;")
             .replace(">","&gt;").replace('"',"&quot;"))


def _parse_dataset(xml_str: str) -> pd.DataFrame:
    b64 = re.search(r'<[^>]*Result[^>]*>([A-Za-z0-9+/=\s]+)</[^>]*Result>', xml_str)
    if b64:
        import base64
        data = base64.b64decode(b64.group(1).strip())
        try:
            data = gzip.decompress(data)
        except Exception:
            pass
        xml_str = data.decode("utf-8", errors="replace")

    root     = ET.fromstring(xml_str)
    ns_diffgr = "urn:schemas-microsoft-com:xml-diffgram-v1"
    diffgram  = root.find(f'.//{{{ns_diffgr}}}diffgram') or root

    rows = []
    for child in diffgram:
        if child.tag.split("}")[-1].lower() == "schema":
            continue
        for row_el in child:
            row = {el.tag.split("}")[-1]: el.text for el in row_el}
            if row:
                rows.append(row)

    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    client = TricoClient()
    screens = {
        "1": ("생산실적 등록",  client.생산실적),
        "2": ("재연마수주 등록", client.수주),
        "3": ("재연마 출하등록", client.출하),
    }

    print("=== Trico ERP 조회 ===")
    for k, (name, _) in screens.items():
        print(f"  {k}. {name}")
    print("  0. 전체 조회")

    choice = input("\n선택: ").strip()
    targets = list(screens.values()) if choice == "0" else \
              [screens[choice]] if choice in screens else []

    if not targets:
        print("잘못된 선택")
    else:
        for name, fn in targets:
            print(f"\n[{name}] 조회 중...")
            try:
                df = fn()
                print(f"  ✅ {len(df)}행 × {len(df.columns)}열")
                print(df.head(3).to_string())
            except Exception as e:
                print(f"  ❌ {e}")
