import streamlit as st
import pandas as pd
import json
EDF= pd.read_csv("data/employees.csv")
PROG=pd.read_csv("data/employee_progress.csv")
ATT=pd.read_csv("data/attendance.csv")

def show():
    st.title("Analytics")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Employee Performance Prediction")
        st.bar_chart(PROG.set_index("name")["predicted_score"])
    with c2:
        st.subheader("Attendance Score")
        st.bar_chart(PROG.set_index("name")["attendance_score"])
    st.divider()
    st.subheader("Employee Details")
    c1, c2 = st.columns(2)
    with c1:
        st.line_chart(EDF.set_index("name")["experience_years"])
    with c2:
        st.line_chart(EDF.set_index("name")["performance_score"])

    