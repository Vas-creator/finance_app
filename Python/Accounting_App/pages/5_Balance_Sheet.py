# pages/5_Balance_Sheet.py
"""
Balance Sheet — ငွေစာရင်း လက်ကျန်စာရင်း
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

st.set_page_config(
    page_title="Balance Sheet",
    page_icon="📊",
    layout="wide",
)

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

existing = None
saved_data = {}
saved_date = ""

try:
    existing = db.get_statement(client_id, "balance_sheet")
    if existing and existing.get("data"):
        saved_data = json.loads(existing["data"])
        saved_date = existing.get("as_at_date", "") or existing.get("period_end", "")
except Exception:
    existing = None
    saved_data = {}
    saved_date = ""

auto_net_profit = 0.0
auto_depreciation = 0.0

try:
    tpl_existing = db.get_statement(client_id, "trading_pl")
    if tpl_existing and tpl_existing.get("data"):
        tpl_data = json.loads(tpl_existing["data"])
        auto_net_profit = float(tpl_data.get("_net_profit", 0.0))
        auto_depreciation = float(tpl_data.get("_depreciation", 0.0))
except Exception:
    pass

if "bs_data" not in st.session_state:
    st.session_state.bs_data = dict(saved_data)

if "bs_date" not in st.session_state:
    st.session_state.bs_date = saved_date or str(date.today())

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
        <div style="background-color: #e3f2fd; padding: 0.8rem; border-radius: 8px; border-left: 4px solid #1565c0;">
            <p style="margin: 0; font-size: 0.85rem; color: #666;">{'ဖောက်သည်' if st.session_state.get('language', 'my') == 'my' else 'Client'}</p>
            <p style="margin: 0.2rem 0 0 0; font-weight: bold; color: #1565c0;">
                👤 {client['name']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 1.2rem 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
        <h1 style="margin: 0; font-size: 1.8rem;">📊 {t('pdf_balance')}</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem; opacity: 0.95;">
            Balance Sheet — {client['name']}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 3])
with col1:
    try:
        initial_date = date.fromisoformat(st.session_state.bs_date)
    except Exception:
        initial_date = date.today()

    as_at_date = st.date_input(
        f"📅 {t('as_at_date')}",
        value=initial_date,
        key="bs_date_input",
    )
    st.session_state.bs_date = str(as_at_date)

def num_input(label: str, key: str, is_deduction: bool = False, default: float = None, help_text: str = "") -> float:
    if default is None:
        value = st.session_state.bs_data.get(key, 0.0)
    else:
        value = st.session_state.bs_data.get(key, default)

    prefix = "➖ " if is_deduction else ""
    result = st.number_input(
        f"{prefix}{label}",
        value=float(value) if value else 0.0,
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key=f"bs_{key}",
        help=help_text,
    )
    st.session_state.bs_data[key] = result
    return result

def subtotal_box(label: str, value: float, color: str = "#1976d2"):
    st.markdown(
        f"""
        <div style="background-color: {color}20; border-left: 3px solid {color}; padding: 0.6rem 0.8rem; border-radius: 6px; margin: 0.5rem 0;">
            <span style="color: {color}; font-weight: bold;">{label}:</span>
            <span style="float: right; font-weight: bold; color: {color};">
                {format_number(value)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'<h3 style="color: #2e7d32; font-size: 1.15rem; border-bottom: 2px solid #43e97b; padding-bottom: 0.3rem;">{"၁။ ပုံသေ ပိုင်ဆိုင်မှုများ" if st.session_state.get("language") == "my" else "1. Fixed Assets"}</h3>', unsafe_allow_html=True)
    nca_land = num_input("မြေ (Land)" if st.session_state.get("language") == "my" else "Land", "nca_land")
    nca_building = num_input("အဆောက်အအုံ (Building)" if st.session_state.get("language") == "my" else "Building", "nca_building")
    nca_machine = num_input("စက်ပစ္စည်း (Machine)" if st.session_state.get("language") == "my" else "Machine", "nca_machine")
    nca_furniture = num_input("ပရိဘောဂ (Furniture)" if st.session_state.get("language") == "my" else "Furniture", "nca_furniture")
    nca_vehicle = num_input("ယာဉ် (Vehicle)" if st.session_state.get("language") == "my" else "Vehicle", "nca_vehicle")

    total_nca = nca_land + nca_building + nca_machine + nca_furniture + nca_vehicle
    subtotal_box("ပုံသေ ပိုင်ဆိုင်မှု စုစုပေါင်း" if st.session_state.get("language") == "my" else "Total Fixed Assets", total_nca, "#2e7d32")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f'<h3 style="color: #2e7d32; font-size: 1.15rem; border-bottom: 2px solid #43e97b; padding-bottom: 0.3rem;">{"၂။ လက်ရှိ ပိုင်ဆိုင်မှုများ" if st.session_state.get("language") == "my" else "2. Current Assets"}</h3>', unsafe_allow_html=True)
    ca_inventories = num_input("ကုန်ပစ္စည်းလက်ကျန် (Inventories)" if st.session_state.get("language") == "my" else "Inventories", "ca_inventories")
    ca_receivable = num_input("ရရန်ကျန်ငွေ (A/C Receivable)" if st.session_state.get("language") == "my" else "A/C Receivable", "ca_receivable")
    ca_advance = num_input("ကြိုတင်ပေးငွေ (Advance Payments)" if st.session_state.get("language") == "my" else "Advance Payments", "ca_advance")
    ca_cash = num_input("လက်ထဲ/ဘဏ် ငွေသား (Cash)" if st.session_state.get("language") == "my" else "Cash", "ca_cash")

    total_ca = ca_inventories + ca_receivable + ca_advance + ca_cash
    subtotal_box("လက်ရှိ ပိုင်ဆိုင်မှု စုစုပေါင်း" if st.session_state.get("language") == "my" else "Total Current Assets", total_ca, "#2e7d32")
    st.markdown("<br>", unsafe_allow_html=True)

    total_assets = total_nca + total_ca
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 1.2rem; border-radius: 12px; color: white; margin-top: 1rem;">
            <p style="margin: 0; font-size: 1rem; opacity: 0.95;">📊 {'ပိုင်ဆိုင်မှု စုစုပေါင်း' if st.session_state.get('language') == 'my' else 'Total Assets'}</p>
            <h1 style="margin: 0.4rem 0 0 0; font-size: 1.8rem;">{format_number(total_assets)}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(f'<h3 style="color: #c2185b; font-size: 1.15rem; border-bottom: 2px solid #f093fb; padding-bottom: 0.3rem;">{"၃။ အရင်း ငွေ (Equity)" if st.session_state.get("language") == "my" else "3. Equity"}</h3>', unsafe_allow_html=True)
    eq_capital = num_input("အရင်း (Capital)" if st.session_state.get("language") == "my" else "Capital", "eq_capital")
    eq_retain = num_input("စုဆောင်း အမြတ် (Retain Earning)" if st.session_state.get("language") == "my" else "Retain Earning", "eq_retain")

    eq_profit = st.number_input(
        "📈 ယခုနှစ် အမြတ် (Profit for the year) — Trading မှ" if st.session_state.get("language") == "my" else "📈 Profit for the year (from Trading)",
        value=float(st.session_state.bs_data.get("eq_profit", auto_net_profit)),
        min_value=-999999999999.0,
        step=1000.0,
        format="%.2f",
        key="bs_eq_profit_input",
        help="Trading & P&L page မှ auto-fill — လိုအပ်ရင် ပြင်လို့ရ" if st.session_state.get("language") == "my" else "Auto-filled from Trading & P&L",
    )
    st.session_state.bs_data["eq_profit"] = eq_profit

    eq_drawing = num_input("ပိုင်ရှင် ထုတ်ယူမှု (Drawing)" if st.session_state.get("language") == "my" else "Drawing", "eq_drawing", is_deduction=True)
    total_equity = eq_capital + eq_retain + eq_profit - eq_drawing
    subtotal_box("အရင်း စုစုပေါင်း" if st.session_state.get("language") == "my" else "Total Equity", total_equity, "#c2185b")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f'<h3 style="color: #c2185b; font-size: 1.15rem; border-bottom: 2px solid #f093fb; padding-bottom: 0.3rem;">{"၄။ အကြွေးများ (Liabilities)" if st.session_state.get("language") == "my" else "4. Liabilities"}</h3>', unsafe_allow_html=True)
    liab_bank_loan = num_input("ဘဏ် ချေးငွေ (Bank Loan)" if st.session_state.get("language") == "my" else "Bank Loan", "liab_bank_loan")
    liab_payable = num_input("ပေးရန်ကျန်ငွေ (A/C Payable)" if st.session_state.get("language") == "my" else "A/C Payable", "liab_payable")

    total_liab = liab_bank_loan + liab_payable
    subtotal_box("အကြွေး စုစုပေါင်း" if st.session_state.get("language") == "my" else "Total Liabilities", total_liab, "#c2185b")
    st.markdown("<br>", unsafe_allow_html=True)

    total_eq_liab = total_equity + total_liab
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.2rem; border-radius: 12px; color: white; margin-top: 1rem;">
            <p style="margin: 0; font-size: 1rem; opacity: 0.95;">💰 {'အရင်း + အကြွေး စုစုပေါင်း' if st.session_state.get('language') == 'my' else 'Total Equity & Liabilities'}</p>
            <h1 style="margin: 0.4rem 0 0 0; font-size: 1.8rem;">{format_number(total_eq_liab)}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    difference = total_assets - total_eq_liab
    is_balanced = abs(difference) < 0.01

    if is_balanced:
        check_color = "#43e97b"
        check_icon = "✓"
        check_text = "ဟုန်းချင်း ကိုက်ညီပါသည်" if st.session_state.get("language") == "my" else "Balanced"
    else:
        check_color = "#f5576c"
        check_icon = "✗"
        check_text = "ဟုန်းချင်း မကိုက်ညီပါ" if st.session_state.get("language") == "my" else "Not Balanced"

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {check_color} 0%, {check_color}cc 100%); padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1rem; text-align: center;">
            <p style="margin: 0; font-size: 3rem;">{check_icon}</p>
            <h3 style="margin: 0.5rem 0 0 0; font-size: 1.2rem;">{check_text}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    diff_color = "#2e7d32" if is_balanced else "#c62828"
    st.markdown(
        f"""
        <div style="background-color: #f5f5f5; padding: 1rem; border-radius: 8px;">
            <p style="margin: 0 0 0.5rem 0; font-size: 0.85rem; color: #666; font-weight: bold;">📊 {'အသေးစိတ်' if st.session_state.get('language') == 'my' else 'Breakdown'}</p>
            <table style="width: 100%; font-size: 0.9rem;">
                <tr><td>{'ပိုင်ဆိုင်မှု' if st.session_state.get('language') == 'my' else 'Assets'}</td><td style="text-align: right; font-weight: bold;">{format_number(total_assets)}</td></tr>
                <tr><td>{'အရင်း' if st.session_state.get('language') == 'my' else 'Equity'}</td><td style="text-align: right; font-weight: bold;">{format_number(total_equity)}</td></tr>
                <tr><td>{'အကြွေး' if st.session_state.get('language') == 'my' else 'Liabilities'}</td><td style="text-align: right; font-weight: bold;">{format_number(total_liab)}</td></tr>
                <tr style="border-top: 1px solid #ddd;"><td><b>{'အရင်း + အကြွေး' if st.session_state.get('language') == 'my' else 'Equity + Liab'}</b></td><td style="text-align: right; font-weight: bold; color: #c2185b;">{format_number(total_eq_liab)}</td></tr>
                <tr style="border-top: 2px solid {diff_color};"><td><b>{'ကွာဟမှု' if st.session_state.get('language') == 'my' else 'Difference'}</b></td><td style="text-align: right; font-weight: bold; color: {diff_color};">{format_number(difference)}</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.bs_data["_total_assets"] = total_assets
    st.session_state.bs_data["_total_equity"] = total_equity
    st.session_state.bs_data["_total_liab"] = total_liab
    st.session_state.bs_data["_current_assets"] = total_ca
    st.session_state.bs_data["_current_liab"] = total_liab
    st.session_state.bs_data["_cash"] = ca_cash
    st.session_state.bs_data["_depreciation"] = auto_depreciation

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(t('save'), use_container_width=True, type="primary"):
        try:
            bs_data = st.session_state.bs_data
            bs_data["ca_inventories"] = ca_inventories
            bs_data["ca_receivable"] = ca_receivable
            bs_data["ca_advance"] = ca_advance
            bs_data["ca_cash"] = ca_cash
            bs_data["nca_land"] = nca_land
            bs_data["nca_building"] = nca_building
            bs_data["nca_machine"] = nca_machine
            bs_data["nca_furniture"] = nca_furniture
            bs_data["nca_vehicle"] = nca_vehicle
            bs_data["liab_payable"] = liab_payable
            bs_data["liab_bank_loan"] = liab_bank_loan
            bs_data["eq_capital"] = eq_capital
            bs_data["eq_retain"] = eq_retain
            bs_data["eq_profit"] = eq_profit
            bs_data["eq_drawing"] = eq_drawing

            data_json = json.dumps(bs_data, ensure_ascii=False)
            db.save_statement(
                client_id=client_id,
                statement_type="balance_sheet",
                period_end=st.session_state.bs_date,
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
                statement_type="balance_sheet",
                client_name=client["name"],
                data=st.session_state.bs_data,
                as_at_date=st.session_state.bs_date,
                lang=st.session_state.language, # ⭐ Lang ထည့်ပြီး
            )
            st.download_button(
                "⬇️ PDF Download",
                data=pdf_bytes,
                file_name=f"{client['name']}_BalanceSheet_{st.session_state.bs_date}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"❌ PDF Error: {e}")

with col3:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.bs_data = {}
        st.rerun()

with col4:
    if st.button(t('detail'), use_container_width=True):
        st.switch_page("pages/2_Client_Detail.py")

st.divider()
st.caption(f"📅 {t('as_at_date')}: {format_date_mm(st.session_state.bs_date)}")
st.caption(f"👤 {t('clients')}: {client['name']}")
if existing and existing.get("updated_at"):
    st.caption(f"🔄 {t('updated')}: {format_date_mm(existing.get('updated_at', ''))}")