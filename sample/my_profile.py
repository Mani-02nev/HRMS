import streamlit as st
import pandas as pd
from datetime import datetime
import random

EMP_FILE = "data/employees.csv"
ATT_FILE = "data/attendance.csv"

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_employees():
    return pd.read_csv(EMP_FILE)

@st.cache_data
def load_attendance():
    try:
        return pd.read_csv(ATT_FILE)
    except:
        return pd.DataFrame(columns=["id","name","date","check_in","check_out","status"])

def save_attendance(df):
    df.to_csv(ATT_FILE, index=False)
    st.cache_data.clear()


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def show():

    df = load_employees()

    if df.empty:
        st.warning("No employee data found")
        return

    # 👉 simple demo user (first row)
    emp = df.iloc[0]

    # -----------------------------
    # PROFILE
    # -----------------------------
    st.title("My Profile")

    col1, col2 = st.columns([1, 3])

    with col1:
     st.image(
        f"https://api.dicebear.com/7.x/adventurer/png?seed={random.randint(1,100000)}",
        width=120
    )
     print("rendering image")
    with col2:
        st.subheader(emp["name"])
        st.write(f"Role: {emp['role']}")
        st.write(f"Department: {emp['department']}")
        st.write(f"Email: {emp['email']}")
        st.write(f"Phone: {emp['phone']}")

    st.divider()

    # -----------------------------
    # ATTENDANCE
    # -----------------------------
    st.subheader("Attendance")

    att_df = load_attendance()

    today = datetime.now().date()
    now_time = datetime.now().strftime("%H:%M:%S")

    today_data = att_df[
        (att_df["id"] == emp["id"]) &
        (att_df["date"] == str(today))
    ]

    col1, col2 = st.columns(2)

    # ✅ CHECK-IN
    if col1.button("Check In"):
        if not today_data.empty:
            st.warning("Already checked in today")
        else:
            new_row = {
                "id": emp["id"],
                "name": emp["name"],
                "date": today,
                "check_in": now_time,
                "check_out": "",
                "status": "Present"
            }
            att_df = pd.concat([att_df, pd.DataFrame([new_row])], ignore_index=True)
            save_attendance(att_df)
            st.success("Checked In")
            st.rerun()

    # ✅ CHECK-OUT (ONLY ONCE)
    if col2.button("Check Out"):
        if today_data.empty:
            st.warning("Check in first")
        else:
            index = today_data.index[0]

            # already checked out?
            if str(att_df.loc[index, "check_out"]) != "":
                st.error("Already checked out today")
            else:
                att_df.loc[index, "check_out"] = now_time
                save_attendance(att_df)
                st.success("Checked Out")
                st.rerun()

    st.divider()

    # -----------------------------
    # STATUS
    # -----------------------------
    if today_data.empty:
        st.info("Status: Not Checked In")
    else:
        index = today_data.index[0]
        if str(att_df.loc[index, "check_out"]) == "":
            st.warning("Status: Checked In")
        else:
            st.success("Status: Completed")

    # -----------------------------
    # HISTORY
    # -----------------------------
    st.subheader("Attendance History")

    user_att = att_df[att_df["id"] == emp["id"]]

    st.dataframe(user_att, use_container_width=True)