# pages/7_Export.py
"""
Export — ၄ ခုလုံး Financial Statements PDF တစ်ခါတည်း ထုတ်ယူခြင်း
"""

import streamlit as st
import json
import zipfile
import io
from datetime import date

from core import db
from core.utils import format_date_mm, format_number, info_box
from core.pdf_generator import generate_pdf

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Export",
    page_icon="📄",
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
# LOAD ALL STATEMENTS
# ============================================================

statements = {
    "manufacturing": {"icon": "🏭", "data": None, "period": "", "label_my": "ကုန်ထုတ်လုပ်မှု စာရင်း", "label_en": "Manufacturing Account"},
    "trading_pl": {"icon": "💰", "data": None, "period": "", "label_my": "အရောင်းအဝယ် အမြတ်အစွန်း", "label_en": "Trading & Profit/Loss"},
    "balance_sheet": {"icon": "📊", "data": None, "period": "", "label_my": "ငွေစာရင်း လက်ကျန်စာရင်း", "label_en": "Balance Sheet"},
    "cash_flow": {"icon": "💵", "data": None, "period": "", "label_my": "ငွေသား စီးဆင်းမှု ရှင်းတမ်း", "label_en": "Cash Flow Statement"},
}

for key in statements.keys():
    try:
        existing = db.get_statement(client_id, key)
        if existing and existing.get("data"):
            statements[key]["data"] = json.loads(existing["data"])
            statements[key]["period"] = existing.get("period_end", "") or existing.get("as_at_date", "")
    except Exception as e:
        st.warning(f"⚠️ {key}: {e}")

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; padding: 0.5rem 0;">
            <h2 style="color: #1f4788; font-size: 1.3rem; margin: 0;">
                📊 {'စာရင်း အက်ပ်' if st.session_state.get('language', 'my') == 'my' else 'Accounting App'}
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    if st.button("🏠 ပင်မ" if st.session_state.get("language") == "my" else "🏠 Home", use_container_width=True, key="nav_home"):
        st.switch_page("app.py")
    if st.button("👥 ဖောက်သည်" if st.session_state.get("language") == "my" else "👥 Clients", use_container_width=True, key="nav_clients"):
        st.switch_page("pages/1_Clients.py")
    if st.button("📂 အသေးစိတ်" if st.session_state.get("language") == "my" else "📂 Detail", use_container_width=True, key="nav_detail"):
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
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    ">
        <h1 style="margin: 0; font-size: 1.8rem;">
            📄 {'PDF ထုတ်ယူခြင်း' if st.session_state.get('language', 'my') == 'my' else 'Export PDF'}
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.95;">
            Financial Statements Export — {client['name']}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# STATEMENTS STATUS
# ============================================================

st.markdown(
    f"""
    <h3 style="color: #1f4788; font-size: 1.3rem;">
        📋 {'ရှင်းတမ်း ၄ ခု Status' if st.session_state.get('language', 'my') == 'my' else 'Status of 4 Statements'}
    </h3>
    """,
    unsafe_allow_html=True,
)

cols = st.columns(4)
available_count = 0

for idx, (key, stmt) in enumerate(statements.items()):
    with cols[idx]:
        has_data = stmt["data"] is not None
        if has_data:
            available_count += 1

        status_icon = "✓" if has_data else "○"
        status_text = ("✓ ရှိပြီး" if has_data else "○ မရှိသေး") if st.session_state.get("language") == "my" else ("✓ Available" if has_data else "○ Not Available")
        status_color = "#2e7d32" if has_data else "#999"
        border_color = "#2e7d32" if has_data else "#ddd"

        title = stmt["label_my"] if st.session_state.get("language") == "my" else stmt["label_en"]

        st.markdown(
            f"""
            <div style="
                background-color: {'#e8f5e9' if has_data else '#f5f5f5'};
                border: 2px solid {border_color};
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
                margin-bottom: 0.5rem;
                min-height: 180px;
            ">
                <p style="font-size: 2rem; margin: 0;">{stmt['icon']}</p>
                <h4 style="margin: 0.5rem 0 0.3rem 0; color: #1f4788; font-size: 1rem;">
                    {title}
                </h4>
                <p style="margin: 0.5rem 0 0 0; color: {status_color}; 
                          font-weight: bold; font-size: 0.9rem;">
                    {status_icon} {status_text}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not has_data:
            if st.button(
                "➕ ထည့်ရန်" if st.session_state.get("language") == "my" else "➕ Add Data",
                key=f"goto_{key}",
                use_container_width=True,
            ):
                page_map = {
                    "manufacturing": "pages/3_Manufacturing.py",
                    "trading_pl": "pages/4_Trading_PL.py",
                    "balance_sheet": "pages/5_Balance_Sheet.py",
                    "cash_flow": "pages/6_Cash_Flow.py",
                }
                st.switch_page(page_map[key])

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ============================================================
# EXPORT OPTIONS
# ============================================================

st.markdown(
    f"""
    <h3 style="color: #1f4788; font-size: 1.3rem;">
        📄 {'PDF ထုတ်ယူရန် ရွေးချယ်ပါ' if st.session_state.get('language', 'my') == 'my' else 'Choose PDF Export Option'}
    </h3>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 8px;">
            <h4 style="margin: 0; color: #1565c0;">
                📦 Available Statements
            </h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold; color: #1565c0;">
                {available_count} / 4
            </p>
            <p style="margin: 0.3rem 0 0 0; color: #666; font-size: 0.9rem;">
                {'ရှင်းတမ်း %d ခု ထုတ်ယူနိုင်ပါသည်' % available_count if st.session_state.get('language', 'my') == 'my' else f'{available_count} statements available for export'}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div style="background-color: #fff3e0; padding: 1rem; border-radius: 8px;">
            <h4 style="margin: 0; color: #e65100;">
                💡 {'အကြံပြုချက်' if st.session_state.get('language', 'my') == 'my' else 'Recommendation'}
            </h4>
            <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;">
                {'ရှင်းတမ်း ၄ ခုလုံး ဖြည့်ပြီးမှ ထုတ်ယူပါ။ ဘဏ်တင်ပြရာမှာ ၄ ခုလုံး လိုအပ်ပါသည်။' if st.session_state.get('language', 'my') == 'my' else 'Fill all 4 statements before exporting. Banks usually require all 4.'}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# GENERATE BUTTONS
# ============================================================

st.markdown(
    f"""
    <h3 style="color: #1f4788; font-size: 1.3rem;">
        📥 {'ထုတ်ယူရန်' if st.session_state.get('language', 'my') == 'my' else 'Export'}
    </h3>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "📦 အားလုံး ထုတ်ယူ (ZIP)" if st.session_state.get("language") == "my" else "📦 Export All (ZIP)",
        use_container_width=True,
        type="primary",
        disabled=(available_count == 0),
        key="export_zip_btn"
    ):
        try:
            zip_buffer = io.BytesIO()
            lang = st.session_state.get("language", "my")

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for key, stmt in statements.items():
                    if stmt["data"] is None:
                        continue

                    if key == "balance_sheet":
                        pdf_bytes = generate_pdf(
                            statement_type=key,
                            client_name=client["name"],
                            data=stmt["data"],
                            as_at_date=stmt["period"],
                            lang=lang,
                        )
                    else:
                        pdf_bytes = generate_pdf(
                            statement_type=key,
                            client_name=client["name"],
                            data=stmt["data"],
                            period_end=stmt["period"],
                            lang=lang,
                        )

                    safe_name = client["name"].replace(" ", "_")
                    filename = f"{safe_name}_{key}.pdf"
                    zf.writestr(filename, pdf_bytes)

            zip_bytes = zip_buffer.getvalue()

            st.download_button(
                "⬇️ ZIP ရယူရန်" if st.session_state.get("language") == "my" else "⬇️ Download ZIP",
                data=zip_bytes,
                file_name=f"{client['name'].replace(' ', '_')}_FinancialStatements.zip",
                mime="application/zip",
                use_container_width=True,
                key="download_zip_btn"
            )
            st.success(f"✓ ZIP ဖန်တီးပြီး ({len(zip_bytes):,} bytes)" if st.session_state.get("language") == "my" else f"✓ ZIP created ({len(zip_bytes):,} bytes)")
        except Exception as e:
            st.error(f"❌ Error: {e}")

with col2:
    if st.button(
        "📄 တစ်ခုချင်း ထုတ်ယူ" if st.session_state.get("language") == "my" else "📄 Export Individual",
        use_container_width=True,
        disabled=(available_count == 0),
        key="export_indiv_btn"
    ):
        st.session_state["show_individual"] = True

# ============================================================
# INDIVIDUAL DOWNLOAD
# ============================================================

if st.session_state.get("show_individual"):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <h4 style="color: #1f4788;">
            📄 {'တစ်ခုချင်း ထုတ်ယူရန်' if st.session_state.get('language', 'my') == 'my' else 'Individual Download'}
        </h4>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    for idx, (key, stmt) in enumerate(statements.items()):
        if stmt["data"] is None:
            continue

        with cols[idx % 2]:
            try:
                lang = st.session_state.get("language", "my")
                
                if key == "balance_sheet":
                    pdf_bytes = generate_pdf(
                        statement_type=key,
                        client_name=client["name"],
                        data=stmt["data"],
                        as_at_date=stmt["period"],
                        lang=lang,
                    )
                else:
                    pdf_bytes = generate_pdf(
                        statement_type=key,
                        client_name=client["name"],
                        data=stmt["data"],
                        period_end=stmt["period"],
                        lang=lang,
                    )

                filename = f"{client['name'].replace(' ', '_')}_{key}.pdf"
                title = stmt["label_my"] if st.session_state.get("language") == "my" else stmt["label_en"]

                st.download_button(
                    f"{stmt['icon']} {title}",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"dl_{key}",
                )
            except Exception as e:
                st.error(f"{key}: {e}")

# ============================================================
# PREVIEW SUMMARY
# ============================================================

st.divider()
st.markdown(
    f"""
    <h3 style="color: #1f4788; font-size: 1.3rem;">
        📊 {'ရှင်းတမ်း အကျဉ်းချုပ်' if st.session_state.get('language', 'my') == 'my' else 'Statements Summary'}
    </h3>
    """,
    unsafe_allow_html=True,
)

summary_data = []

if statements["manufacturing"]["data"]:
    d = statements["manufacturing"]["data"]
    pc = d.get("_production_cost", 0)
    label = "🏭 ကုန်ထုတ်လုပ်မှု" if st.session_state.get("language") == "my" else "🏭 Manufacturing"
    val_label = "Production Cost"
    summary_data.append((label, f"{val_label}: {format_number(pc)}"))

if statements["trading_pl"]["data"]:
    d = statements["trading_pl"]["data"]
    np_ = d.get("_net_profit", 0)
    label = "💰 အရောင်းအဝယ်" if st.session_state.get("language") == "my" else "💰 Trading P&L"
    val_label = "Net Profit"
    summary_data.append((label, f"{val_label}: {format_number(np_)}"))

if statements["balance_sheet"]["data"]:
    d = statements["balance_sheet"]["data"]
    ta = d.get("_total_assets", 0)
    label = "📊 လက်ကျန်စာရင်း" if st.session_state.get("language") == "my" else "📊 Balance Sheet"
    val_label = "Total Assets"
    summary_data.append((label, f"{val_label}: {format_number(ta)}"))

if statements["cash_flow"]["data"]:
    d = statements["cash_flow"]["data"]
    nc = d.get("_net_change", 0)
    label = "💵 ငွေသားစီးဆင်းမှု" if st.session_state.get("language") == "my" else "💵 Cash Flow"
    val_label = "Net Change"
    summary_data.append((label, f"{val_label}: {format_number(nc)}"))

if summary_data:
    for label, value in summary_data:
        st.markdown(
            f"""
            <div style="
                background-color: #f5f5f5;
                padding: 0.8rem 1rem;
                border-radius: 8px;
                border-left: 4px solid #1565c0;
                margin-bottom: 0.5rem;
            ">
                <span style="font-weight: bold; color: #1f4788;">{label}</span>
                <span style="float: right; color: #666;">{value}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    info_box(
        "ရှင်းတမ်း မရှိသေးပါ။ ရှင်းတမ်း တစ်ခုခုကို အရင် ဖြည့်ပါ။" if st.session_state.get("language") == "my" else "No statements yet. Please fill at least one statement first.",
        "info",
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption(f"👤 {'ဖောက်သည်' if st.session_state.get('language') == 'my' else 'Clients'}: {client['name']}")
st.caption(f"📅 {'ယနေ့' if st.session_state.get('language') == 'my' else 'Today'}: {format_date_mm(str(date.today()))}")