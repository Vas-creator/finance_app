import streamlit as st
from core.db import query_df, execute
from core.utils import mmk, recalc_account_balances

st.set_page_config(page_title="Accounts", page_icon="🏦", layout="wide")
st.title("🏦 Accounts")
st.caption("ငွေ ဘယ်နေရာမှာ ဘယ်လောက် ရှိလဲ")

# ============ SUMMARY ============
accounts = query_df("SELECT id, name, type, balance FROM accounts")
total = accounts["balance"].sum() if not accounts.empty else 0

c1, c2 = st.columns(2)
c1.metric("📦 Account အရေအတွက်", len(accounts))
c2.metric("💰 စုစုပေါင်း Balance", mmk(total))

st.divider()

# ============ ADD ACCOUNT ============
with st.expander("➕ Account အသစ် ထည့်", expanded=False):
    with st.form("add_account_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Account Name *", placeholder="KBZ Bank")
            atype = st.selectbox(
                "Type",
                ["cash", "bank", "wallet", "credit"],
                format_func=lambda x: {
                    "cash": "💵 Cash",
                    "bank": "🏦 Bank",
                    "wallet": "📱 Wallet",
                    "credit": "💳 Credit",
                }[x],
            )

        with col2:
            initial = st.number_input(
                "Initial Balance (ကျပ်)",
                min_value=0.0,
                step=10000.0,
                help="Account ရဲ့ လက်ရှိ ငွေ",
            )
            note = st.text_input("Note (optional)")

        submitted = st.form_submit_button("💾 Save", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Account name ဖြည့်ပါ")
            else:
                # Duplicate check
                existing = query_df(
                    "SELECT id FROM accounts WHERE name=?", (name.strip(),)
                )
                if not existing.empty:
                    st.error(f"'{name}' ဆိုတဲ့ account ရှိပြီးသား")
                else:
                    execute(
                        "INSERT INTO accounts (name, type, balance) VALUES (?,?,?)",
                        (name.strip(), atype, initial),
                    )
                    st.success(f"✅ '{name}' ထည့်ပြီး")
                    st.rerun()

st.divider()

# ============ ACCOUNT LIST ============
if accounts.empty:
    st.info("Account မရှိသေးဘူး — အပေါ်က ➕ နှိပ်ပြီး ထည့်ပါ")
    st.stop()

st.subheader("📋 Account စာရင်း")

TYPE_ICON = {
    "cash": "💵",
    "bank": "🏦",
    "wallet": "📱",
    "credit": "💳",
}

for _, acc in accounts.iterrows():
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 2])

        with c1:
            icon = TYPE_ICON.get(acc["type"], "💼")
            st.markdown(f"### {icon} {acc['name']}")
            st.caption(f"`{acc['type']}`")

        with c2:
            st.metric("Balance", mmk(acc["balance"]))

        with c3:
            c3a, c3b, c3c = st.columns(3)

            if c3a.button("✏️", key=f"edit_{acc['id']}", use_container_width=True):
                st.session_state[f"editing_acc_{acc['id']}"] = True

            if c3b.button("💰", key=f"adj_{acc['id']}", use_container_width=True):
                st.session_state[f"adjusting_acc_{acc['id']}"] = True

            if c3c.button("🗑", key=f"del_{acc['id']}", use_container_width=True):
                st.session_state[f"deleting_acc_{acc['id']}"] = True

        # ---------- Edit mode ----------
        if st.session_state.get(f"editing_acc_{acc['id']}"):
            with st.form(f"edit_form_{acc['id']}"):
                st.markdown("**✏️ Account ပြင်**")
                new_name = st.text_input("Name", value=acc["name"])
                new_type = st.selectbox(
                    "Type",
                    ["cash", "bank", "wallet", "credit"],
                    index=["cash", "bank", "wallet", "credit"].index(acc["type"]),
                )

                csave, ccancel = st.columns(2)
                if csave.form_submit_button("💾 Save", use_container_width=True):
                    execute(
                        "UPDATE accounts SET name=?, type=? WHERE id=?",
                        (new_name.strip(), new_type, acc["id"]),
                    )
                    st.session_state[f"editing_acc_{acc['id']}"] = False
                    st.success("✅ ပြင်ပြီး")
                    st.rerun()
                if ccancel.form_submit_button("Cancel", use_container_width=True):
                    st.session_state[f"editing_acc_{acc['id']}"] = False
                    st.rerun()

        # ---------- Adjust balance mode ----------
        if st.session_state.get(f"adjusting_acc_{acc['id']}"):
            with st.form(f"adjust_form_{acc['id']}"):
                st.markdown("**💰 Balance ပြင် (manual adjust)**")
                st.caption(
                    f"လက်ရှိ: **{mmk(acc['balance'])}** — "
                    "တကယ်ရှိတဲ့ ငွေကို ရိုက်ထည့်ပါ"
                )

                new_balance = st.number_input(
                    "တကယ်ရှိတဲ့ ငွေ (ကျပ်)",
                    value=float(acc["balance"]),
                    step=10000.0,
                    help="Credit/overdraft ဆို အနုတ် ရိုက်လို့ရ",
                )

                csave, ccancel = st.columns(2)
                if csave.form_submit_button("💾 Save", use_container_width=True):
                    execute(
                        "UPDATE accounts SET balance=? WHERE id=?",
                        (new_balance, acc["id"]),
                    )
                    st.session_state[f"adjusting_acc_{acc['id']}"] = False
                    st.success("✅ ပြင်ပြီး")
                    st.rerun()
                if ccancel.form_submit_button("Cancel", use_container_width=True):
                    st.session_state[f"adjusting_acc_{acc['id']}"] = False
                    st.rerun()

        # ---------- Delete mode ----------
        if st.session_state.get(f"deleting_acc_{acc['id']}"):
            with st.form(f"del_form_{acc['id']}"):
                st.warning(f"⚠️ **'{acc['name']}'** ကို ဖျက်မှာ သေချာလား?")

                txn_count = query_df(
                    "SELECT COUNT(*) AS n FROM transactions WHERE account_id=?",
                    (acc["id"],),
                )["n"][0]

                if txn_count > 0:
                    st.error(
                        f"⚠️ ဒီ account မှာ transaction **{txn_count} ခု** ရှိတယ်။ "
                        "ဖျက်ရင် transaction တွေပါ ပျက်သွားမယ်။"
                    )

                c_yes, c_no = st.columns(2)

                if c_yes.form_submit_button(
                    "🗑 ဖျက်", use_container_width=True, type="primary"
                ):
                    execute("DELETE FROM transactions WHERE account_id=?", (acc["id"],))
                    execute("DELETE FROM accounts WHERE id=?", (acc["id"],))
                    recalc_account_balances()
                    st.session_state[f"deleting_acc_{acc['id']}"] = False
                    st.success("🗑 ဖျက်ပြီး")
                    st.rerun()

                if c_no.form_submit_button("Cancel", use_container_width=True):
                    st.session_state[f"deleting_acc_{acc['id']}"] = False
                    st.rerun()

st.divider()
st.caption("💡 Account balance ကို transaction ထည့်တိုင်း auto update ဖြစ်တယ်")