import streamlit as st
import pandas as pd
from datetime import datetime
import random

EMP_FILE = "data/employees.csv"
ATT_FILE = "data/attendance.csv"


def load_employees():
    return pd.read_csv(EMP_FILE)


def load_attendance():
    try:
        df = pd.read_csv(ATT_FILE)
        df["date"] = df["date"].astype(str)
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "name", "date", "check_in", "check_out", "status", "hours"])


def save_attendance(df):
    df.to_csv(ATT_FILE, index=False)


def get_today_record(att_df, emp_id):
    today = str(datetime.now().date())
    rows = att_df[(att_df["id"] == emp_id) & (att_df["date"] == today)]
    if rows.empty:
        return None, None
    idx = rows.index[-1]
    return idx, att_df.loc[idx]


def show():
    # ── Custom CSS ──────────────────────────────────────────────
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

        .profile-card {
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
            border-radius: 16px; padding: 24px; color: white;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .emp-name { font-size: 22px; font-weight: 600; margin: 0; }
        .emp-meta { font-size: 13px; opacity: 0.6; margin: 4px 0 8px; }
        .emp-contact { font-size: 13px; opacity: 0.75; }

        .status-badge {
            display: inline-block; padding: 4px 14px;
            border-radius: 99px; font-size: 13px; font-weight: 500;
        }
        .badge-in  { background:#fef3c7; color:#92400e; }
        .badge-out { background:#d1fae5; color:#065f46; }
        .badge-no  { background:#fee2e2; color:#991b1b; }

        .att-row {
            background: #f8fafc; border-radius: 10px;
            padding: 10px 14px; margin-bottom: 8px;
            border-left: 4px solid #6366f1;
            font-size: 13px; color: #334155;
        }
        .att-row b { color: #1e293b; }

        div[data-testid="stButton"] > button {
            border-radius: 10px; font-weight: 500;
            height: 46px; font-size: 15px;
            transition: all 0.2s;
        }
    </style>
    """, unsafe_allow_html=True)

    # ── Load data ────────────────────────────────────────────────
    emp_df = load_employees()
    if emp_df.empty:
        st.warning("No employee data found.")
        return

    emp = emp_df.iloc[0]

    if "avatar_seed" not in st.session_state:
        st.session_state.avatar_seed = random.randint(1, 100000)

    # ── Profile card ─────────────────────────────────────────────
    st.markdown(
    '<h3><i class="fas fa-user" style="margin-right:8px;"></i>My Profile</h3>',
    unsafe_allow_html=True
)
    col_img, col_info = st.columns([1, 3])

    with col_img:
        st.image(
            f"https://api.dicebear.com/7.x/adventurer/png?seed={st.session_state.avatar_seed}",
            width=110
        )
    with col_info:
        st.markdown(f"""
        <div class="profile-card">
            <p class="emp-name">{emp['name']}</p>
            <p class="emp-meta">{emp['role']} &bull; {emp['department']}</p>
            <p class="emp-contact">📧 {emp['email']}<br>📞 {emp['phone']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Attendance state ─────────────────────────────────────────
    att_df = load_attendance()                          # always fresh read
    today = str(datetime.now().date())
    now_time = datetime.now().strftime("%H:%M:%S")

    idx, record = get_today_record(att_df, emp["id"])

    checked_in  = record is not None
    checked_out = checked_in and str(record["check_out"]).strip() not in ("", "nan")

    # ── Action buttons ───────────────────────────────────────────
    st.subheader("⏱ Attendance")
    c1, c2 = st.columns(2)

    if c1.button("🟢 Check In", disabled=checked_in, use_container_width=True):
        new_row = {
            "id": emp["id"], "name": emp["name"], "date": today,
            "check_in": now_time, "check_out": "", "status": "Present", "hours": ""
        }
        att_df = pd.concat([att_df, pd.DataFrame([new_row])], ignore_index=True)
        save_attendance(att_df)
        st.success(f"✅ Checked In at {now_time}")
        st.rerun()

    if c2.button("🔴 Check Out", disabled=(not checked_in or checked_out), use_container_width=True):
        t1 = datetime.strptime(att_df.loc[idx, "check_in"], "%H:%M:%S")
        t2 = datetime.strptime(now_time, "%H:%M:%S")
        hours = str(t2 - t1)

        att_df.loc[idx, "check_out"] = now_time
        att_df.loc[idx, "hours"]     = hours
        save_attendance(att_df)
        st.success(f"✅ Checked Out at {now_time}  |  Worked: {hours}")
        st.rerun()

    # ── Status badge ─────────────────────────────────────────────
    if not checked_in:
        st.markdown('<span class="status-badge badge-no">⛔ Not Checked In</span>', unsafe_allow_html=True)
    elif not checked_out:
        ci = att_df.loc[idx, "check_in"]
        st.markdown(f'<span class="status-badge badge-in">🟡 Checked In at {ci}</span>', unsafe_allow_html=True)
    else:
        ci = att_df.loc[idx, "check_in"]
        co = att_df.loc[idx, "check_out"]
        hrs = att_df.loc[idx, "hours"]
        st.markdown(f'<span class="status-badge badge-out">✅ {ci} → {co} ({hrs})</span>', unsafe_allow_html=True)

    st.divider()

    # ── History ───────────────────────────────────────────────────
    st.subheader("📅 Attendance History")
    history = att_df[att_df["id"] == emp["id"]].sort_values("date", ascending=False)

    if history.empty:
        st.info("No attendance records found.")
    else:
       st.dataframe(history[["date", "check_in", "check_out", "status", "hours"]].reset_index(drop=True), hide_index=True)