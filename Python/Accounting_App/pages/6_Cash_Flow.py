# pages/6_Cash_Flow.py
"""
Cash Flow Statement — ငွေသား စီးဆင်းမှု ရှင်းတမ်း
Indirect Method — Auto-calc from BS + P&L
"""

import streamlit as st
import json
from datetime import date

from core import db
from core.utils import (
    format_number, format_date_mm, info_box, parse_number
)
from core.pdf_generator import generate_pdf
from core.translations import t

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Cash Flow Statement",
    page_icon="💵",
    layout="wide",
)

# ============================================================
# AUTH + CLIENT CHECK
# ============================================================

if not st.session_state.get("authentication_status"):
    st.warning("⚠️ ကျေးဇူးပြု၍ အရင် ဝင်ရောက်ပါ" if st.session_state.get("language", "my") == "my" else "⚠️ Please login first")
    st.switch_page("app.py")
    st.stop()

client_id = st.session_state.get("selected_client_id")
if not client_id:
    st.warning("⚠️ ဖောက်သည် မရွေးရသေးပါ" if st.session_state.get("language", "my") == "my" else "⚠️ No client selected")
    if st.button("← ဖောက်သည် စာရင်းသို့ ပြန်" if st.session_state.get("language", "my") == "my" else "← Back to Clients"):
        st.switch_page("pages/1_Clients.py")
    st.stop()

try:
    client = db.get_client(client_id)
except Exception as e:
    st.error(f"❌ Database error: {e}")
    st.stop()

if not client:
    st.error("❌ ဖောက်သည် မတွေ့ပါ" if st.session_state.get("language", "my") == "my" else "❌ Client not found")
    st.stop()

# ============================================================
# LOAD EXISTING CASH FLOW
# ============================================================

existing = None
saved_data = {}
saved_period = ""

try:
    existing = db.get_statement(client_id, "cash_flow")
    if existing and existing.get("data"):
        saved_data = json.loads(existing["data"])
        saved_period = existing.get("period_end", "")
except Exception:
    existing = None
    saved_data = {}
    saved_period = ""

# ============================================================
# AUTO-PULL: Trading & P&L (Net Profit, Depreciation)
# ============================================================

auto_net_profit = 0.0
auto_depreciation = 0.0
tpl_data = {}

try:
    tpl_existing = db.get_statement(client_id, "trading_pl")
    if tpl_existing and tpl_existing.get("data"):
        tpl_data = json.loads(tpl_existing["data"])
        auto_net_profit = float(tpl_data.get("_net_profit", 0.0))
        auto_depreciation = float(tpl_data.get("_depreciation", 0.0))
except Exception:
    pass

# ============================================================
# AUTO-PULL: Balance Sheet (Working Capital, Fixed Assets, Loans, Drawing)
# ============================================================

auto_bs = {}
try:
    bs_existing = db.get_statement(client_id, "balance_sheet")
    if bs_existing and bs_existing.get("data"):
        auto_bs = json.loads(bs_existing["data"])
except Exception:
    auto_bs = {}

# ============================================================
# SESSION STATE
# ============================================================

if "cf_data" not in st.session_state:
    st.session_state.cf_data = dict(saved_data)

if "cf_period" not in st.session_state:
    st.session_state.cf_period = saved_period or str(date.today())

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; padding: 0.5rem 0;">
            <h2 style="color: #1f4788; font-size: 1.3rem; margin: 0;">
                📊 {t('app_title')}
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    if st.button(t('home'), use_container_width=True):
        st.switch_page("app.py")
    if st.button(t('clients'), use_container_width=True):
        st.switch_page("pages/1_Clients.py")
    if st.button(t('detail'), use_container_width=True):
        st.switch_page("pages/2_Client_Detail.py")

    st.divider()

    st.markdown(
        f"""
        <div style="
            background-color: #e3f2fd;
            padding: 0.8rem;
            border-radius: 8px;
            border-left: 4px solid #1565c0;
        ">
            <p style="margin: 0; font-size: 0.85rem; color: #666;">{'ဖောက်သည်' if st.session_state.get('language', 'my') == 'my' else 'Client'}</p>
            <p style="margin: 0.2rem 0 0 0; font-weight: bold; color: #1565c0;">
                👤 {client['name']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    ">
        <h1 style="margin: 0; font-size: 1.8rem;">
            💵 {t('pdf_cashflow')}
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem; opacity: 0.95;">
            Cash Flow Statement — {client['name']}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# PERIOD
# ============================================================

col1, col2 = st.columns([1, 3])
with col1:
    try:
        initial_date = date.fromisoformat(st.session_state.cf_period)
    except Exception:
        initial_date = date.today()

    period_end = st.date_input(
        f"📅 {t('period_end')}",
        value=initial_date,
        key="cf_period_input",
    )
    st.session_state.cf_period = str(period_end)

# ============================================================
# HELPER — WORKING CAPITAL CHANGE
# ============================================================

def wc_change(key: str, current: float, previous: float, 
              is_asset: bool = True) -> float:
    change = current - previous
    if is_asset:
        return -change   # Asset increase → cash out
    else:
        return change    # Liability increase → cash in

# ============================================================
# SESSION STATE — DEFAULTS
# ============================================================

cf = st.session_state.cf_data

defaults = {
    "opening_cash": 0.0,
    "opening_inventories": 0.0,
    "opening_receivable": 0.0,
    "opening_payable": 0.0,
    "opening_fixed_assets": 0.0,
    "opening_loan": 0.0,
    "net_profit": auto_net_profit,
    "depreciation": auto_depreciation,
    "amortization": 0.0,
    "retain_earning_change": 0.0,
    "investing_purchase_fa": 0.0,
    "investing_intangible": 0.0,
    "financing_loan_increase": 0.0,
    "financing_drawing": 0.0,
}

for k, v in defaults.items():
    if k not in cf:
        cf[k] = v

# ============================================================
# 3 COLUMNS LAYOUT
# ============================================================

col1, col2, col3 = st.columns(3)

# ============================================================
# COLUMN 1 — OPERATING ACTIVITIES
# ============================================================

with col1:
    st.markdown(
        f"""
        <h3 style="color: #1565c0; font-size: 1.1rem; 
                   border-bottom: 2px solid #4facfe; padding-bottom: 0.3rem;">
            {'က။ လုပ်ငန်း လည်ပတ်မှု လုပ်ဆောင်ချက်များမှ ငွေသား' if st.session_state.get('language', 'my') == 'my' else 'A. OPERATING ACTIVITIES'}
        </h3>
        """,
        unsafe_allow_html=True,
    )

    net_profit = st.number_input(
        "အခွန်မဆိုင်မီ အသားတင် အမြတ်/အရှုံး" if st.session_state.get("language") == "my" else "Net Profit/Loss before Taxation",
        value=float(cf.get("net_profit", auto_net_profit)),
        min_value=-999999999999.0,
        step=1000.0,
        format="%.2f",
        key="cf_net_profit",
        help="Trading & P&L မှ auto" if st.session_state.get("language") == "my" else "Auto from Trading & P&L",
    )
    cf["net_profit"] = net_profit

    retain_change = st.number_input(
        "စုဆောင်းအမြတ် တိုးလာမှု" if st.session_state.get("language") == "my" else "Increase in Retain Earning",
        value=float(cf.get("retain_earning_change", 0.0)),
        min_value=-999999999999.0,
        step=1000.0,
        format="%.2f",
        key="cf_retain_change",
    )
    cf["retain_earning_change"] = retain_change

    st.markdown(
        f'<p style="color: #666; font-size: 0.9rem; margin: 0.5rem 0;">{"ချိန်ညှိမှုများ (Adjustment):" if st.session_state.get("language") == "my" else "Adjustment for:"}</p>',
        unsafe_allow_html=True,
    )

    amortization = st.number_input(
        "တန်ဖိုးကျဆင်းမှု ဖြန့်ခွဲ (Amortization)" if st.session_state.get("language") == "my" else "Amortization of Deferred Expenditure",
        value=float(cf.get("amortization", 0.0)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_amortization",
    )
    cf["amortization"] = amortization

    depreciation = st.number_input(
        "တန်ဖိုးကျဆင်းမှု (Depreciation)" if st.session_state.get("language") == "my" else "Depreciation",
        value=float(cf.get("depreciation", auto_depreciation)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_depreciation",
        help="Trading & P&L မှ auto" if st.session_state.get("language") == "my" else "Auto from Trading & P&L",
    )
    cf["depreciation"] = depreciation

    op_before_wc = net_profit + retain_change + amortization + depreciation
    st.markdown(
        f"""
        <div style="background-color: #e3f2fd; padding: 0.6rem; 
                    border-radius: 6px; margin: 0.5rem 0;">
            <span style="color: #1565c0; font-weight: bold; font-size: 0.85rem;">
                {'လုပ်ငန်းလည်ပတ်မှု အမြတ် (WC မဆိုင်မီ)' if st.session_state.get('language', 'my') == 'my' else 'Operation Profit before WC'}:
            </span>
            <span style="float: right; font-weight: bold; color: #1565c0;">
                {format_number(op_before_wc)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# COLUMN 2 — WORKING CAPITAL CHANGES
# ============================================================

with col2:
    st.markdown(
        f"""
        <h3 style="color: #1976d2; font-size: 1.1rem; 
                   border-bottom: 2px solid #4facfe; padding-bottom: 0.3rem;">
            {'လုပ်ငန်း အရင်းအနှီး ပြောင်းလဲမှုများ' if st.session_state.get('language', 'my') == 'my' else 'Working Capital Changes'}
        </h3>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("language") == "my":
        st.caption("➡️ Asset တိုးရင် (−)၊ လျော့ရင် (+)")
        st.caption("➡️ Liability တိုးရင် (+)၊ လျော့ရင် (−)")
    else:
        st.caption("➡️ Asset increase (−), decrease (+)")
        st.caption("➡️ Liability increase (+), decrease (−)")

    st.markdown("<br>", unsafe_allow_html=True)

    opening_inv = st.number_input(
        "အဖွင့် Inventories" if st.session_state.get("language") == "my" else "Opening Inventories",
        value=float(cf.get("opening_inventories", 0.0)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_opening_inv",
    )
    cf["opening_inventories"] = opening_inv

    opening_rec = st.number_input(
        "အဖွင့် A/C Receivable" if st.session_state.get("language") == "my" else "Opening A/C Receivable",
        value=float(cf.get("opening_receivable", 0.0)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_opening_rec",
    )
    cf["opening_receivable"] = opening_rec

    opening_pay = st.number_input(
        "အဖွင့် Creditors/A/P" if st.session_state.get("language") == "my" else "Opening Creditors/A/P",
        value=float(cf.get("opening_payable", 0.0)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_opening_pay",
    )
    cf["opening_payable"] = opening_pay

    closing_inv = float(auto_bs.get("ca_inventories", 0.0))
    closing_rec = float(auto_bs.get("ca_receivable", 0.0))
    closing_pay = float(auto_bs.get("liab_payable", 0.0))

    st.markdown(
        f"""
        <div style="background-color: #f5f5f5; padding: 0.6rem; 
                    border-radius: 6px; margin-top: 0.8rem; font-size: 0.85rem;">
            <b>{'အပိတ် (BS မှ auto):' if st.session_state.get('language', 'my') == 'my' else 'Closing (Auto from BS):'}</b><br>
            {'Inventories' if st.session_state.get('language') == 'en' else 'Inventories'}: {format_number(closing_inv)}<br>
            {'A/C Receivable' if st.session_state.get('language') == 'en' else 'A/C Receivable'}: {format_number(closing_rec)}<br>
            {'Creditors/A/P' if st.session_state.get('language') == 'en' else 'Creditors/A/P'}: {format_number(closing_pay)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    inv_change = wc_change("inv", closing_inv, opening_inv, is_asset=True)
    rec_change = wc_change("rec", closing_rec, opening_rec, is_asset=True)
    pay_change = wc_change("pay", closing_pay, opening_pay, is_asset=False)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="background-color: #fff3e0; padding: 0.8rem; 
                    border-radius: 8px; font-size: 0.9rem;">
            <table style="width: 100%;">
                <tr>
                    <td>{'Inventories ပြောင်းလဲမှု' if st.session_state.get('language', 'my') == 'my' else 'Inventories change'}</td>
                    <td style="text-align: right; font-weight: bold; 
                               color: {'#c62828' if inv_change < 0 else '#2e7d32'};">
                        {format_number(inv_change)}
                    </td>
                </tr>
                <tr>
                    <td>{'A/C Receivable ပြောင်းလဲမှု' if st.session_state.get('language', 'my') == 'my' else 'A/C Receivable change'}</td>
                    <td style="text-align: right; font-weight: bold;
                               color: {'#c62828' if rec_change < 0 else '#2e7d32'};">
                        {format_number(rec_change)}
                    </td>
                </tr>
                <tr>
                    <td>{'Creditors/A/P ပြောင်းလဲမှု' if st.session_state.get('language', 'my') == 'my' else 'Creditors/A/P change'}</td>
                    <td style="text-align: right; font-weight: bold;
                               color: {'#c62828' if pay_change < 0 else '#2e7d32'};">
                        {format_number(pay_change)}
                    </td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_wc_change = inv_change + rec_change + pay_change

    st.markdown(
        f"""
        <div style="background-color: #fce4ec; padding: 0.6rem; 
                    border-radius: 6px; margin-top: 0.5rem;">
            <span style="color: #c2185b; font-weight: bold; font-size: 0.85rem;">
                {'လုပ်ငန်းလည်ပတ်မှုမှ ငွေသား (Net):' if st.session_state.get('language', 'my') == 'my' else 'Cash used in / generated from operation:'}
            </span>
            <span style="float: right; font-weight: bold; color: #c2185b;">
                {format_number(total_wc_change)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# COLUMN 3 — INVESTING + FINANCING + SUMMARY
# ============================================================

with col3:
    net_operating = op_before_wc + total_wc_change

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 1.2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1rem;
        ">
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.95;">
                💰 {'လုပ်ငန်းလည်ပတ်မှုမှ ရရှိသော ငွေသား (Net)' if st.session_state.get('language', 'my') == 'my' else 'Net Cash from Operating'}
            </p>
            <h2 style="margin: 0.4rem 0 0 0; font-size: 1.6rem;">
                {format_number(net_operating)}
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <h4 style="color: #1976d2; font-size: 1rem; 
                   border-bottom: 1px solid #4facfe; padding-bottom: 0.2rem;">
            {'ခ။ ရင်းနှီးမြှုပ်နှံမှု လုပ်ဆောင်ချက်များမှ ငွေသား' if st.session_state.get('language', 'my') == 'my' else 'INVESTING ACTIVITIES'}
        </h4>
        """,
        unsafe_allow_html=True,
    )

    invest_fa = st.number_input(
        "ပုံသေပိုင်ဆိုင်မှု ဝယ်ယူမှု" if st.session_state.get("language") == "my" else "Purchase of Fixed Assets",
        value=float(cf.get("investing_purchase_fa", 0.0)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_invest_fa",
    )
    cf["investing_purchase_fa"] = invest_fa

    invest_intangible = st.number_input(
        "မမြင်နိုင်သော ပိုင်ဆိုင်မှု တိုးလာမှု" if st.session_state.get("language") == "my" else "Increase in Intangible Assets",
        value=float(cf.get("investing_intangible", 0.0)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_invest_intangible",
    )
    cf["investing_intangible"] = invest_intangible

    net_investing = -(invest_fa + invest_intangible)

    st.markdown(
        f"""
        <div style="background-color: #e3f2fd; padding: 0.5rem; 
                    border-radius: 6px; font-size: 0.85rem;">
            <span style="color: #1565c0; font-weight: bold;">
                {'ရင်းနှီးမြှုပ်နှံမှုမှ ငွေသား (Net):' if st.session_state.get('language', 'my') == 'my' else 'Net Cash from Investing:'}
            </span>
            <span style="float: right; font-weight: bold; color: #1565c0;">
                {format_number(net_investing)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <h4 style="color: #1976d2; font-size: 1rem; 
                   border-bottom: 1px solid #4facfe; padding-bottom: 0.2rem;">
            {'ဂ။ ငွေကြေးရှာဖွေမှု လုပ်ဆောင်ချက်များမှ ငွေသား' if st.session_state.get('language', 'my') == 'my' else 'FINANCING ACTIVITIES'}
        </h4>
        """,
        unsafe_allow_html=True,
    )

    auto_drawing = float(auto_bs.get("eq_drawing", 0.0))
    auto_loan = float(auto_bs.get("liab_bank_loan", 0.0))

    finance_loan = st.number_input(
        "ချေးငွေ တိုးလာမှု" if st.session_state.get("language") == "my" else "Increase in Loan",
        value=float(cf.get("financing_loan_increase", auto_loan)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_finance_loan",
    )
    cf["financing_loan_increase"] = finance_loan

    finance_drawing = st.number_input(
        "ပိုင်ရှင် ထုတ်ယူမှု (Drawing)" if st.session_state.get("language") == "my" else "Drawing",
        value=float(cf.get("financing_drawing", auto_drawing)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_finance_drawing",
        help="Balance Sheet မှ auto" if st.session_state.get("language") == "my" else "Auto from Balance Sheet",
    )
    cf["financing_drawing"] = finance_drawing

    net_financing = finance_loan - finance_drawing

    st.markdown(
        f"""
        <div style="background-color: #e3f2fd; padding: 0.5rem; 
                    border-radius: 6px; font-size: 0.85rem;">
            <span style="color: #1565c0; font-weight: bold;">
                {'ငွေကြေးရှာဖွေမှုမှ ငွေသား (Net):' if st.session_state.get('language', 'my') == 'my' else 'Net Cash from Financing:'}
            </span>
            <span style="float: right; font-weight: bold; color: #1565c0;">
                {format_number(net_financing)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    net_change = net_operating + net_investing + net_financing

    opening_cash = st.number_input(
        "ကာလအစ ငွေသား" if st.session_state.get("language") == "my" else "Cash and Equivalents at beginning",
        value=float(cf.get("opening_cash", 0.0)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="cf_opening_cash",
    )
    cf["opening_cash"] = opening_cash

    closing_cash_calc = opening_cash + net_change
    auto_closing_cash = float(auto_bs.get("ca_cash", 0.0))

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 1rem;
            border-radius: 12px;
            color: white;
            margin-top: 0.5rem;
        ">
            <p style="margin: 0; font-size: 0.85rem; opacity: 0.95;">
                {'ငွေသား ပြောင်းလဲမှု (Net)' if st.session_state.get('language', 'my') == 'my' else 'Net Change in Cash'}
            </p>
            <h3 style="margin: 0.3rem 0 0 0; font-size: 1.3rem;">
                {format_number(net_change)}
            </h3>
            <hr style="margin: 0.5rem 0; border-color: rgba(255,255,255,0.3);">
            <p style="margin: 0; font-size: 0.8rem; opacity: 0.9;">
                + {'ကာလအစ ငွေသား' if st.session_state.get('language', 'my') == 'my' else 'Cash at Beginning'}: {format_number(opening_cash)}
            </p>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.9rem; font-weight: bold;">
                = {'ကာလအဆုံး ငွေသား' if st.session_state.get('language', 'my') == 'my' else 'Cash at End'}: {format_number(closing_cash_calc)}
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem; opacity: 0.85;">
                {'BS မှ Closing Cash' if st.session_state.get('language', 'my') == 'my' else 'Closing Cash from BS'}: {format_number(auto_closing_cash)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# ACTION BUTTONS
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(t('save'), use_container_width=True, type="primary"):
        try:
            cf["_net_operating"] = net_operating
            cf["_net_investing"] = net_investing
            cf["_net_financing"] = net_financing
            cf["_net_change"] = net_change
            cf["_closing_cash"] = closing_cash_calc

            data_json = json.dumps(cf, ensure_ascii=False)
            db.save_statement(
                client_id=client_id,
                statement_type="cash_flow",
                period_end=st.session_state.cf_period,
                data_json=data_json,
            )
            st.success("✓ သိမ်းပြီးပါပြီ" if st.session_state.get("language") == "my" else "✓ Saved successfully")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Error: {e}")

with col2:
    if st.button("📄 PDF", use_container_width=True):
        try:
            pdf_bytes = generate_pdf(
                statement_type="cash_flow",
                client_name=client["name"],
                data=cf,
                period_end=st.session_state.cf_period,
                lang=st.session_state.language, # ⭐ Lang ထည့်ပြီး
            )
            st.download_button(
                "⬇️ PDF Download",
                data=pdf_bytes,
                file_name=f"{client['name']}_CashFlow_{st.session_state.cf_period}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"❌ PDF Error: {e}")

with col3:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.cf_data = {}
        st.rerun()

with col4:
    if st.button(t('detail'), use_container_width=True):
        st.switch_page("pages/2_Client_Detail.py")

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption(f"📅 {t('period_end')}: {format_date_mm(st.session_state.cf_period)}")
st.caption(f"👤 {t('clients')}: {client['name']}")
if existing and existing.get("updated_at"):
    st.caption(f"🔄 {t('updated')}: {format_date_mm(existing.get('updated_at', ''))}")