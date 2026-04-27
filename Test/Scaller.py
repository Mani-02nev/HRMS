import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

# Sample dataset
data = pd.DataFrame({
    'Price': [100, 150, 200, 250, 300],
    'Weight': [1.2, 1.5, 1.7, 2.0, 2.5]
})

# Standardization
std_scaler = StandardScaler()
print("Standardization:\n", std_scaler.fit_transform(data))

# Min-Max Scaling
mm_scaler = MinMaxScaler()
print("\nMin-Max Scaling:\n", mm_scaler.fit_transform(data))

# Robust Scaling
rob_scaler = RobustScaler()
print("\nRobust Scaling:\n", rob_scaler.fit_transform(data))
