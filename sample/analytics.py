import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA

st.set_page_config(layout="wide")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("data/employees.csv")
edf = pd.read_csv("data/employee_progress.csv")

# ---------------- CLEAN ----------------
df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce')
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
df['Joining_Date'] = pd.to_datetime(df['Joining_Date'], errors='coerce')

df['Salary'].fillna(df['Salary'].mean(), inplace=True)
df['Age'].fillna(df['Age'].median(), inplace=True)
df['status'].fillna("active", inplace=True)

# ---------------- OUTLIER REMOVAL ----------------
Q1 = df['Salary'].quantile(0.25)
Q3 = df['Salary'].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df['Outlier'] = (df['Salary'] < lower) | (df['Salary'] > upper)
df_clean = df[(df['Salary'] >= lower) & (df['Salary'] <= upper)]

# ---------------- MAIN FUNCTION ----------------
def show():

    st.title("🚀 HR Analytics Dashboard")

    # ---------------- KPI ----------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Employees", len(df))
    c2.metric("💰 Avg Salary", int(df['Salary'].mean()))
    c3.metric("🏢 Departments", df['Department'].nunique())
    c4.metric("🌍 Countries", df['Country'].nunique())

    st.markdown("---")

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4, tab5,tab6 = st.tabs([
        "📊 Overview",
        "📈 Performance",
        "📅 Attendance",
        "🏢 Company Analytics",
        "🧠 Data Processing",
        "📉 PCA Analysis"
    ])

    # ================= OVERVIEW =================
    with tab1:
        st.subheader("🏢 Department Analysis")

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            sns.countplot(x="Department", data=df, ax=ax)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            avg_salary = df.groupby("Department")["Salary"].mean().reset_index()
            fig, ax = plt.subplots()
            sns.barplot(x="Department", y="Salary", data=avg_salary, ax=ax)
            plt.xticks(rotation=45)
            st.pyplot(fig)

    # ================= PERFORMANCE =================
    with tab2:
        st.subheader("📈 Employee Performance")

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            sns.histplot(df['Salary'], bins=20, ax=ax)
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots()
            sns.scatterplot(x="Age", y="Salary", hue="Department", data=df, ax=ax)
            st.pyplot(fig)

    # ================= ATTENDANCE =================
    with tab3:
        st.subheader("📅 Employee Status & Outlier Analysis")

        # ---------------- STATUS COUNT ----------------
        col1, col2 = st.columns(2)

        # with col1:
        #     st.markdown("### 📊 Employee Status Count")
        #     fig, ax = plt.subplots()
        #     sns.countplot(x="status", data=df, ax=ax)
        #     st.pyplot(fig)

        # ---------------- OUTLIER SUMMARY ----------------
        with col1:
            st.markdown("### ⚠️ Outlier Summary")
            out_count = df["Outlier"].value_counts()

            st.write("Total Outliers:", int(out_count.get(True, 0)))

        st.markdown("---")

        # ---------------- BOXPLOTS ----------------
        st.subheader("📦 Salary Distribution Analysis")

        col1, col2 = st.columns(2)

        # 🔴 WITH OUTLIERS
        with col1:
            st.markdown("### 🔴 With Outliers")
            fig, ax = plt.subplots()

            sns.boxplot(y=df["Salary"], ax=ax)
            sns.stripplot(y=df[df["Outlier"]]["Salary"], color="red", size=5, ax=ax)

            ax.set_title("Salary Distribution (With Outliers)")
            st.pyplot(fig)

        # 🟢 WITHOUT OUTLIERS
        with col2:
            st.markdown("### 🟢 Without Outliers")
            fig, ax = plt.subplots()

            sns.boxplot(y=df_clean["Salary"], ax=ax)

            ax.set_title("Salary Distribution (Clean Data)")
            st.pyplot(fig)

        st.markdown("---")

        # ---------------- CATEGORY-BASED OUTLIERS ----------------
        st.subheader("📊 Department-wise Outlier Analysis")

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            sns.boxplot(x="Department", y="Salary", data=df, ax=ax)
            plt.xticks(rotation=45)
            ax.set_title("Salary by Department (With Outliers)")
            st.pyplot(fig)
    # ================= COMPANY =================
    with tab4:
        st.subheader("🎯 Performance Score")

        fig, ax = plt.subplots()
        sns.kdeplot(data=edf, x="performance_score", hue="department", ax=ax)
        st.pyplot(fig)

        # ================= DATA PROCESSING =================
    with tab5:
        st.subheader("🧠 Encoding + Scaling + Feature Engineering")

        proc_df = df_clean.copy()

        # -------- RAW DATA --------
        st.write("### 1. Raw Data (Cleaned)")
        st.dataframe(proc_df.head(10))

        # -------- ENCODING + SCALING --------
        categorical = ["Department", "Country"]
        numeric = ["Salary"]   # 👉 Salary மட்டும் scale செய்கிறோம்

        preprocessor = ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", MinMaxScaler(), numeric)
        ])

        X_processed = preprocessor.fit_transform(proc_df[categorical + numeric])

        # Convert to array safely
        X_processed = X_processed.toarray() if hasattr(X_processed, "toarray") else X_processed

        # Column names
        try:
            cat_cols = preprocessor.named_transformers_["cat"].get_feature_names_out(categorical)
            all_cols = list(cat_cols) + numeric
        except:
            all_cols = [f"feature_{i}" for i in range(X_processed.shape[1])]

        df_encoded = pd.DataFrame(X_processed, columns=all_cols)

        st.write("### 2. After Encoding + Scaling (Salary scaled)")
        st.dataframe(df_encoded.head(10))

        # -------- FEATURE ENGINEERING --------
        df_encoded["Salary_Squared"] = df_encoded["Salary"] ** 2
        df_encoded["Salary_Cube"] = df_encoded["Salary"] ** 3

        st.write("### 3. Feature Engineering")
        st.dataframe(df_encoded.head())
    with tab6:
        st.write("### 4. PCA (Dimensionality Reduction)")

        # Apply PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(df_encoded)

        # Convert to DataFrame
        df_pca = pd.DataFrame(X_pca, columns=["PC1", "PC2"])

        # Show data
        st.write("#### PCA Output")
        st.dataframe(df_pca.head(10))

        # -------- Explained Variance --------
        st.write("#### Explained Variance")
        variance = pca.explained_variance_ratio_
        st.write(f"PC1: {round(variance[0]*100,2)}%")
        st.write(f"PC2: {round(variance[1]*100,2)}%")
        st.write(f"Total: {round(sum(variance)*100,2)}%")

        # -------- PCA VISUALIZATION --------
        st.write("### 📊 PCA Visualization (Industry Level)")

        fig, ax = plt.subplots(figsize=(8,6))

        sns.scatterplot(
            x=df_pca["PC1"],
            y=df_pca["PC2"],
            hue=df_clean["Department"],   # grouping
            size=df_clean["Salary"],      # importance
            sizes=(20,200),
            palette="Set2",
            alpha=0.7,
            ax=ax
        )

        # Center lines
        ax.axhline(0, color='gray', linestyle='--')
        ax.axvline(0, color='gray', linestyle='--')

        # Labels
        ax.set_title("PCA - Employee Insights")
        ax.set_xlabel("PC1 (Overall Performance)")
        ax.set_ylabel("PC2 (Skill Variation)")
        ax.grid(True)

        st.pyplot(fig)

        # -------- INSIGHT TEXT --------
        st.info("""
        🧠 PCA Insights:
        - PC1 → Overall employee performance
        - PC2 → Skill differences between employees
        - Clusters → Groups of similar employees
        - Bigger dots → Higher salary employees
        """)
       
    

  