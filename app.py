import streamlit as st
from sample import analytics
from sample import dashboard
from sample import employees
from sample import hiring
from sample import settings
from sample import my_profile 
from sample import cal
st.set_page_config(layout="wide")

# -----------------------------
# 🧠 SESSION STATE (React useState)
# -----------------------------
if 'page' not in st.session_state:
     st.session_state.page = "Dashboard"
if 'user' not in st.session_state:
    st.session_state.user = None
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
""", unsafe_allow_html=True)

# -----------------------------
# 🎨 CUSTOM CSS (Premium Sidebar)
# -----------------------------
st.markdown("""
<style>

/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b);
    padding-top: 20px;
}

/* Sidebar buttons */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    padding: 12px;
    margin: 5px 0;
    background-color: transparent;
    color: #cbd5e1;
    border: none;
    text-align: left;
    font-weight: 500;
    transition: all 0.3s ease;
}

/* Hover */
.stButton > button:hover {
    background-color: #334155;
    color: white;
}

/* Active button */
.active {
    background: linear-gradient(90deg, #2563eb, #1d4ed8) !important;
    color: white !important;
}

/* Title */
.sidebar-title {
    font-size: 20px;
    font-weight: bold;
    color: white;
    padding-left: 10px;
    margin-bottom: 20px;
    font-style: satoshi;
    margin-left: 40px;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
""", unsafe_allow_html=True)


# -----------------------------
# 🧾 SIDEBAR TITLE
# -------------------------------
st.sidebar.markdown('<div class="sidebar-title"><i class="fas fa-users"></i> HRMS</div>', unsafe_allow_html=True)

# -----------------------------
# 🎯 NAVIGATION FUNCTION
# -----------------------------
def nav_button(label):
    if st.sidebar.button(label):
        st.session_state.page = label

    # Apply active style
    if st.session_state.page == label:
        st.sidebar.markdown(
            f'<style>button:contains("{label}") {{background: linear-gradient(90deg, #2563eb, #1d4ed8); color:white;}}</style>',
            unsafe_allow_html=True
        )

nav_button("Dashboard")
nav_button("Employees")
nav_button("Hiring")
nav_button("Analytics")
nav_button("My Profile") 
nav_button("Calendar")

# -----------------------------
# 📊 MAIN CONTENT
# -----------------------------
page = st.session_state.page
if page == "Dashboard":
     dashboard.show()
elif page == "Employees":
    employees.show()
elif page == "Hiring":
    hiring.show()
elif page == "Analytics":
    analytics.show()
elif page == "My Profile": 
     my_profile.show()
elif page == "Calendar":
    cal.show()