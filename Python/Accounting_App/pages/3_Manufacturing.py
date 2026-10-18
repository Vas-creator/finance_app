# pages/3_Manufacturing.py
"""
Manufacturing Account — ကုန်ထုတ်လုပ်မှု စာရင်း
Real-time calculation + Save to DB + PDF Export
"""

import streamlit as st
import json
from datetime import date

from core import db
from core.utils import (
    format_number, format_currency, format_date_mm,
    info_box, parse_number
)
from core.templates import get_input_fields
from core.pdf_generator import generate_pdf, calculate_manufacturing
from core.translations import t

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Manufacturing",
    page_icon="🏭",
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
# LOAD EXISTING DATA
# ============================================================

existing = None
saved_data = {}
saved_period = ""

try:
    existing = db.get_statement(client_id, "manufacturing")
    if existing and existing.get("data"):
        saved_data = json.loads(existing["data"])
        saved_period = existing.get("period_end", "")
    else:
        saved_data = {}
        saved_period = ""
except Exception:
    existing = None
    saved_data = {}
    saved_period = ""

# ============================================================
# SESSION STATE INIT
# ============================================================

if "mfg_data" not in st.session_state:
    st.session_state.mfg_data = dict(saved_data)

if "mfg_period" not in st.session_state:
    st.session_state.mfg_period = saved_period or str(date.today())

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
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    ">
        <h1 style="margin: 0; font-size: 1.8rem;">
            🏭 {t('pdf_mfg')}
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem; opacity: 0.95;">
            Manufacturing Account — {client['name']}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# PERIOD END
# ============================================================

col1, col2 = st.columns([1, 3])
with col1:
    period_end = st.date_input(
        f"📅 {t('period_end')}",
        value=date.fromisoformat(st.session_state.mfg_period) if st.session_state.mfg_period else date.today(),
        key="mfg_period_input",
    )
    st.session_state.mfg_period = str(period_end)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# INPUT HELPER
# ============================================================

def number_input(label: str, key: str, help_text: str = "", 
                 is_deduction: bool = False) -> float:
    """Number input with formatting"""
    value = st.session_state.mfg_data.get(key, 0.0)
    
    prefix = "➖ " if is_deduction else ""
    
    result = st.number_input(
        f"{prefix}{label}",
        value=float(value) if value else 0.0,
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key=f"mfg_{key}",
        help=help_text,
    )
    st.session_state.mfg_data[key] = result
    return result

# ============================================================
# FORM — 3 COLUMNS
# ============================================================

col1, col2, col3 = st.columns(3)

# ---------- Column 1: Direct Materials + Labour + Expenses ----------
with col1:
    st.markdown(
        f"""
        <h3 style="color: #c2185b; font-size: 1.15rem; 
                   border-bottom: 2px solid #f093fb; padding-bottom: 0.3rem;">
            {'၁။ တိုက်ရိုက် ကုန်ကြမ်းများ' if st.session_state.get('language', 'my') == 'my' else '1. Direct Materials'}
        </h3>
        """,
        unsafe_allow_html=True,
    )
    dm_opening = number_input("အဖွင့် ကုန်ကြမ်းလက်ကျန်" if st.session_state.get("language") == "my" else "Opening Stock (Raw)", "opening_stock_raw")
    dm_purchases = number_input("ကုန်ကြမ်းဝယ်ယူမှု" if st.session_state.get("language") == "my" else "Purchases (Raw)", "purchases_raw")
    dm_carriage = number_input("သယ်ယူပို့ဆောင်ခ" if st.session_state.get("language") == "my" else "Carriage Inward", "carriage_inward")
    dm_customs = number_input("အကောက်ခွန်" if st.session_state.get("language") == "my" else "Customs Duty", "customs_duty")
    dm_closing = number_input("အပိတ် ကုန်ကြမ်းလက်ကျန်" if st.session_state.get("language") == "my" else "Closing Stock (Raw)", "closing_stock_raw", is_deduction=True)

    cost_of_materials = dm_opening + dm_purchases + dm_carriage + dm_customs - dm_closing
    st.markdown(
        f"""
        <div style="background-color: #fce4ec; padding: 0.6rem; border-radius: 6px; margin-top: 0.5rem;">
            <span style="color: #c2185b; font-weight: bold;">{'အသုံးပြုသော ကုန်ကြမ်းကုန်ကျစရိတ်' if st.session_state.get('language', 'my') == 'my' else 'Cost of Materials Used'}:</span>
            <span style="float: right; font-weight: bold; color: #c2185b;">
                {format_number(cost_of_materials)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <h3 style="color: #c2185b; font-size: 1.15rem; 
                   border-bottom: 2px solid #f093fb; padding-bottom: 0.3rem;">
            {'၂။ တိုက်ရိုက် အလုပ်သမားခ' if st.session_state.get('language', 'my') == 'my' else '2. Direct Labour'}
        </h3>
        """,
        unsafe_allow_html=True,
    )
    dl_direct = number_input("တိုက်ရိုက် အလုပ်သမားခ" if st.session_state.get("language") == "my" else "Direct Wages", "wages_direct")
    dl_overtime = number_input("အချိန်ပို အလုပ်သမားခ" if st.session_state.get("language") == "my" else "Overtime Wages", "wages_overtime")
    dl_contract = number_input("စာချုပ် အလုပ်သမားခ" if st.session_state.get("language") == "my" else "Contract Wages", "wages_contract")

    direct_labour_total = dl_direct + dl_overtime + dl_contract
    st.markdown(
        f"""
        <div style="background-color: #fce4ec; padding: 0.6rem; border-radius: 6px; margin-top: 0.5rem;">
            <span style="color: #c2185b; font-weight: bold;">{'အလုပ်သမားခ စုစုပေါင်း' if st.session_state.get('language', 'my') == 'my' else 'Total Direct Labour'}:</span>
            <span style="float: right; font-weight: bold; color: #c2185b;">
                {format_number(direct_labour_total)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <h3 style="color: #c2185b; font-size: 1.15rem; 
                   border-bottom: 2px solid #f093fb; padding-bottom: 0.3rem;">
            {'၃။ တိုက်ရိုက် အသုံးစရိတ်များ' if st.session_state.get('language', 'my') == 'my' else '3. Direct Expenses'}
        </h3>
        """,
        unsafe_allow_html=True,
    )
    de_royalty = number_input("မူပိုင်ခွင့်ကြေး" if st.session_state.get("language") == "my" else "Royalty", "royalty")
    de_hire = number_input("စက်ပစ္စည်း ငှားရမ်းခ" if st.session_state.get("language") == "my" else "Hire of Plant", "hire_plant")
    de_fuel = number_input("လောင်စာနှင့် လျှပ်စစ်" if st.session_state.get("language") == "my" else "Fuel & Power", "fuel_power_direct")

    direct_expenses_total = de_royalty + de_hire + de_fuel
    st.markdown(
        f"""
        <div style="background-color: #fce4ec; padding: 0.6rem; border-radius: 6px; margin-top: 0.5rem;">
            <span style="color: #c2185b; font-weight: bold;">{'တိုက်ရိုက် အသုံးစရိတ် စုစုပေါင်း' if st.session_state.get('language', 'my') == 'my' else 'Total Direct Expenses'}:</span>
            <span style="float: right; font-weight: bold; color: #c2185b;">
                {format_number(direct_expenses_total)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Column 2: Factory Overhead ----------
with col2:
    st.markdown(
        f"""
        <h3 style="color: #1976d2; font-size: 1.15rem; 
                   border-bottom: 2px solid #4facfe; padding-bottom: 0.3rem;">
            {'၄။ စက်ရုံ အသုံးစရိတ်များ' if st.session_state.get('language', 'my') == 'my' else '4. Factory Overhead'}
        </h3>
        """,
        unsafe_allow_html=True,
    )
    fo_rent = number_input("စက်ရုံ ငှားရမ်းခ" if st.session_state.get("language") == "my" else "Factory Rent", "factory_rent")
    fo_rates = number_input("စက်ရုံ အခွန်" if st.session_state.get("language") == "my" else "Factory Rates", "factory_rates")
    fo_insurance = number_input("စက်ရုံ အာမခံ" if st.session_state.get("language") == "my" else "Factory Insurance", "factory_insurance")
    fo_power = number_input("စက်ရုံ လျှပ်စစ်" if st.session_state.get("language") == "my" else "Factory Power", "factory_power")
    fo_salary = number_input("စက်ရုံ ဝန်ထမ်းခ" if st.session_state.get("language") == "my" else "Factory Salary", "factory_salary")
    fo_depr = number_input("စက်ပစ္စည်း တန်ဖိုးကျဆင်း" if st.session_state.get("language") == "my" else "Depreciation - Plant", "depreciation_plant")
    fo_repairs = number_input("စက်ပစ္စည်း ပြုပြင်ခ" if st.session_state.get("language") == "my" else "Repairs - Plant", "repairs_plant")
    fo_indirect = number_input("သွယ်ဝိုက် အလုပ်သမားခ" if st.session_state.get("language") == "my" else "Indirect Wages", "indirect_wages")
    fo_misc = number_input("အထွေထွေ စက်ရုံစရိတ်" if st.session_state.get("language") == "my" else "Misc Factory Exp", "factory_misc")

    factory_overhead_total = (
        fo_rent + fo_rates + fo_insurance + fo_power + fo_salary +
        fo_depr + fo_repairs + fo_indirect + fo_misc
    )
    st.markdown(
        f"""
        <div style="background-color: #e3f2fd; padding: 0.6rem; border-radius: 6px; margin-top: 0.5rem;">
            <span style="color: #1976d2; font-weight: bold;">{'စက်ရုံ စုစုပေါင်း' if st.session_state.get('language', 'my') == 'my' else 'Total Factory Overhead'}:</span>
            <span style="float: right; font-weight: bold; color: #1976d2;">
                {format_number(factory_overhead_total)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <h3 style="color: #1976d2; font-size: 1.15rem; 
                   border-bottom: 2px solid #4facfe; padding-bottom: 0.3rem;">
            {'၅။ လုပ်ငန်း ဆောင်ရွက်ဆဲ (WIP)' if st.session_state.get('language', 'my') == 'my' else '5. Work in Progress'}
        </h3>
        """,
        unsafe_allow_html=True,
    )
    wip_opening = number_input("အဖွင့် WIP" if st.session_state.get("language") == "my" else "Opening WIP", "add_opening_wip")
    wip_closing = number_input("အပိတ် WIP" if st.session_state.get("language") == "my" else "Closing WIP", "less_closing_wip", is_deduction=True)

# ---------- Column 3: LIVE CALCULATION ----------
with col3:
    prime_cost = cost_of_materials + direct_labour_total + direct_expenses_total
    production_cost = prime_cost + factory_overhead_total + wip_opening - wip_closing

    # Prime Cost card
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1rem;
        ">
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">
                ⭐ {'အခြေခံ ကုန်ကျစရိတ်' if st.session_state.get('language', 'my') == 'my' else 'Prime Cost'}
            </p>
            <h2 style="margin: 0.3rem 0 0 0; font-size: 1.6rem;">
                {format_number(prime_cost)}
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Production Cost card
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1rem;
        ">
            <p style="margin: 0; font-size: 1rem; opacity: 0.95;">
                🎯 {'ကုန်ထုတ်လုပ်မှု ကုန်ကျစရိတ်' if st.session_state.get('language', 'my') == 'my' else 'Production Cost'}
            </p>
            <h1 style="margin: 0.5rem 0 0 0; font-size: 2.2rem;">
                {format_number(production_cost)}
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Breakdown
    st.markdown(
        f"""
        <div style="background-color: #f5f5f5; padding: 1rem; border-radius: 8px;">
            <p style="margin: 0 0 0.5rem 0; font-size: 0.85rem; color: #666; font-weight: bold;">
                📊 {'အသေးစိတ်' if st.session_state.get('language', 'my') == 'my' else 'Breakdown'}
            </p>
            <table style="width: 100%; font-size: 0.9rem;">
                <tr>
                    <td>{'ကုန်ကြမ်း' if st.session_state.get('language', 'my') == 'my' else 'Materials'}</td>
                    <td style="text-align: right; font-weight: bold;">{format_number(cost_of_materials)}</td>
                </tr>
                <tr>
                    <td>{'အလုပ်သမားခ' if st.session_state.get('language', 'my') == 'my' else 'Labour'}</td>
                    <td style="text-align: right; font-weight: bold;">{format_number(direct_labour_total)}</td>
                </tr>
                <tr>
                    <td>{'တိုက်ရိုက် စရိတ်' if st.session_state.get('language', 'my') == 'my' else 'Direct Exp'}</td>
                    <td style="text-align: right; font-weight: bold;">{format_number(direct_expenses_total)}</td>
                </tr>
                <tr style="border-top: 1px solid #ddd;">
                    <td><b>Prime Cost</b></td>
                    <td style="text-align: right; font-weight: bold; color: #f5576c;">
                        {format_number(prime_cost)}
                    </td>
                </tr>
                <tr>
                    <td>{'စက်ရုံ စရိတ်' if st.session_state.get('language', 'my') == 'my' else 'Factory Overhead'}</td>
                    <td style="text-align: right; font-weight: bold;">{format_number(factory_overhead_total)}</td>
                </tr>
                <tr>
                    <td>WIP (net)</td>
                    <td style="text-align: right; font-weight: bold;">{format_number(wip_opening - wip_closing)}</td>
                </tr>
                <tr style="border-top: 2px solid #38f9d7;">
                    <td><b>Production Cost</b></td>
                    <td style="text-align: right; font-weight: bold; color: #38a169; font-size: 1.05rem;">
                        {format_number(production_cost)}
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
            st.session_state.mfg_data["_production_cost"] = production_cost
            data_json = json.dumps(st.session_state.mfg_data, ensure_ascii=False)
            db.save_statement(
                client_id=client_id,
                statement_type="manufacturing",
                period_end=st.session_state.mfg_period,
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
                statement_type="manufacturing",
                client_name=client["name"],
                data=st.session_state.mfg_data,
                period_end=st.session_state.mfg_period,
                lang=st.session_state.language,  # ⭐ Lang ထည့်ပြီး
            )
            st.download_button(
                "⬇️ PDF Download",
                data=pdf_bytes,
                file_name=f"{client['name']}_Manufacturing_{st.session_state.mfg_period}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"❌ PDF Error: {e}")

with col3:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.mfg_data = {}
        st.rerun()

with col4:
    if st.button(t('detail'), use_container_width=True):
        st.switch_page("pages/2_Client_Detail.py")

# ============================================================
# FOOTER INFO
# ============================================================

st.divider()
st.caption(f"📅 {t('period_end')}: {format_date_mm(st.session_state.mfg_period)}")
st.caption(f"👤 {t('clients')}: {client['name']}")
if existing and existing.get('updated_at'):
    st.caption(f"🔄 {t('updated')}: {format_date_mm(existing.get('updated_at', ''))}")