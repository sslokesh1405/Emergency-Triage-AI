import pandas as pd

triage_path = "data/raw/mimic-iv-ed-demo-2.2/mimic-iv-ed-demo-2.2/ed/triage.csv.gz"

print("Loading triage dataset...")

df = pd.read_csv(triage_path)

print("\n===== TRIAGE DATA =====")
print("Rows and Columns:", df.shape)

print("\n===== COLUMNS =====")
print(df.columns.tolist())

print("\n===== FIRST 5 ROWS =====")
print(df.head())

print("\n===== DATA TYPES =====")
print(df.dtypes)

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== TRIAGE ACUITY COUNTS =====")
if "acuity" in df.columns:
    print(df["acuity"].value_counts().sort_index())
else:
    print("Acuity column not found.")

    print("\n===== PAIN VALUES =====")
print(df["pain"].value_counts(dropna=False))

print("\n===== SAMPLE CHIEF COMPLAINTS =====")
print(df["chiefcomplaint"].head(20).to_string(index=False))

print("\n===== ACUITY VS MISSING VALUES =====")
print(df[df["acuity"].isna()][
    ["temperature", "heartrate", "resprate", "o2sat",
     "sbp", "dbp", "pain", "chiefcomplaint"]
].head(20))