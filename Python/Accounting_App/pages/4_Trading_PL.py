# pages/4_Trading_PL.py
"""
Trading & Profit/Loss — Income Statement
Format: Revenue → Cost of Sales → Gross Profit → Admin Expenses → Net Profit
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
    page_title="Trading & P&L",
    page_icon="💰",
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
# LOAD EXISTING
# ============================================================

existing = None
saved_data = {}
saved_period = ""

try:
    existing = db.get_statement(client_id, "trading_pl")
    if existing and existing.get("data"):
        saved_data = json.loads(existing["data"])
        saved_period = existing.get("period_end", "")
except Exception:
    existing = None
    saved_data = {}
    saved_period = ""

# ============================================================
# TRY TO PULL MANUFACTURING COST
# ============================================================

mfg_production_cost = 0.0
mfg_existing = None
try:
    mfg_existing = db.get_statement(client_id, "manufacturing")
    if mfg_existing and mfg_existing.get("data"):
        mfg_data = json.loads(mfg_existing["data"])
        mfg_production_cost = float(mfg_data.get("_production_cost", 0.0))
except Exception:
    mfg_production_cost = 0.0

# ============================================================
# SESSION STATE
# ============================================================

if "tpl_data" not in st.session_state:
    st.session_state.tpl_data = dict(saved_data)

if "tpl_period" not in st.session_state:
    st.session_state.tpl_period = saved_period or str(date.today())

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
    if st.button(t('mfg_acc'), use_container_width=True):
        st.switch_page("pages/3_Manufacturing.py")

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
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    ">
        <h1 style="margin: 0; font-size: 1.8rem;">
            💰 {t('pdf_trading')}
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem; opacity: 0.95;">
            Trading & Profit/Loss — {client['name']}
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
        initial_date = date.fromisoformat(st.session_state.tpl_period)
    except Exception:
        initial_date = date.today()

    period_end = st.date_input(
        f"📅 {t('period_end')}",
        value=initial_date,
        key="tpl_period_input",
    )
    st.session_state.tpl_period = str(period_end)

# ============================================================
# HELPER
# ============================================================

def num_input(label: str, key: str, is_deduction: bool = False, 
              help_text: str = "") -> float:
    value = st.session_state.tpl_data.get(key, 0.0)
    prefix = "➖ " if is_deduction else ""
    result = st.number_input(
        f"{prefix}{label}",
        value=float(value) if value else 0.0,
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key=f"tpl_{key}",
        help=help_text,
    )
    st.session_state.tpl_data[key] = result
    return result

def subtotal_box(label: str, value: float, color: str = "#1976d2"):
    st.markdown(
        f"""
        <div style="background-color: {color}20; 
                    border-left: 3px solid {color};
                    padding: 0.6rem 0.8rem; 
                    border-radius: 6px; 
                    margin: 0.5rem 0;">
            <span style="color: {color}; font-weight: bold;">{label}:</span>
            <span style="float: right; font-weight: bold; color: {color};">
                {format_number(value)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 3 COLUMNS LAYOUT
# ============================================================

col1, col2, col3 = st.columns(3)

# ============================================================
# COLUMN 1 — REVENUE + COST OF SALES
# ============================================================

with col1:
    # --- Revenue ---
    st.markdown(
        f"""
        <h3 style="color: #1976d2; font-size: 1.15rem; 
                   border-bottom: 2px solid #4facfe; padding-bottom: 0.3rem;">
            {'၁။ အရောင်းများ (Revenue)' if st.session_state.get('language', 'my') == 'my' else '1. Revenue'}
        </h3>
        """,
        unsafe_allow_html=True,
    )
    rev_cash = num_input("ငွေသား အရောင်း" if st.session_state.get("language") == "my" else "Cash Sales", "cash_sales")
    rev_credit = num_input("အကြွေး အရောင်း" if st.session_state.get("language") == "my" else "Credit Sales", "credit_sales")
    rev_return = num_input("အရောင်းပြန်အမ်း" if st.session_state.get("language") == "my" else "Sales Returns", "sales_return", is_deduction=True)

    total_revenue = rev_cash + rev_credit - rev_return
    subtotal_box("စုစုပေါင်း အရောင်း" if st.session_state.get("language") == "my" else "Total Revenue", total_revenue, "#1976d2")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Cost of Sales ---
    st.markdown(
        f"""
        <h3 style="color: #1976d2; font-size: 1.15rem; 
                   border-bottom: 2px solid #4facfe; padding-bottom: 0.3rem;">
            {'၂။ ရောင်းကုန် ကုန်ကျစရိတ် (Cost of Sales)' if st.session_state.get('language', 'my') == 'my' else '2. Cost of Sales'}
        </h3>
        """,
        unsafe_allow_html=True,
    )

    mfg_cost_input = st.number_input(
        "🏭 ကုန်ထုတ်လုပ်မှု ကုန်ကျစရိတ် (Manufacturing မှ)" if st.session_state.get("language") == "my" else "🏭 Manufacturing Cost (Auto)",
        value=float(st.session_state.tpl_data.get("manufacturing_cost", mfg_production_cost)),
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="tpl_manufacturing_cost_input",
        help="Manufacturing page မှ ကုန်ကျစရိတ် — auto ဖြည့်ထား" if st.session_state.get("language") == "my" else "Auto-filled from Manufacturing page",
    )
    st.session_state.tpl_data["manufacturing_cost"] = mfg_cost_input

    cs_opening = num_input("အဖွင့် ကုန်ချောလက်ကျန်" if st.session_state.get("language") == "my" else "Opening Stock (Finished)", "opening_stock_finished")
    cs_purchases = num_input("ကုန်ပစ္စည်း ဝယ်ယူမှု" if st.session_state.get("language") == "my" else "Purchases", "purchases")
    cs_carriage = num_input("သယ်ယူပို့ဆောင်ခ" if st.session_state.get("language") == "my" else "Carriage Inward", "carriage_inward")
    cs_return = num_input("ဝယ်ယူမှု ပြန်အမ်း" if st.session_state.get("language") == "my" else "Purchase Returns", "purchase_return", is_deduction=True)
    cs_closing = num_input("အပိတ် ကုန်ချောလက်ကျန်" if st.session_state.get("language") == "my" else "Closing Stock (Finished)", "closing_stock_finished", is_deduction=True)

    total_cos = (
        mfg_cost_input + cs_opening + cs_purchases + 
        cs_carriage - cs_return - cs_closing
    )
    subtotal_box("အရောင်း ကုန်ကျစရိတ် စုစုပေါင်း" if st.session_state.get("language") == "my" else "Total Cost of Sales", total_cos, "#1976d2")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Gross Profit ---
    gross_profit = total_revenue - total_cos
    gp_color = "#43e97b" if gross_profit >= 0 else "#f5576c"
    gp_label = ("အမြတ် (Gross Profit)" if gross_profit >= 0 else "အရှုံး (Gross Loss)") if st.session_state.get("language") == "my" else ("Gross Profit" if gross_profit >= 0 else "Gross Loss")

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {gp_color} 0%, {gp_color}cc 100%);
            padding: 1.2rem;
            border-radius: 12px;
            color: white;
            margin-top: 1rem;
        ">
            <p style="margin: 0; font-size: 0.95rem; opacity: 0.95;">
                💰 {gp_label}
            </p>
            <h2 style="margin: 0.4rem 0 0 0; font-size: 1.8rem;">
                {format_number(gross_profit)}
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# COLUMN 2 — ADMIN EXPENSES
# ============================================================

with col2:
    st.markdown(
        f"""
        <h3 style="color: #c2185b; font-size: 1.15rem; 
                   border-bottom: 2px solid #f093fb; padding-bottom: 0.3rem;">
            {'၃။ စီမံ သုံးစွဲမှုများ (Admin Expenses)' if st.session_state.get('language', 'my') == 'my' else '3. Admin Expenses'}
        </h3>
        """,
        unsafe_allow_html=True,
    )

    exp_salary = num_input("ဝန်ထမ်းခနှင့် အလုပ်သမားခ" if st.session_state.get("language") == "my" else "Staff Salaries", "staff_salary")
    exp_tax = num_input("အခွန်နှင့် အခြား" if st.session_state.get("language") == "my" else "Tax & Other", "tax_other")
    exp_electricity = num_input("လျှပ်စစ်ခ" if st.session_state.get("language") == "my" else "Electricity", "electricity")
    exp_telephone = num_input("တယ်လီဖုန်းခ" if st.session_state.get("language") == "my" else "Telephone", "telephone")
    exp_fuel = num_input("လောင်စာ" if st.session_state.get("language") == "my" else "Fuel", "fuel")
    exp_repair = num_input("ပြုပြင်ထိန်းသိမ်းမှု" if st.session_state.get("language") == "my" else "Repair & Maintenance", "repair_maintenance")
    exp_general = num_input("အထွေထွေ သုံးစွဲမှု" if st.session_state.get("language") == "my" else "General Expenses", "general_expenses")

    st.markdown(
        f"""
        <p style="color: #666; font-size: 0.9rem; margin: 0.5rem 0;">
            📉 {'တန်ဖိုးကျဆင်းမှု (Depreciation):' if st.session_state.get('language', 'my') == 'my' else 'Depreciation:'}
        </p>
        """,
        unsafe_allow_html=True,
    )
    exp_dep_building = num_input("အဆောက်အအုံ" if st.session_state.get("language") == "my" else "Building", "dep_building")
    exp_dep_machine = num_input("စက်ပစ္စည်း" if st.session_state.get("language") == "my" else "Machine", "dep_machine")
    exp_dep_furniture = num_input("ပရိဘောဂ" if st.session_state.get("language") == "my" else "Furniture", "dep_furniture")
    exp_dep_vehicle = num_input("ယာဉ်" if st.session_state.get("language") == "my" else "Vehicle", "dep_vehicle")

    total_depreciation = (exp_dep_building + exp_dep_machine + exp_dep_furniture + exp_dep_vehicle)

    total_expenses = (
        exp_salary + exp_tax + exp_electricity + exp_telephone +
        exp_fuel + exp_repair + exp_general + total_depreciation
    )

    subtotal_box("စီမံ သုံးစွဲမှု စုစုပေါင်း" if st.session_state.get("language") == "my" else "Total Admin Expenses", total_expenses, "#c2185b")
    st.session_state.tpl_data["_depreciation"] = total_depreciation

# ============================================================
# COLUMN 3 — LIVE CALC
# ============================================================

with col3:
    net_profit = gross_profit - total_expenses

    np_color = "#43e97b" if net_profit >= 0 else "#f5576c"
    np_label = ("အသားတင် အမြတ်" if net_profit >= 0 else "အသားတင် အရှုံး") if st.session_state.get("language") == "my" else ("Net Profit" if net_profit >= 0 else "Net Loss")

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {np_color} 0%, {np_color}cc 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1rem;
        ">
            <p style="margin: 0; font-size: 1rem; opacity: 0.95;">
                🎯 {np_label}
            </p>
            <h1 style="margin: 0.5rem 0 0 0; font-size: 2.2rem;">
                {format_number(net_profit)}
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.tpl_data["_net_profit"] = net_profit
    st.session_state.tpl_data["_gross_profit"] = gross_profit
    st.session_state.tpl_data["_total_revenue"] = total_revenue
    st.session_state.tpl_data["_total_cos"] = total_cos

    st.markdown(
        f"""
        <div style="background-color: #f5f5f5; padding: 1rem; border-radius: 8px;">
            <p style="margin: 0 0 0.5rem 0; font-size: 0.85rem; color: #666; font-weight: bold;">
                📊 {'အသေးစိတ်' if st.session_state.get('language', 'my') == 'my' else 'Breakdown'}
            </p>
            <table style="width: 100%; font-size: 0.9rem;">
                <tr>
                    <td>{'အရောင်း' if st.session_state.get('language', 'my') == 'my' else 'Revenue'}</td>
                    <td style="text-align: right; font-weight: bold;">{format_number(total_revenue)}</td>
                </tr>
                <tr>
                    <td>{'ကုန်ကျစရိတ်' if st.session_state.get('language', 'my') == 'my' else 'Cost of Sales'}</td>
                    <td style="text-align: right; font-weight: bold; color: #c62828;">
                        ({format_number(total_cos)})
                    </td>
                </tr>
                <tr style="border-top: 1px solid #ddd;">
                    <td><b>Gross Profit</b></td>
                    <td style="text-align: right; font-weight: bold; color: #1976d2;">
                        {format_number(gross_profit)}
                    </td>
                </tr>
                <tr>
                    <td>{'သုံးစွဲမှု' if st.session_state.get('language', 'my') == 'my' else 'Expenses'}</td>
                    <td style="text-align: right; font-weight: bold; color: #c62828;">
                        ({format_number(total_expenses)})
                    </td>
                </tr>
                <tr style="border-top: 2px solid {np_color};">
                    <td><b>Net Profit</b></td>
                    <td style="text-align: right; font-weight: bold; color: {np_color}; font-size: 1.05rem;">
                        {format_number(net_profit)}
                    </td>
                </tr>
            </table>
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
            data_json = json.dumps(st.session_state.tpl_data, ensure_ascii=False)
            db.save_statement(
                client_id=client_id,
                statement_type="trading_pl",
                period_end=st.session_state.tpl_period,
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
                statement_type="trading_pl",
                client_name=client["name"],
                data=st.session_state.tpl_data,
                period_end=st.session_state.tpl_period,
                lang=st.session_state.language, # ⭐ Lang ထည့်ပြီး
            )
            st.download_button(
                "⬇️ PDF Download",
                data=pdf_bytes,
                file_name=f"{client['name']}_TradingPL_{st.session_state.tpl_period}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"❌ PDF Error: {e}")

with col3:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.tpl_data = {}
        st.rerun()

with col4:
    if st.button(t('detail'), use_container_width=True):
        st.switch_page("pages/2_Client_Detail.py")

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption(f"📅 {t('period_end')}: {format_date_mm(st.session_state.tpl_period)}")
st.caption(f"👤 {t('clients')}: {client['name']}")
if existing and existing.get("updated_at"):
    st.caption(f"🔄 {t('updated')}: {format_date_mm(existing.get('updated_at', ''))}")