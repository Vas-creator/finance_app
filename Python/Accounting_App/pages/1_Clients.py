# pages/1_Clients.py
import streamlit as st
from core import db
from core.utils import format_date_mm, info_box
from core.translations import t

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Clients",
    page_icon="👥",
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
# BUSINESS TYPES
# ============================================================

BUSINESS_TYPES = [
    "ကုန်ထုတ်လုပ်ငန်း (Manufacturing)",
    "အရောင်းအဝယ်လုပ်ငန်း (Trading)",
    "ဝန်ဆောင်မှုလုပ်ငန်း (Service)",
    "လယ်ယာစိုက်ပျိုးရေး (Agriculture)",
    "ဆောက်လုပ်ရေး (Construction)",
    "သယ်ယူပို့ဆောင်ရေး (Transportation)",
    "လက်လီ/လက်ကား (Retail/Wholesale)",
    "အခြား (Others)",
]

# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(f"""
    <div style="padding: 0.5rem 0 1.5rem 0;">
        <h1 style="color: #1f4788; font-size: 2.3rem; margin: 0;">{t('client_management')}</h1>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR — Navigation
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
    
    st.divider()
    
    st.caption(f"👤 {st.session_state.get('name', 'User')}")

# ============================================================
# SESSION STATE INIT
# ============================================================

if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False
if "editing_client_id" not in st.session_state:
    st.session_state.editing_client_id = None
if "delete_confirm_id" not in st.session_state:
    st.session_state.delete_confirm_id = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# ============================================================
# TOP BAR — Search + Add Button (ကော်ဒီနေရာမှာ key ထည့်ပြီး)
# ============================================================

col1, col2, col3 = st.columns([3, 2, 1])

with col1:
    search = st.text_input(
        t('search_placeholder'),
        value=st.session_state.search_query,
        placeholder=t('search_placeholder'),
        label_visibility="collapsed",
        key="search_input",
    )
    st.session_state.search_query = search

with col3:
    if st.button(
        t('add_client'), 
        use_container_width=True, 
        type="primary",
        key="add_client_btn_top" # ⭐ key ထည့်ပြီး
    ):
        st.session_state.show_add_form = True
        st.session_state.editing_client_id = None

# ============================================================
# ADD CLIENT FORM
# ============================================================

if st.session_state.show_add_form:
    with st.form("add_client_form", clear_on_submit=False):
        st.markdown(
            f"""
            <h3 style="color: #1565c0; margin-top: 1rem;">
                {t('add_client')}
            </h3>
            """,
            unsafe_allow_html=True,
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                t('client_name'),
                placeholder="ဥပမာ — ရွှေမြို့တော် ကုမ္ပဏီ" if st.session_state.get("language") == "my" else "e.g. — Shwe Myo Taw Co.",
                key="add_name",
            )
            business_name = st.text_input(
                t('business_name'),
                placeholder="ဥပမာ — ရွှေမြို့တော် လီမိတက်" if st.session_state.get("language") == "my" else "e.g. — Shwe Myo Taw Ltd.",
                key="add_business_name",
            )
            business_type = st.selectbox(
                t('business_type'),
                options=[""] + BUSINESS_TYPES,
                key="add_business_type",
            )
        
        with col2:
            email = st.text_input(
                t('email'),
                placeholder="example@email.com",
                key="add_email",
            )
            fiscal_year_end = st.text_input(
                "ဘဏ္ဍာရေးနှစ် ကုန်ဆုံးရက်" if st.session_state.get("language") == "my" else "Fiscal Year End",
                value="09-30",
                placeholder="MM-DD",
                key="add_fiscal_year_end",
            )
            address = st.text_input(
                t('address'),
                placeholder="ဥပမာ — ရန်ကုန်မြို့" if st.session_state.get("language") == "my" else "e.g. — Yangon",
                key="add_address",
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns([1, 1, 3])
        with col_a:
            submit = st.form_submit_button(
                t('save'),
                use_container_width=True,
                type="primary",
            )
        with col_b:
            cancel = st.form_submit_button(
                t('cancel'),
                use_container_width=True,
            )
        
        if submit:
            if not name or len(name.strip()) < 2:
                st.error("❌ ဖောက်သည် အမည် ဖြည့်ပါ (အနည်းဆုံး ၂ လုံး)" if st.session_state.get("language") == "my" else "❌ Please enter Client Name (min 2 chars)")
            else:
                try:
                    client_id = db.create_client(
                        name=name.strip(),
                        business_name=business_name.strip(),
                        business_type=business_type,
                        email=email.strip(),
                        address=address.strip(),
                        fiscal_year_end=fiscal_year_end.strip() or "09-30",
                    )
                    st.success(f"✓ ဖောက်သည် '{name}' ထည့်ပြီးပါပြီ" if st.session_state.get("language") == "my" else f"✓ Client '{name}' added successfully")
                    st.session_state.show_add_form = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        if cancel:
            st.session_state.show_add_form = False
            st.rerun()
    
    st.divider()

# ============================================================
# EDIT CLIENT FORM
# ============================================================

if st.session_state.editing_client_id is not None:
    client = db.get_client(st.session_state.editing_client_id)
    
    if client:
        with st.form("edit_client_form"):
            st.markdown(
                f"""
                <h3 style="color: #f57c00; margin-top: 1rem;">
                    {t('edit')} — {client['name']}
                </h3>
                """,
                unsafe_allow_html=True,
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    t('client_name'),
                    value=client.get("name", ""),
                    key="edit_name",
                )
                business_name = st.text_input(
                    t('business_name'),
                    value=client.get("business_name", "") or "",
                    key="edit_business_name",
                )
                
                current_type = client.get("business_type", "") or ""
                type_index = 0
                if current_type in BUSINESS_TYPES:
                    type_index = BUSINESS_TYPES.index(current_type) + 1
                business_type = st.selectbox(
                    t('business_type'),
                    options=[""] + BUSINESS_TYPES,
                    index=type_index,
                    key="edit_business_type",
                )
            
            with col2:
                email = st.text_input(
                    t('email'),
                    value=client.get("email", "") or "",
                    key="edit_email",
                )
                fiscal_year_end = st.text_input(
                    "ဘဏ္ဍာရေးနှစ် ကုန်ဆုံးရက်" if st.session_state.get("language") == "my" else "Fiscal Year End",
                    value=client.get("fiscal_year_end", "09-30") or "09-30",
                    key="edit_fiscal_year_end",
                )
                address = st.text_input(
                    t('address'),
                    value=client.get("address", "") or "",
                    key="edit_address",
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns([1, 1, 3])
            with col_a:
                save = st.form_submit_button(
                    t('save'),
                    use_container_width=True,
                    type="primary",
                )
            with col_b:
                cancel = st.form_submit_button(
                    t('cancel'),
                    use_container_width=True,
                )
            
            if save:
                if not name or len(name.strip()) < 2:
                    st.error("❌ ဖောက်သည် အမည် ဖြည့်ပါ" if st.session_state.get("language") == "my" else "❌ Please enter Client Name")
                else:
                    try:
                        db.update_client(
                            st.session_state.editing_client_id,
                            name=name.strip(),
                            business_name=business_name.strip(),
                            business_type=business_type,
                            email=email.strip(),
                            address=address.strip(),
                            fiscal_year_end=fiscal_year_end.strip() or "09-30",
                        )
                        st.success("✓ ပြင်ဆင်ပြီးပါပြီ" if st.session_state.get("language") == "my" else "✓ Updated successfully")
                        st.session_state.editing_client_id = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            
            if cancel:
                st.session_state.editing_client_id = None
                st.rerun()
        
        st.divider()

# ============================================================
# CLIENT LIST
# ============================================================

try:
    all_clients = db.get_all_clients()
except Exception as e:
    st.error(f"Database error: {e}")
    all_clients = []

if st.session_state.search_query:
    q = st.session_state.search_query.lower()
    all_clients = [
        c for c in all_clients
        if q in (c.get("name") or "").lower()
        or q in (c.get("email") or "").lower()
        or q in (c.get("business_name") or "").lower()
    ]

search_info = f'(ရှာဖွေမှု — "{st.session_state.search_query}")' if (st.session_state.search_query and st.session_state.get("language") == "my") else f'(Search — "{st.session_state.search_query}")' if st.session_state.search_query else ''

st.markdown(
    f"""
    <p style="color: #666; font-size: 1rem; margin: 0.5rem 0;">
        {t('total')} <b style="color: #1565c0;">{len(all_clients)}</b> {t('clients')}
        {search_info}
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# EMPTY STATE
# ============================================================

if not all_clients:
    if st.session_state.search_query:
        info_box(
            f"'{st.session_state.search_query}' နဲ့ ကိုက်ညီတဲ့ ဖောက်သည် မတွေ့ပါ" if st.session_state.get("language") == "my" else f"No clients found matching '{st.session_state.search_query}'",
            "warning",
        )
    else:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 3rem 2rem;
                border-radius: 16px;
                text-align: center;
                color: white;
                margin: 2rem 0;
            ">
                <h1 style="font-size: 4rem; margin: 0;">👥</h1>
                <h2 style="margin: 1rem 0 0.5rem 0; font-size: 1.5rem;">
                    {'ဖောက်သည် မရှိသေးပါ' if st.session_state.get('language') == 'my' else 'No clients yet'}
                </h2>
                <p style="opacity: 0.9; font-size: 1rem;">
                    {'➕ ဖောက်သည် အသစ် ကို နှိပ်ပြီး စတင်ပါ' if st.session_state.get('language') == 'my' else 'Click ➕ Add New Client to start'}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.stop()

# ============================================================
# CLIENT CARDS
# ============================================================

for client in all_clients:
    with st.container():
        st.markdown(
            f"""
            <div style="
                background-color: white;
                border: 1px solid #e0e0e0;
                border-left: 5px solid #1565c0;
                border-radius: 8px;
                padding: 1rem 1.2rem;
                margin-bottom: 0.5rem;
            ">
                <h3 style="margin: 0; color: #1f4788; font-size: 1.2rem;">
                    👤 {client['name']}
                </h3>
                <p style="margin: 0.3rem 0 0 0; color: #666; font-size: 0.95rem;">
                    {f'🏢 {client.get("business_name")}' if client.get('business_name') else ''}
                    {f' &nbsp;•&nbsp; 📧 {client.get("email")}' if client.get('email') else ''}
                    {f' &nbsp;•&nbsp; 📍 {client.get("address")}' if client.get('address') else ''}
                </p>
                <p style="margin: 0.3rem 0 0 0; color: #999; font-size: 0.85rem;">
                    {f'💼 {client.get("business_type")}' if client.get('business_type') else ''}
                    &nbsp;•&nbsp; 📅 {'နောက်ဆုံး' if st.session_state.get('language') == 'my' else 'Last'}: {format_date_mm(client.get('updated_at', ''))}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Action buttons (key တွေ အားလုံး သီးခြားစီ ထည့်ထားပါတယ်)
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            if st.button(
                t('details'),
                key=f"detail_{client['id']}",
                use_container_width=True,
            ):
                st.session_state["selected_client_id"] = client["id"]
                st.session_state["selected_client_name"] = client["name"]
                st.switch_page("pages/2_Client_Detail.py")
        
        with col2:
            if st.button(
                t('edit'),
                key=f"edit_{client['id']}",
                use_container_width=True,
            ):
                st.session_state.editing_client_id = client["id"]
                st.session_state.show_add_form = False
                st.rerun()
        
        with col3:
            if st.button(
                t('delete'),
                key=f"del_{client['id']}",
                use_container_width=True,
            ):
                st.session_state.delete_confirm_id = client["id"]
                st.rerun()
        
        with col4:
            if st.button(
                "🏭",
                key=f"quick_mfg_{client['id']}",
                help="ကုန်ထုတ် စာရင်း" if st.session_state.get("language") == "my" else "Manufacturing",
                use_container_width=True,
            ):
                st.session_state["selected_client_id"] = client["id"]
                st.session_state["selected_client_name"] = client["name"]
                st.switch_page("pages/3_Manufacturing.py")
        
        with col5:
            if st.button(
                "📊",
                key=f"quick_bs_{client['id']}",
                help="လက်ကျန်စာရင်း" if st.session_state.get("language") == "my" else "Balance Sheet",
                use_container_width=True,
            ):
                st.session_state["selected_client_id"] = client["id"]
                st.session_state["selected_client_name"] = client["name"]
                st.switch_page("pages/5_Balance_Sheet.py")
        
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# ============================================================
# DELETE CONFIRMATION DIALOG
# ============================================================

if st.session_state.delete_confirm_id is not None:
    client = db.get_client(st.session_state.delete_confirm_id)
    
    if client:
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
                    ⚠️ {'ဖျက်ရန် အတည်ပြုပါ' if st.session_state.get('language') == 'my' else 'Confirm Delete'}
                </h3>
                <p style="color: #c62828; margin: 0.5rem 0 0 0; font-size: 1rem;">
                    '<b>{client['name']}</b>' {'ကို ဖျက်ပါမည်လား? ဒီဖောက်သည်ရဲ့ ရှင်းတမ်းအားလုံးလည်း ပါသွားပါမည်။' if st.session_state.get('language') == 'my' else 'will be deleted along with all its statements. Are you sure?'}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button(t('delete'), type="primary", use_container_width=True, key="confirm_del_btn"):
                try:
                    db.delete_client(st.session_state.delete_confirm_id)
                    st.success(f"✓ '{client['name']}' {'ဖျက်ပြီးပါပြီ' if st.session_state.get('language') == 'my' else 'deleted successfully'}")
                    st.session_state.delete_confirm_id = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        with col2:
            if st.button(t('cancel'), use_container_width=True, key="cancel_del_btn"):
                st.session_state.delete_confirm_id = None
                st.rerun()