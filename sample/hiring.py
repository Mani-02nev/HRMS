import streamlit as st
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FILE = "data/resumes.json"

# -----------------------------
# LOAD JSON (FAST)
# -----------------------------
@st.cache_data
def load_data():
    with open(FILE) as f:
        return pd.DataFrame(json.load(f))

# -----------------------------
# MAIN
# -----------------------------
def show():

    st.markdown("### Hiring System")

    df = load_data()

    if df.empty:
        st.warning("No resumes")
        return

    # -----------------------------
    # DOMAIN SELECT
    # -----------------------------
    domain = st.selectbox("Domain", [
        "Data Science","Software Engineering","HR","Finance","Data Visualization","Product Management"
    ])

    skills = {
        "Data Science":"python sql machine learning",
        "Software Engineering":"java python c++",
        "HR":"recruitment communication",
        "Finance":"accounting excel",
        "Data Visualization":"matplotlib seaborn plotly",
        "Product Management":"roadmap agile leadership"
    }

    job = skills[domain]

    # -----------------------------
    # MATCHING
    # -----------------------------
    texts = df["text"].tolist() + [job]

    vec = TfidfVectorizer()
    X = vec.fit_transform(texts)

    scores = cosine_similarity(X[-1], X[:-1])[0]

    df["Score"] = (scores*100).round(2)
    df = df.sort_values("Score", ascending=False)
    count_hire = st.radio("Show top candidates", [1,3, 5, 10, 20], index=0, horizontal=True)
    

    # -----------------------------
    # UI (CLEAN)
    # -----------------------------
    st.subheader("Top Candidates")

    for i, row in df.head(count_hire).iterrows():
        co1, co2 = st.columns(2)
        with co1:
            st.markdown(f"**{row['name']}**")
        with co2:
            st.markdown(f"<span style='color:#10b981;font-size:18px;'>{row['Score']}%</span>", unsafe_allow_html=True)

    st.divider()

    st.dataframe(df[["name","Score"]], use_container_width=True)