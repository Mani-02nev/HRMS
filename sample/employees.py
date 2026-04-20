import streamlit as st
import pandas as pd
from sklearn.linear_model import  LinearRegression


fd = "data/employees.csv"
emp_prog_data="data/employee_progress.csv"

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    try:
        return pd.read_csv(fd)
    except Exception:
        return pd.DataFrame(columns=[
            "id", "name", "department", "role", "email", "phone",
            "joining_date", "salary", "status"
        ])

    


def save_data(df):
    df.to_csv(fd, index=False)
    st.cache_data.clear()

def load_progress():
    try:
        return pd.read_csv(emp_prog_data)
    except Exception:
        return pd.DataFrame()
# -----------------------------
# MAIN FUNCTION (IMPORTANT)
# -----------------------------
def show():
# -----------------------------
# HEADER
 # -----------------------------
    st.markdown("""
            <div style="
                display:flex;
                align-items:center;
                gap:10px;
                border-bottom:1px solid #334155;
                padding-bottom:10px;
                margin-bottom:20px;
            ">
                <i class="fas fa-users" style="color:#60a5fa; font-size:24px;"></i>
                <span style="font-size:26px; font-weight:600; color:white;">
                    Employees
                </span>
            </div>
            """, unsafe_allow_html=True)
    

    df = load_data()
    tab1, tab2 = st.tabs(["Employee List", "Analytics"])

    with tab1:
            
            # -----------------------------
            # KPI CARDS
            # -----------------------------
            col1, col2, col3,col4= st.columns(4)

            col1.metric("Total Employees", len(df))
            col2.metric("Active", len(df[df["status"] == "Active"]))
            col3.metric("Inactive", len(df[df["status"] == "Inactive"]))
            col4.metric("Departments", df["department"].nunique())

            st.markdown("---")

            # -----------------------------
            # FILTERS
            # -----------------------------
            col1, col2 = st.columns(2)

            with col1:
                search = st.text_input("Search Employee")

            with col2:
                dept = st.selectbox(
                    "Department",
                    ["All"] + sorted(df["department"].dropna().astype(str).unique())
                )

            filtered_df = df.copy()

            if search:
                filtered_df = filtered_df[
                    filtered_df["name"].str.contains(search, case=False, na=False)
                ]

            if dept != "All":
                filtered_df = filtered_df[
                    filtered_df["department"] == dept
                ]

            # -----------------------------
            # ADD EMPLOYEE
            # -----------------------------
            st.markdown("### Add Employee")

            with st.expander("Create New Employee", expanded=False):

                with st.form("add_employee_form", clear_on_submit=True):

                    col1, col2 = st.columns(2)

                    with col1:
                        name = st.text_input("Name",placeholder="Enter full name")
                        role = st.selectbox(
                            "Role",
                            ["Developer", "Designer", "Manager", "HR", "Sales", "Finance", "Other"]
                        )
                        department = st.selectbox(
                            "Department",
                            ["IT", "HR", "Finance", "Sales","design","Management","Development","Other"]
                        )

                    with col2:
                        email = st.text_input("Email",placeholder="Enter email address")
                        phone = st.text_input("Phone",placeholder="Enter phone number")
                        salary = st.number_input("Salary", min_value=0, step=1000,value=None,format="%d",placeholder="Enter salary")

                    status = st.selectbox("Status", ["Active", "Inactive"])

                    submit = st.form_submit_button("Add Employee")
                    print(name, role, department, email, phone, salary, status,submit)
                    if submit:
                        if not name or not role:
                            st.warning("Name and Role are required")
                        else:
                            new_id = df["id"].max() + 1 if not df.empty else 1

                            new_row = {
                                "id": new_id,
                                "name": name,
                                "department": department,
                                "role": role,
                                "email": email,
                                "phone": phone,
                                "joining_date": pd.Timestamp.today().date(),
                                "salary": salary,
                                "status": status
                            }

                            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                            save_data(df)

                            st.success("Employee added successfully")
                            st.rerun()

            # -----------------------------
            # TABLE HEADER
            # -----------------------------
            st.markdown("### Employee List")

            # -----------------------------
            # TABLE DISPLAY (CLEAN)
            # -----------------------------
            st.dataframe(
                filtered_df,
                use_container_width=True,
                height=500 ,
                hide_index=True
            )
    with tab2:

        PROG = load_progress().copy()

        if PROG.empty:
            st.warning("No progress data found")
        else:

            # -----------------------------
            # CLEAN DATA
            # -----------------------------
            cols = ["completed_projects","pending_projects","total_projects"]
            PROG[cols] = PROG[cols].apply(pd.to_numeric, errors="coerce").fillna(0)
            PROG["experience_years"] = pd.to_numeric(PROG["experience_years"], errors="coerce").fillna(0)
            PROG["performance_score"] = pd.to_numeric(PROG["performance_score"], errors="coerce").fillna(0)
            PROG["attendance_score"] = pd.to_numeric(PROG["attendance_score"], errors="coerce").fillna(0)

            # -----------------------------
            # ML MODEL 

            X = PROG[cols]
            y = PROG["experience_years"]

            model = LinearRegression()
            model.fit(X, y)

            PROG["predicted_score"] = model.predict(X).round(2)

            # -----------------------------
            # BEST EMPLOYEE
            # -----------------------------
            best_emp = PROG.sort_values("performance_score", ascending=False).iloc[0]

            # -----------------------------
            # PROMOTION EMPLOYEE (BALANCED)
            # -----------------------------
            PROG["promo_score"] = (
                PROG["performance_score"] * 0.4 +
                PROG["attendance_score"] * 0.3 +
                PROG["completed_projects"] * 5
            )

            promo_emp = PROG.sort_values("predicted_score", ascending=False).iloc[0]

            # -----------------------------
            # UI (TOP CARDS)
            # -----------------------------
            col1, col2 = st.columns(2)

            with col1:
                st.success(f"⭐ Best Employee\n\n{best_emp['name']}")

            with col2:
                st.info(f"🚀 Promotion Employee\n\n{promo_emp['name']}")

            st.divider()

            # -----------------------------
            # TABLE
            # -----------------------------
            st.subheader("Employee Analytics")

            st.dataframe(
                PROG[[
                    "name",
                    "performance_score",
                    "attendance_score",
                    "completed_projects",
                    "experience_years",
                    "predicted_score"
                ]].sort_values("performance_score", ascending=False),
                use_container_width=True,
                hide_index=True
            )

            # -----------------------------
            # CHART
            # -----------------------------
           
        
        
        
