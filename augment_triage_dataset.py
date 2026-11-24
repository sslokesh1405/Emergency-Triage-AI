import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

INPUT_PATH = Path(
    "data/processed/triage_processed.csv"
)

OUTPUT_PATH = Path(
    "data/processed/triage_augmented.csv"
)

TARGET_ROWS = 2000

RANDOM_STATE = 42


# Features used by the Random Forest model

FEATURES = [
    "temperature",
    "heartrate",
    "resprate",
    "o2sat",
    "sbp",
    "dbp",
    "pain_numeric"
]


# Reasonable ranges

LIMITS = {

    "temperature": (35.0, 42.0),

    "heartrate": (30.0, 220.0),

    "resprate": (6.0, 50.0),

    "o2sat": (70.0, 100.0),

    "sbp": (60.0, 220.0),

    "dbp": (30.0, 140.0),

    "pain_numeric": (0.0, 10.0)
}


# Small variations added to original values

NOISE_STD = {

    "temperature": 0.25,

    "heartrate": 4.0,

    "resprate": 1.0,

    "o2sat": 0.6,

    "sbp": 6.0,

    "dbp": 4.0,

    "pain_numeric": 0.7
}


# ============================================================
# CLEAN DATASET
# ============================================================

def clean_dataset(df):

    print("\nChecking dataset...")

    required_columns = FEATURES + ["priority"]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns: "
            + ", ".join(missing)
        )

    df = df.copy()


    # Convert features to numbers

    for column in FEATURES:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


    # Convert priority to numeric

    df["priority"] = pd.to_numeric(
        df["priority"],
        errors="coerce"
    )


    # Keep only 0 and 1

    df = df[
        df["priority"].isin([0, 1])
    ]


    # Remove invalid rows

    df = df.dropna(
        subset=FEATURES + ["priority"]
    )


    # Make priority integer

    df["priority"] = df[
        "priority"
    ].astype(int)


    # Clamp values

    for column, limits in LIMITS.items():

        minimum, maximum = limits

        df[column] = df[column].clip(
            minimum,
            maximum
        )


    return df.reset_index(drop=True)


# ============================================================
# GENERATE SYNTHETIC DATA
# ============================================================

def generate_synthetic_rows(
    source_df,
    number_of_rows,
    rng
):

    generated = []


    # Split original data by priority

    low_df = source_df[
        source_df["priority"] == 0
    ]

    high_df = source_df[
        source_df["priority"] == 1
    ]


    print("\nOriginal classes:")

    print(
        "Lower Priority (0):",
        len(low_df)
    )

    print(
        "High Priority (1):",
        len(high_df)
    )


    if len(low_df) == 0:

        raise ValueError(
            "No priority 0 rows found."
        )


    if len(high_df) == 0:

        raise ValueError(
            "No priority 1 rows found."
        )


    # Keep synthetic data balanced

    low_count = number_of_rows // 2

    high_count = (
        number_of_rows
        - low_count
    )


    # ========================================================
    # LOWER PRIORITY
    # ========================================================

    low_indices = rng.integers(
        0,
        len(low_df),
        size=low_count
    )

    low_rows = low_df.iloc[
        low_indices
    ].copy().reset_index(drop=True)


    for feature in FEATURES:

        noise = rng.normal(
            0,
            NOISE_STD[feature],
            size=low_count
        )

        low_rows[feature] = (
            low_rows[feature]
            + noise
        )

        minimum, maximum = LIMITS[
            feature
        ]

        low_rows[feature] = (
            low_rows[feature]
            .clip(
                minimum,
                maximum
            )
        )


    low_rows["priority"] = 0

    generated.append(low_rows)


    # ========================================================
    # HIGH PRIORITY
    # ========================================================

    high_indices = rng.integers(
        0,
        len(high_df),
        size=high_count
    )

    high_rows = high_df.iloc[
        high_indices
    ].copy().reset_index(drop=True)


    for feature in FEATURES:

        noise = rng.normal(
            0,
            NOISE_STD[feature],
            size=high_count
        )

        high_rows[feature] = (
            high_rows[feature]
            + noise
        )

        minimum, maximum = LIMITS[
            feature
        ]

        high_rows[feature] = (
            high_rows[feature]
            .clip(
                minimum,
                maximum
            )
        )


    high_rows["priority"] = 1

    generated.append(high_rows)


    return pd.concat(
        generated,
        ignore_index=True
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=========================================="
    )

    print(
        "   EMERGENCY TRIAGE DATASET AUGMENTATION"
    )

    print(
        "=========================================="
    )


    # ========================================================
    # LOAD
    # ========================================================

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"\nDataset not found:\n{INPUT_PATH}"
        )


    print(
        "\nLoading:",
        INPUT_PATH
    )


    original = pd.read_csv(
        INPUT_PATH
    )


    print(
        "Original dataset shape:",
        original.shape
    )


    # ========================================================
    # CLEAN
    # ========================================================

    clean = clean_dataset(
        original
    )


    print(
        "\nUsable original rows:",
        len(clean)
    )


    print(
        "\nOriginal class distribution:"
    )

    print(
        clean["priority"]
        .value_counts()
        .sort_index()
    )


    # ========================================================
    # CALCULATE REQUIRED SYNTHETIC ROWS
    # ========================================================

    if len(clean) >= TARGET_ROWS:

        print(
            "\nDataset already contains",
            len(clean),
            "rows."
        )

        final_df = clean

    else:

        rows_needed = (
            TARGET_ROWS
            - len(clean)
        )


        print(
            "\nSynthetic rows required:",
            rows_needed
        )


        rng = np.random.default_rng(
            RANDOM_STATE
        )


        synthetic = generate_synthetic_rows(
            clean,
            rows_needed,
            rng
        )


        # Combine original + synthetic

        final_df = pd.concat(
            [
                clean,
                synthetic
            ],
            ignore_index=True
        )


        # Shuffle

        final_df = final_df.sample(
            frac=1.0,
            random_state=RANDOM_STATE
        ).reset_index(
            drop=True
        )


    # ========================================================
    # ROUND VALUES
    # ========================================================

    final_df["temperature"] = (
        final_df["temperature"]
        .round(1)
    )

    final_df["heartrate"] = (
        final_df["heartrate"]
        .round()
        .astype(int)
    )

    final_df["resprate"] = (
        final_df["resprate"]
        .round()
        .astype(int)
    )

    final_df["o2sat"] = (
        final_df["o2sat"]
        .round(1)
    )

    final_df["sbp"] = (
        final_df["sbp"]
        .round()
        .astype(int)
    )

    final_df["dbp"] = (
        final_df["dbp"]
        .round()
        .astype(int)
    )

    final_df["pain_numeric"] = (
        final_df["pain_numeric"]
        .round(1)
    )


    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    final_df.to_csv(
        OUTPUT_PATH,
        index=False
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n=========================================="
    )

    print(
        "       AUGMENTATION COMPLETED"
    )

    print(
        "=========================================="
    )


    print(
        "\nOriginal rows:",
        len(clean)
    )


    print(
        "Final rows:",
        len(final_df)
    )


    print(
        "\nFinal dataset shape:",
        final_df.shape
    )


    print(
        "\nFinal class distribution:"
    )

    print(
        final_df["priority"]
        .value_counts()
        .sort_index()
    )


    print(
        "\nPriority mapping:"
    )

    print(
        "0 = Lower Priority"
    )

    print(
        "1 = High Priority"
    )


    print(
        "\nSaved successfully:"
    )

    print(
        OUTPUT_PATH
    )


    print(
        "\n=========================================="
    )

    print(
        "IMPORTANT"
    )

    print(
        "=========================================="
    )

    print(
        "Synthetic rows are generated variations"
    )

    print(
        "of the original dataset."
    )

    print(
        "Use them for training augmentation."
    )

    print(
        "Keep an independent real test set when"
    )

    print(
        "reporting final research performance."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()