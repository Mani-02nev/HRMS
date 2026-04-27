# Demonstrating different encoding methods on a small dataset
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder

# Step 1: Sample dataset
data = pd.DataFrame({
    'Color': ['Red', 'Blue', 'Green', 'Red', 'Blue'],
    'Size': ['S', 'M', 'L', 'XL', 'M']
})
print('Original Data:\n', data)

# Step 2: Label Encoding
label_enc = LabelEncoder()
data['Color_Label'] = label_enc.fit_transform(data['Color'])
print('\nLabel Encoding:\n', data[['Color', 'Color_Label']])

# Step 3: One-Hot Encoding
onehot = pd.get_dummies(data['Size'], prefix='Size')
print('\nOne-Hot Encoding:\n', onehot)

# Step 4: Ordinal Encoding (define order for Size)
ord_enc = OrdinalEncoder(categories=[['S', 'M', 'L', 'XL']])
data['Size_Ordinal'] = ord_enc.fit_transform(data[['Size']])
print('\nOrdinal Encoding:\n', data[['Size', 'Size_Ordinal']])

# Step 5: Frequency Encoding
frequency_map = data['Color'].value_counts().to_dict()
print('\nFrequency Map for Color:\n', frequency_map)
data['Color_Freq'] = data['Color'].map(frequency_map)
print('\nFrequency Encoding:\n', data[['Color', 'Color_Freq']])

data = pd.concat([data, onehot ], axis=1)
print('\nFinal Data with All Encodings:\n', data)