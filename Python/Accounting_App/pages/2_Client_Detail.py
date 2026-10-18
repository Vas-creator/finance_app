# pages/2_Client_Detail.py
"""
Client Detail — ဖောက်သည် အသေးစိတ် + ရှင်းတမ်း ၄ ခု Overview
"""
import streamlit as st
from core import db
from core.utils import format_date_mm
from core.translations import t

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Client Detail",
    page_icon="📂",
    layout="wide",
)

# ============================================================
# AUTH CHECK
# ============================================================

if not st.session_state.get("authentication_status"):
    st.warning("⚠️ ကျေးဇူးပြု၍ အရင် ဝင်ရောက်ပါ" if st.session_state.get("language", "my") == "my" else "⚠️ Please login first")
    st.switch_page("app.py")
    st.stop()

# ============================================================
# CLIENT ID CHECK
# ============================================================

client_id = st.session_state.get("selected_client_id")

if not client_id:
    st.warning("⚠️ ဖောက်သည် မရွေးရသေးပါ" if st.session_state.get("language", "my") == "my" else "⚠️ No client selected")
    if st.button("← ဖောက်သည် စာရင်းသို့ ပြန်" if st.session_state.get("language", "my") == "my" else "← Back to Clients"):
        st.switch_page("pages/1_Clients.py")
    st.stop()

# ============================================================
# LOAD CLIENT
# ============================================================

try:
    client = db.get_client(client_id)
except Exception as e:
    st.error(f"❌ Database error: {e}")
    st.stop()

if not client:
    st.error("❌ ဖောက်သည် မတွေ့ပါ" if st.session_state.get("language", "my") == "my" else "❌ Client not found")
    if st.button("← ဖောက်သည် စာရင်းသို့ ပြန်" if st.session_state.get("language", "my") == "my" else "← Back to Clients"):
        st.switch_page("pages/1_Clients.py")
    st.stop()

# ============================================================
# SIDEBAR NAVIGATION
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

    st.divider()

    st.markdown(
        f"""
        <div style="
            background-color: #e3f2fd;
            padding: 0.8rem;
            border-radius: 8px;
            border-left: 4px solid #1565c0;
            margin-bottom: 1rem;
        ">
            <p style="margin: 0; font-size: 0.85rem; color: #666;">{'လက်ရှိ ဖောက်သည်' if st.session_state.get('language', 'my') == 'my' else 'Current Client'}</p>
            <p style="margin: 0.2rem 0 0 0; font-weight: bold; color: #1565c0;">
                👤 {client['name']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"👤 {st.session_state.get('name', 'User')}")

# ============================================================
# HEADER — Client Info
# ============================================================

col_back, col_blank = st.columns([1, 5])
with col_back:
    if st.button("← " + ("ပြန်" if st.session_state.get("language", "my") == "my" else "Back"), use_container_width=True):
        st.switch_page("pages/1_Clients.py")

st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    ">
        <h1 style="margin: 0; font-size: 2rem;">
            👤 {client['name']}
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.95;">
            {f'🏢 {client.get("business_name")}' if client.get('business_name') else ''}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Client Info Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div style="background-color: #f5f5f5; padding: 0.8rem; border-radius: 8px;">
            <p style="margin: 0; font-size: 0.8rem; color: #666;">📧 {t('email')}</p>
            <p style="margin: 0.3rem 0 0 0; font-weight: bold; color: #333;">
                {client.get('email') or '—'}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div style="background-color: #f5f5f5; padding: 0.8rem; border-radius: 8px;">
            <p style="margin: 0; font-size: 0.8rem; color: #666;">📞 {t('phone')}</p>
            <p style="margin: 0.3rem 0 0 0; font-weight: bold; color: #333;">
                {client.get('phone') or '—'}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div style="background-color: #f5f5f5; padding: 0.8rem; border-radius: 8px;">
            <p style="margin: 0; font-size: 0.8rem; color: #666;">📍 {t('address')}</p>
            <p style="margin: 0.3rem 0 0 0; font-weight: bold; color: #333;">
                {client.get('address') or '—'}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div style="background-color: #f5f5f5; padding: 0.8rem; border-radius: 8px;">
            <p style="margin: 0; font-size: 0.8rem; color: #666;">💼 {t('business_type')}</p>
            <p style="margin: 0.3rem 0 0 0; font-weight: bold; color: #333; font-size: 0.85rem;">
                {client.get('business_type') or '—'}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# STATEMENTS OVERVIEW
# ============================================================

st.markdown(
    f"""
    <h2 style="color: #1f4788; font-size: 1.6rem; margin-top: 1rem;">
        {t('all_statements')}
    </h2>
    """,
    unsafe_allow_html=True,
)

# Statement types
statements_config = [
    {
        "key": "manufacturing",
        "icon": "🏭",
        "page": "pages/3_Manufacturing.py",
        "color": "#f093fb",
    },
    {
        "key": "trading_pl",
        "icon": "💰",
        "page": "pages/4_Trading_PL.py",
        "color": "#4facfe",
    },
    {
        "key": "balance_sheet",
        "icon": "📊",
        "page": "pages/5_Balance_Sheet.py",
        "color": "#43e97b",
    },
    {
        "key": "cash_flow",
        "icon": "💵",
        "page": "pages/6_Cash_Flow.py",
        "color": "#667eea",
    },
]

cols = st.columns(4)
for idx, stmt in enumerate(statements_config):
    with cols[idx]:
        try:
            existing = db.get_statement(client_id, stmt["key"])
            has_data = existing is not None
        except Exception:
            has_data = False

        status_icon = "✓" if has_data else "○"
        status_text = t("has_data") if has_data else t("no_data")
        status_color = "#2e7d32" if has_data else "#999"
        
        # Statement Title
        title_key = stmt["key"]
        if title_key == "manufacturing":
            title = t("manufacturing")
        elif title_key == "trading_pl":
            title = t("trading_pl")
        elif title_key == "balance_sheet":
            title = t("balance_sheet_title")
        elif title_key == "cash_flow":
            title = t("cash_flow")

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, {stmt['color']}40, {stmt['color']}20);
                border: 2px solid {stmt['color']};
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                margin-bottom: 0.5rem;
                min-height: 200px;
            ">
                <p style="font-size: 3rem; margin: 0;">{stmt['icon']}</p>
                <h3 style="margin: 0.5rem 0 0.3rem 0; color: #1f4788; font-size: 1.15rem;">
                    {title}
                </h3>
                <p style="margin: 0.8rem 0 0 0; color: {status_color}; font-weight: bold; font-size: 0.95rem;">
                    {status_icon} {status_text}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            t("open_page") if has_data else t("add_data"),
            key=f"goto_{stmt['key']}",
            use_container_width=True,
            type="primary" if not has_data else "secondary",
        ):
            st.session_state["selected_client_id"] = client_id
            st.session_state["selected_client_name"] = client["name"]
            st.switch_page(stmt["page"])

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# PDF EXPORT SECTION
# ============================================================

st.markdown(
    f"""
    <h2 style="color: #1f4788; font-size: 1.6rem; margin-top: 1rem;">
        📄 {t('export_pdf')}
    </h2>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style="
        background-color: #fff3e0;
        border-left: 5px solid #e65100;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    ">
        <p style="margin: 0; color: #e65100; font-size: 1rem;">
            💡 <b>{t('export_pdf')}</b> — {'ရှင်းတမ်း ၄ ခုလုံး ဖြည့်ပြီးမှ ဤနေရာမှ ထုတ်ယူပါ' if st.session_state.get('language', 'my') == 'my' else 'Fill all 4 statements before exporting PDF'}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    if st.button(f"📄 {t('export_pdf')}", use_container_width=True, type="primary"):
        st.session_state["selected_client_id"] = client_id
        st.session_state["selected_client_name"] = client["name"]
        st.switch_page("pages/7_Export.py")

with col2:
    if st.button(t("delete_client"), use_container_width=True):
        st.session_state["delete_from_detail"] = True
        st.rerun()

# ============================================================
# DELETE CONFIRMATION
# ============================================================

if st.session_state.get("delete_from_detail"):
    st.divider()
    st.markdown(
        f"""
        <div style="
            background-color: #ffebee;
            border-left: 5px solid #c62828;
            border-radius: 8px;
            padding: 1.2rem;
            margin: 1rem 0;
        ">
            <h3 style="color: #c62828; margin: 0;">
                ⚠️ {'ဖျက်ရန် အတည်ပြုပါ' if st.session_state.get('language', 'my') == 'my' else 'Confirm Delete'}
            </h3>
            <p style="color: #c62828; margin: 0.5rem 0 0 0; font-size: 1rem;">
                '<b>{client['name']}</b>' {'နဲ့ ရှင်းတမ်းအားလုံးကို ဖျက်ပါမည်လား?' if st.session_state.get('language', 'my') == 'my' else 'and all statements will be deleted. Are you sure?'}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button(t("delete"), type="primary", use_container_width=True):
            try:
                db.delete_client(client_id)
                st.session_state.pop("selected_client_id", None)
                st.session_state.pop("selected_client_name", None)
                st.session_state["delete_from_detail"] = False
                st.success(f"✓ '{client['name']}' {'ဖျက်ပြီးပါပြီ' if st.session_state.get('language', 'my') == 'my' else 'deleted successfully'}")
                st.switch_page("pages/1_Clients.py")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    with col2:
        if st.button(t("cancel"), use_container_width=True):
            st.session_state["delete_from_detail"] = False
            st.rerun()

# ============================================================
# NOTES SECTION (optional)
# ============================================================

if client.get("notes"):
    st.divider()
    st.markdown(
        f"""
        <h3 style="color: #1f4788; font-size: 1.2rem;">
            📝 {t('notes')}
        </h3>
        """,
        unsafe_allow_html=True,
    )
    st.info(client["notes"])

# ============================================================
# META INFO
# ============================================================

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption(f"📅 {t('created')}: {format_date_mm(client.get('created_at', ''))}")
with col2:
    st.caption(f"🔄 {t('updated')}: {format_date_mm(client.get('updated_at', ''))}")