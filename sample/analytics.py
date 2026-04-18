import streamlit as st


def show():
    st.markdown("""
<div style="display:flex; align-items:center; gap:10px;">
    <i class="fas fa-chart-bar" style="color:60a5fa; font-size:22px;"></i>
    <span style="font-size:20px; font-weight:600; color:white;">
        Analytics
    </span>
</div>
""", unsafe_allow_html=True)
    st.write("View analytics and reports here.")