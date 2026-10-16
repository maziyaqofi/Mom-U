import pandas as pd

# Load the article source inventory
file_path = "data/raw/Corpus Mom-U.xlsx"

# Read Excel using the second row as the header
df = pd.read_excel(file_path, header=1, usecols="B:F")

# Display dataset information
print("Total articles:", len(df))

print("\nDataset columns:")
print(df.columns.tolist())

print("\nFirst five articles:")
print(df.head())

# Clean article metadata
text_columns = ["Article Title", "Category", "Source", "URL"]

for column in text_columns:
    df[column] = df[column].astype("string").str.strip()

# Create consistent document IDs
df["document_id"] = df["ID"].apply(
    lambda article_id: f"MOMU_{int(article_id):03d}"
)

# Check missing values
print("\nMissing values:")
print(df[["ID"] + text_columns].isna().sum())

# Check duplicate URLs
print("\nDuplicate URLs:", df["URL"].duplicated().sum())

# Display cleaned metadata
print("\nCleaned article metadata:")
print(
    df[["document_id", "Article Title", "Category", "Source"]]
    .head()
    .to_string(index=False)
)