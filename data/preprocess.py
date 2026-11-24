import pandas as pd
from pathlib import Path

# ==============================
# 1. Load dataset
# ==============================

triage_path = (
    "data/raw/mimic-iv-ed-demo-2.2/"
    "mimic-iv-ed-demo-2.2/ed/triage.csv.gz"
)

print("Loading dataset...")

df = pd.read_csv(triage_path)

print("Original shape:", df.shape)


# ==============================
# 2. Remove records without target
# ==============================

df = df.dropna(subset=["acuity"]).copy()

print("After removing missing acuity:", df.shape)


# ==============================
# 3. Convert pain to numeric
# ==============================

df["pain_numeric"] = pd.to_numeric(
    df["pain"],
    errors="coerce"
)

# Keep pain values within valid range
df.loc[
    ~df["pain_numeric"].between(0, 10),
    "pain_numeric"
] = pd.NA


# ==============================
# 4. Select clinical features
# ==============================

features = [
    "temperature",
    "heartrate",
    "resprate",
    "o2sat",
    "sbp",
    "dbp",
    "pain_numeric"
]

X = df[features].copy()


# ==============================
# 5. Handle missing values
# ==============================

for column in X.columns:
    X[column] = X[column].fillna(X[column].median())


# ==============================
# 6. Create emergency priority
# ==============================

# Acuity 1 and 2 = High Priority
# Acuity 3 and 4 = Lower Priority

y = df["acuity"].apply(
    lambda x: 1 if x <= 2 else 0
)


# ==============================
# 7. Create processed dataset
# ==============================

processed = X.copy()

processed["acuity"] = df["acuity"].astype(int)
processed["priority"] = y

output_path = Path(
    "data/processed/triage_processed.csv"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

processed.to_csv(
    output_path,
    index=False
)


# ==============================
# 8. Display results
# ==============================

print("\n===== PREPROCESSING COMPLETE =====")

print("Processed shape:", processed.shape)

print("\n===== FEATURES =====")
print(X.columns.tolist())

print("\n===== PRIORITY DISTRIBUTION =====")
print(y.value_counts())

print("\n===== MISSING VALUES =====")
print(processed.isnull().sum())

print("\nSaved to:")
print(output_path)