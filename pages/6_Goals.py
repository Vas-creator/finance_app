import streamlit as st
from datetime import date, datetime
from core.db import query_df, execute
from core.utils import mmk

st.set_page_config(page_title="Goals", page_icon="🐷", layout="wide")
st.title("🐷 Savings Goals")
st.caption("ငွေစုဆောင်းမှု ရည်မှန်းချက်တွေ ခြေရာခံ")

# ============ SUMMARY ============
goals = query_df("SELECT * FROM goals ORDER BY id DESC")

total_target = goals["target"].sum() if not goals.empty else 0
total_saved = goals["saved"].sum() if not goals.empty else 0
completed = len(goals[goals["saved"] >= goals["target"]]) if not goals.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("🎯 Goals", len(goals))
c2.metric("💰 စုစုပေါင်း Target", mmk(total_target))
c3.metric("✅ စုပြီး", mmk(total_saved))
c4.metric("🎉 ပြီးမြောက်", f"{completed}/{len(goals)}")

st.divider()

# ============ ADD GOAL ============
with st.expander("➕ Goal အသစ် ထည့်", expanded=False):
    with st.form("add_goal_form", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input("Goal Name *", placeholder="💻 Laptop")
            target = st.number_input(
                "Target (ကျပ်) *", min_value=0.0, step=100000.0
            )

        with c2:
            deadline = st.date_input("Deadline", value=date.today())
            note = st.text_input("Note (optional)")

        submitted = st.form_submit_button("💾 Save", use_container_width=True)

        if submitted:
            if not name.strip() or target <= 0:
                st.error("Name နဲ့ Target ဖြည့်ပါ")
            else:
                execute(
                    """
                    INSERT INTO goals (name, target, saved, deadline, note)
                    VALUES (?,?,0,?,?)
                    """,
                    (name.strip(), target, deadline.isoformat(), note),
                )
                st.success(f"✅ '{name}' ထည့်ပြီး")
                st.rerun()

st.divider()

# ============ GOAL LIST ============
if goals.empty:
    st.info("Goal မရှိသေးဘူး — ➕ နှိပ်ပြီး ထည့်ပါ")
    st.stop()

st.subheader(f"📋 Goals ({len(goals)})")

for _, g in goals.iterrows():
    pct = (g["saved"] / g["target"]) if g["target"] > 0 else 0
    pct = min(pct, 1.0)
    remaining = max(g["target"] - g["saved"], 0)
    is_done = g["saved"] >= g["target"]

    with st.container(border=True):
        c1, c2, c3 = st.columns([4, 2, 2])

        with c1:
            header = f"### {'🎉' if is_done else '🎯'} {g['name']}"
            st.markdown(header)

            # Deadline countdown
            try:
                deadline_date = datetime.fromisoformat(g["deadline"]).date()
                days_left = (deadline_date - date.today()).days
                if is_done:
                    st.caption(f"✅ ပြီးမြောက်ပြီ • Deadline: {g['deadline']}")
                elif days_left < 0:
                    st.caption(f"⚠️ ရက်လွန်နေပြီ • Deadline: {g['deadline']}")
                elif days_left == 0:
                    st.caption(f"🔥 ဒီနေ့ပဲ • Deadline: {g['deadline']}")
                else:
                    st.caption(f"📅 ရက် {days_left} ကျန် • Deadline: {g['deadline']}")
            except (ValueError, TypeError):
                st.caption(f"📅 {g['deadline'] or 'Deadline မရှိ'}")

            if g["note"]:
                st.write(g["note"])

            st.progress(
                pct,
                text=f"{mmk(g['saved'])} / {mmk(g['target'])} ({pct*100:.0f}%)",
            )

        with c2:
            st.metric("စုပြီး", mmk(g["saved"]))
            if is_done:
                st.metric("🎉", "ပြီးပြီ")
            else:
                st.metric("ကျန်", mmk(remaining))

        with c3:
            add_amt = st.number_input(
                "ထည့်မယ့်ငွေ",
                min_value=0.0,
                step=10000.0,
                key=f"amt_{g['id']}",
            )
            ca, cb = st.columns(2)
            if ca.button(
                "➕ ထည့်", key=f"add_{g['id']}", use_container_width=True
            ):
                if add_amt > 0:
                    execute(
                        "UPDATE goals SET saved = saved + ? WHERE id=?",
                        (add_amt, g["id"]),
                    )
                    st.rerun()

            c3a, c3b = st.columns(2)
            if c3a.button(
                "✏️", key=f"edit_goal_{g['id']}", use_container_width=True
            ):
                st.session_state[f"editing_goal_{g['id']}"] = True

            if c3b.button(
                "🗑", key=f"del_goal_{g['id']}", use_container_width=True
            ):
                execute("DELETE FROM goals WHERE id=?", (g["id"],))
                st.rerun()

        # ---------- Edit mode ----------
        if st.session_state.get(f"editing_goal_{g['id']}"):
            with st.form(f"edit_goal_form_{g['id']}"):
                st.markdown("**✏️ Goal ပြင်**")
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_name = st.text_input("Name", value=g["name"])
                    e_target = st.number_input(
                        "Target",
                        min_value=0.0,
                        value=float(g["target"]),
                        step=100000.0,
                    )
                with ec2:
                    e_saved = st.number_input(
                        "စုပြီး",
                        min_value=0.0,
                        value=float(g["saved"]),
                        step=10000.0,
                    )
                    e_note = st.text_input("Note", value=g["note"] or "")

                csave, ccancel = st.columns(2)
                if csave.form_submit_button(
                    "💾 Save", use_container_width=True
                ):
                    execute(
                        """
                        UPDATE goals
                        SET name=?, target=?, saved=?, note=?
                        WHERE id=?
                        """,
                        (e_name, e_target, e_saved, e_note, g["id"]),
                    )
                    st.session_state[f"editing_goal_{g['id']}"] = False
                    st.success("✅ ပြင်ပြီး")
                    st.rerun()
                if ccancel.form_submit_button(
                    "Cancel", use_container_width=True
                ):
                    st.session_state[f"editing_goal_{g['id']}"] = False
                    st.rerun()

st.divider()
st.caption("💡 Goal ပြီးမြောက်ရင် 🎉 ပြတယ်")