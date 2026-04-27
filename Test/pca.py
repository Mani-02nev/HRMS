import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


data = {
    "Math": [80, 60, 90, 70, 85],
    "Science": [75, 65, 95, 60, 80],
    "English": [70, 55, 85, 65, 75],
    "Tamil": [65, 50, 80, 55, 70]
}

df = pd.DataFrame(data)

print(" Original Data:\n")
print(df)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)


pca = PCA(n_components=2)  
X_pca = pca.fit_transform(X_scaled)


df_pca = pd.DataFrame(X_pca, columns=["PC1", "PC2"])

print("\n PCA Result:\n")
print(df_pca)

# ---------------- STEP 5: IMPORTANCE ----------------
print("\n📌 Explained Variance:")
print(pca.explained_variance_ratio_)