import streamlit as st
import pandas as pd

fd = "data/employees.csv"

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv(fd)


def save_data(df):
    df.to_csv(fd, index=False)
    st.cache_data.clear()


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
                    ["All"] + sorted(df["department"].unique())
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
                            ["IT", "HR", "Finance", "Sales"]
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
                height=500
            )
    with tab2:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <i class="fas fa-chart-bar" style="color:60a5fa; font-size:22px;"></i>
            <span style="font-size:20px; font-weight:600; color:white;">
                Analytics
            </span>
        </div>
        """, unsafe_allow_html=True)
