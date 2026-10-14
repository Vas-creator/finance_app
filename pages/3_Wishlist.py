import streamlit as st
from datetime import date
from core.db import query_df, execute
from core.utils import mmk

st.set_page_config(page_title="Wishlist", page_icon="🛍", layout="wide")
st.title("🛍 Wish List")
st.caption("ဝယ်ချင်တာတွေ စုစည်းထားပြီး ဆုံးဖြတ်ချက် ချနိုင်ဖို့")

# ============ ADD FORM ============
with st.expander("➕ ဝယ်ချင်တာ ထည့်", expanded=False):
    with st.form("wish_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("ပစ္စည်းအမည် *", placeholder="နာရီ")
        price = c2.number_input("စျေး (ကျပ်) *", min_value=0.0, step=10000.0)
        priority = c3.selectbox(
            "ဦးစားပေး",
            ["low", "medium", "high"],
            index=1,
            format_func=lambda x: {
                "low": "🟢 Low",
                "medium": "🟡 Medium",
                "high": "🔴 High",
            }[x],
        )

        c4, c5, c6 = st.columns(3)
        category = c4.selectbox(
            "အမျိုးအစား",
            ["Electronics", "Fashion", "Home", "Health", "Education", "Other"],
        )
        target_date = c5.date_input("ဝယ်ချင်တဲ့ရက်", value=date.today())
        url = c6.text_input("Link (optional)")

        note = st.text_area("မှတ်ချက်", height=70)

        if st.form_submit_button("💾 သိမ်း", use_container_width=True):
            if not name.strip() or price <= 0:
                st.error("အမည်နဲ့ စျေး ဖြည့်ပါ")
            else:
                execute(
                    """
                    INSERT INTO wishlist
                        (name, price, priority, category, url, note, target_date)
                    VALUES (?,?,?,?,?,?,?)
                    """,
                    (
                        name.strip(),
                        price,
                        priority,
                        category,
                        url,
                        note,
                        target_date.isoformat(),
                    ),
                )
                st.success("✅ သိမ်းပြီးပါပြီ")
                st.rerun()

st.divider()

# ============ FILTERS ============
c1, c2 = st.columns(2)
with c1:
    status_filter = st.multiselect(
        "Status",
        ["considering", "saving", "bought", "skipped"],
        default=["considering", "saving"],
        format_func=lambda x: {
            "considering": "🤔 စဉ်းစားနေဆဲ",
            "saving": "💰 ငွေစုနေဆဲ",
            "bought": "✅ ဝယ်ပြီး",
            "skipped": "❌ မဝယ်တော့",
        }[x],
    )
with c2:
    sort_by = st.selectbox(
        "စီရန်",
        ["ဦးစားပေး", "စျေးကြီး→ငယ်", "စျေးငယ်→ကြီး", "အသစ်ဆုံး"],
    )

# ============ QUERY ============
df = query_df("SELECT * FROM wishlist")
if df.empty:
    st.info("ဝယ်ချင်တာ မရှိသေးဘူး။ ➕ နှိပ်ပြီး ထည့်ပါ။")
    st.stop()

df = df[df["status"].isin(status_filter)]

if df.empty:
    st.warning("Filter နဲ့ ကိုက်တာ မရှိဘူး")
    st.stop()

if sort_by == "ဦးစားပေး":
    order = {"high": 0, "medium": 1, "low": 2}
    df = df.sort_values("priority", key=lambda s: s.map(order))
elif sort_by == "စျေးကြီး→ငယ်":
    df = df.sort_values("price", ascending=False)
elif sort_by == "စျေးငယ်→ကြီး":
    df = df.sort_values("price")
else:
    df = df.sort_values("id", ascending=False)

# ============ SUMMARY ============
c1, c2, c3 = st.columns(3)
c1.metric("📦 အရေအတွက်", len(df))
c2.metric("💰 စုစုပေါင်းတန်ဖိုး", mmk(df["price"].sum()))
c3.metric(
    "🔥 High Priority",
    mmk(df[df["priority"] == "high"]["price"].sum()),
)

st.divider()

# ============ CARDS ============
PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}
STATUS_ICON = {
    "considering": "🤔",
    "saving": "💰",
    "bought": "✅",
    "skipped": "❌",
}
STATUS_LABEL = {
    "considering": "စဉ်းစားနေဆဲ",
    "saving": "ငွေစုနေဆဲ",
    "bought": "ဝယ်ပြီး",
    "skipped": "မဝယ်တော့ဘူး",
}

for _, row in df.iterrows():
    with st.container(border=True):
        c1, c2, c3 = st.columns([4, 2, 2])

        with c1:
            st.markdown(f"### {PRIORITY_ICON[row['priority']]} {row['name']}")
            st.caption(
                f"`{row['category']}`  •  "
                f"{STATUS_ICON[row['status']]} {STATUS_LABEL[row['status']]}  •  "
                f"🎯 {row['target_date']}"
            )
            if row["note"]:
                st.write(row["note"])
            if row["url"]:
                st.markdown(f"[🔗 Link]({row['url']})")

        with c2:
            st.metric("စျေး", mmk(row["price"]))

        with c3:
            new_status = st.selectbox(
                "Status ပြောင်း",
                ["considering", "saving", "bought", "skipped"],
                index=["considering", "saving", "bought", "skipped"].index(
                    row["status"]
                ),
                key=f"st_{row['id']}",
                format_func=lambda x: {
                    "considering": "🤔 စဉ်းစားနေဆဲ",
                    "saving": "💰 စုနေဆဲ",
                    "bought": "✅ ဝယ်ပြီး",
                    "skipped": "❌ မဝယ်တော့",
                }[x],
            )
            if new_status != row["status"]:
                if new_status == "bought":
                    execute(
                        """
                        UPDATE wishlist
                        SET status=?, bought_date=?,
                            actual_price=COALESCE(actual_price, price)
                        WHERE id=?
                        """,
                        (new_status, date.today().isoformat(), row["id"]),
                    )
                else:
                    execute(
                        "UPDATE wishlist SET status=? WHERE id=?",
                        (new_status, row["id"]),
                    )
                st.rerun()

            c3a, c3b = st.columns(2)

            if c3a.button(
                "✏️", key=f"edit_{row['id']}", use_container_width=True
            ):
                st.session_state[f"editing_wish_{row['id']}"] = True

            if c3b.button(
                "🗑", key=f"del_{row['id']}", use_container_width=True
            ):
                execute("DELETE FROM wishlist WHERE id=?", (row["id"],))
                st.rerun()

        # ---------- Edit mode ----------
        if st.session_state.get(f"editing_wish_{row['id']}"):
            with st.form(f"edit_wish_{row['id']}"):
                st.markdown("**✏️ ပြင်**")
                e_name = st.text_input("အမည်", value=row["name"])
                e_price = st.number_input(
                    "စျေး",
                    min_value=0.0,
                    value=float(row["price"]),
                    step=10000.0,
                )
                e_note = st.text_area("မှတ်ချက်", value=row["note"] or "")

                csave, ccancel = st.columns(2)
                if csave.form_submit_button(
                    "💾 Save", use_container_width=True
                ):
                    execute(
                        "UPDATE wishlist SET name=?, price=?, note=? WHERE id=?",
                        (e_name, e_price, e_note, row["id"]),
                    )
                    st.session_state[f"editing_wish_{row['id']}"] = False
                    st.success("✅ ပြင်ပြီး")
                    st.rerun()
                if ccancel.form_submit_button(
                    "Cancel", use_container_width=True
                ):
                    st.session_state[f"editing_wish_{row['id']}"] = False
                    st.rerun()