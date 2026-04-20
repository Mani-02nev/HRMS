import os
import json
from PyPDF2 import PdfReader

RESUME_FOLDER = "data/resumes"
OUT_FILE = "data/resumes.json"

data = []

for file in os.listdir(RESUME_FOLDER):
    if file.endswith(".pdf"):
        path = os.path.join(RESUME_FOLDER, file)

        reader = PdfReader(path)
        text = ""

        data.append({
            "name": file,
            "text": text.lower()
        })

with open(OUT_FILE, "w") as f:
    json.dump(data, f, indent=2)

print("✅ JSON created")