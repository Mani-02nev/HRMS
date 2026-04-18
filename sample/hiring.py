import streamlit as st
import os
import pandas as pd
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RESUME_FOLDER = "data/resumes"

# -----------------------------
# FAST PDF → TEXT (CACHED)
# -----------------------------
@st.cache_data
def load_resumes():
    data = []

    for file in os.listdir(RESUME_FOLDER):
        if file.endswith(".pdf"):
            path = os.path.join(RESUME_FOLDER, file)

            reader = PdfReader(path)
            text = ""

            for page in reader.pages:
                text += page.extract_text() or ""

            data.append({
                "name": file,
                "text": text.lower()
            })

    return pd.DataFrame(data)

# -----------------------------
# MAIN UI
# -----------------------------
def show():

    st.title("Hiring System")

    # Load once (fast after first run)
    resumes_df = load_resumes()

    if resumes_df.empty:
        st.warning("No resumes found")
        return

    # -----------------------------
    # JOB INPUT
    # -----------------------------
    domain = st.selectbox("Select Job Domain", ["Data Science", "Software Engineering", "Product Management", "Design", "Marketing", "Sales", "DevOps", "HR", "Finance"])
    skildb={
        "Data Science":"python sql machine learning deep learning statistics",
        "Software Engineering":"java python c++ software development",
        "Product Management":"product management agile scrum leadership",
        "Design":"graphic design adobe photoshop creativity",
        "Marketing":"digital marketing seo content marketing social media",
        "Sales":"sales communication negotiation crm",
        "DevOps":"devops docker kubernetes ci/cd aws",
        "HR":"human resources recruitment employee relations",
        "Finance":"finance accounting financial analysis excel"}

    job_desc = skildb.get(domain, "")

    if not job_desc:
        st.info("Enter job skills to start matching")
        return

    # -----------------------------
    # MATCHING (FAST)
    # -----------------------------
    texts = resumes_df["text"].tolist() + [job_desc.lower()]

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(texts)

    scores = cosine_similarity(vectors[-1], vectors[:-1])[0]

    resumes_df["Score"] = (scores * 100).round(2)

    # Sort
    results = resumes_df.sort_values(by="Score", ascending=False)

    # -----------------------------
    # UI OUTPUT
    # -----------------------------
    st.subheader("Top Candidates")

    # Top 3 highlight
    top3 = results.head(3)

    cols = st.columns(3)
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
           st.markdown(f"""
           <div style="background: linear-gradient(90deg, #2563eb, #1d4ed8); padding: 10px; border-radius: 5px; color:white;">
               <h4>{row['name']}</h4>
               <p>Match Score: {row['Score']}%</p>
           </div>
           """, unsafe_allow_html=True)

    st.divider()

    # Full table
    st.dataframe(
        results[["name", "Score"]],
        use_container_width=True
    )