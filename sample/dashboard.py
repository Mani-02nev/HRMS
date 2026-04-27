import streamlit as st
import pandas as pd
import json
def show():

    
    # -----------------------------
    # LOAD DATA
    # -----------------------------
    hr = pd.read_csv("data/hr_progress.csv")

    # -----------------------------
    # HEADER
    # -----------------------------
    st.title("HR Dashboard")

    # -----------------------------
    # KPI (LATEST DAY)
    # -----------------------------
    latest = hr.iloc[-1]

    col1, col2, col3 = st.columns(3)

    col1.metric("New Hires", latest["new_hires"])
    col2.metric("Attendance %", f"{latest['attendance_rate']}%")
    col3.metric("Avg Performance", latest["avg_performance"])

    st.divider()

    # -----------------------------
    # VISUALS (HIGH IMPACT)
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hiring Trend")
        st.line_chart(hr.set_index("date")[["new_hires","resignations"]])

    with col2:
        st.subheader("Attendance Trend")
        st.line_chart(hr.set_index("date")["attendance_rate"])

    st.divider()

    # -----------------------------
    # PERFORMANCE OVERVIEW
    # -----------------------------
    st.subheader("Company Performance Trend")
    st.area_chart(hr.set_index("date")["avg_performance"])

    st.divider()

    # -----------------------------
    # LAST EVENT
    # -----------------------------
    try:
        with open("data/event.json") as f:
            events = json.load(f)
            last_event = events[-1] if events else {}
    except:
        last_event = {}

    if last_event:
        st.markdown(f"""
        <div style="padding:12px; border-radius:10px; background:#1e293b; color:#e2e8f0;">
            📅 <b>{last_event.get("title","Event")}</b><br>
            {last_event.get("start","")} → {last_event.get("end","")}
        </div>
        """, unsafe_allow_html=True)
    