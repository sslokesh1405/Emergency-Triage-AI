import pandas as pd
import joblib
import json
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    GridSearchCV
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier
)

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# =========================================================
# EMERGENCY TRIAGE AI
# MODEL COMPARISON + HYPERPARAMETER TUNING
# =========================================================


# =========================================================
# 1. PATHS
# =========================================================

data_path = "data/processed/triage_augmented.csv"

models_dir = Path("models")

model_path = models_dir / "triage_model.pkl"
metrics_path = models_dir / "model_metrics.json"

confusion_path = models_dir / "confusion_matrix.png"
confidence_path = models_dir / "confidence_distribution.png"
performance_path = models_dir / "model_performance.png"
feature_path = models_dir / "feature_importance.png"
comparison_path = models_dir / "model_comparison.png"


models_dir.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# 2. LOAD DATASET
# =========================================================

print("\n")
print("==========================================")
print("       EMERGENCY TRIAGE AI")
print("       MODEL TRAINING SYSTEM")
print("==========================================")

print("\nLoading processed dataset...")

df = pd.read_csv(data_path)

print(
    "Dataset shape:",
    df.shape
)


# =========================================================
# 3. FEATURES
# =========================================================

features = [
    "temperature",
    "heartrate",
    "resprate",
    "o2sat",
    "sbp",
    "dbp",
    "pain_numeric"
]

X = df[features]

y = df["priority"]


print("\nFeatures used:")

for feature in features:
    print("-", feature)

print("\nTarget:", "priority")


# =========================================================
# 4. TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n==========================================")
print("TRAIN / TEST SPLIT")
print("==========================================")

print(
    "Training samples:",
    len(X_train)
)

print(
    "Testing samples:",
    len(X_test)
)


# =========================================================
# 5. CROSS VALIDATION
# =========================================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# =========================================================
# 6. DEFINE MODELS
# =========================================================

models = {

    "Random Forest": {

        "model":
            RandomForestClassifier(
                random_state=42,
                class_weight="balanced"
            ),

        "params": {

            "n_estimators":
                [100, 200, 300],

            "max_depth":
                [None, 5, 10, 15],

            "min_samples_split":
                [2, 5, 10],

            "min_samples_leaf":
                [1, 2, 4]
        }
    },


    "Extra Trees": {

        "model":
            ExtraTreesClassifier(
                random_state=42,
                class_weight="balanced"
            ),

        "params": {

            "n_estimators":
                [100, 200, 300],

            "max_depth":
                [None, 5, 10, 15],

            "min_samples_split":
                [2, 5, 10],

            "min_samples_leaf":
                [1, 2, 4]
        }
    },


    "Gradient Boosting": {

        "model":
            GradientBoostingClassifier(
                random_state=42
            ),

        "params": {

            "n_estimators":
                [50, 100, 150],

            "learning_rate":
                [0.03, 0.05, 0.1],

            "max_depth":
                [2, 3, 4],

            "min_samples_split":
                [2, 5]
        }
    },


    "Logistic Regression": {

        "model":
            Pipeline([

                (
                    "scaler",
                    StandardScaler()
                ),

                (
                    "classifier",
                    LogisticRegression(
                        max_iter=2000
                    )
                )
            ]),

        "params": {

            "classifier__C":
                [0.01, 0.1, 1, 10, 100]
        }
    },


    "SVM": {

        "model":
            Pipeline([

                (
                    "scaler",
                    StandardScaler()
                ),

                (
                    "classifier",
                    SVC(
                        probability=True,
                        random_state=42
                    )
                )
            ]),

        "params": {

            "classifier__C":
                [0.1, 1, 10, 100],

            "classifier__gamma":
                ["scale", 0.01, 0.1, 1],

            "classifier__kernel":
                ["rbf", "linear"]
        }
    }
}


# =========================================================
# 7. TRAIN AND COMPARE MODELS
# =========================================================

print("\n")
print("==========================================")
print("       MODEL COMPARISON")
print("==========================================")


results = []

best_model = None
best_model_name = None
best_cv_score = -1
best_params = None


for name, config in models.items():

    print("\n------------------------------------------")
    print("Training:", name)
    print("------------------------------------------")

    grid = GridSearchCV(

        estimator=config["model"],

        param_grid=config["params"],

        cv=cv,

        scoring="accuracy",

        n_jobs=-1,

        refit=True
    )

    grid.fit(
        X_train,
        y_train
    )

    cv_score = grid.best_score_

    print(
        "Best CV Accuracy:",
        f"{cv_score * 100:.2f}%"
    )

    print(
        "Best Parameters:",
        grid.best_params_
    )


    results.append({

        "model":
            name,

        "cv_accuracy":
            round(
                cv_score * 100,
                2
            ),

        "best_parameters":
            grid.best_params_
    })


    if cv_score > best_cv_score:

        best_cv_score = cv_score

        best_model = grid.best_estimator_

        best_model_name = name

        best_params = grid.best_params__ if hasattr(
            grid,
            "best_params__"
        ) else grid.best_params_


# =========================================================
# 8. MODEL COMPARISON RESULTS
# =========================================================

comparison_df = pd.DataFrame(
    results
)

comparison_df = comparison_df.sort_values(
    by="cv_accuracy",
    ascending=False
)


print("\n")
print("==========================================")
print("       CROSS-VALIDATION RESULTS")
print("==========================================")

print(
    comparison_df[
        [
            "model",
            "cv_accuracy"
        ]
    ].to_string(
        index=False
    )
)


print("\n")
print("BEST MODEL:")
print(
    best_model_name
)

print(
    "Cross-validation accuracy:",
    f"{best_cv_score * 100:.2f}%"
)


# =========================================================
# 9. TEST SET EVALUATION
# =========================================================

print("\n")
print("==========================================")
print("       FINAL TEST EVALUATION")
print("==========================================")


y_pred = best_model.predict(
    X_test
)


test_accuracy = accuracy_score(
    y_test,
    y_pred
)


print(
    "\nTest Accuracy:",
    f"{test_accuracy * 100:.2f}%"
)


# =========================================================
# 10. CLASSIFICATION REPORT
# =========================================================

report_text = classification_report(
    y_test,
    y_pred
)

print("\n===== CLASSIFICATION REPORT =====")

print(
    report_text
)


report = classification_report(
    y_test,
    y_pred,
    output_dict=True
)


# =========================================================
# 11. CONFUSION MATRIX
# =========================================================

cm = confusion_matrix(
    y_test,
    y_pred
)


print("\n===== CONFUSION MATRIX =====")

print(cm)


# =========================================================
# 12. ML CONFIDENCE
# =========================================================

print("\n===== ML CONFIDENCE =====")


if hasattr(
    best_model,
    "predict_proba"
):

    probabilities = (
        best_model.predict_proba(
            X_test
        )
    )

    confidence_scores = (
        probabilities.max(
            axis=1
        )
    )

else:

    confidence_scores = np.ones(
        len(X_test)
    )


confidence_percent = (
    confidence_scores * 100
)


average_confidence = (
    confidence_percent.mean()
)

minimum_confidence = (
    confidence_percent.min()
)

maximum_confidence = (
    confidence_percent.max()
)


print(
    "Average Confidence:",
    f"{average_confidence:.2f}%"
)

print(
    "Minimum Confidence:",
    f"{minimum_confidence:.2f}%"
)

print(
    "Maximum Confidence:",
    f"{maximum_confidence:.2f}%"
)


# =========================================================
# 13. MODEL PERFORMANCE VALUES
# =========================================================

accuracy_value = (
    test_accuracy * 100
)

precision_value = (
    report["weighted avg"]["precision"]
    * 100
)

recall_value = (
    report["weighted avg"]["recall"]
    * 100
)

f1_value = (
    report["weighted avg"]["f1-score"]
    * 100
)


# =========================================================
# 14. FEATURE IMPORTANCE
# =========================================================

print("\n===== FEATURE IMPORTANCE =====")


if hasattr(
    best_model,
    "feature_importances_"
):

    feature_importances = (
        best_model.feature_importances_
    )

elif hasattr(
    best_model,
    "named_steps"
) and hasattr(
    best_model.named_steps["classifier"],
    "coef_"
):

    feature_importances = np.abs(
        best_model.named_steps[
            "classifier"
        ].coef_[0]
    )

else:

    feature_importances = np.zeros(
        len(features)
    )


importance = pd.DataFrame({

    "Feature":
        features,

    "Importance":
        feature_importances

})


importance = importance.sort_values(
    by="Importance",
    ascending=False
)


print(
    importance.to_string(
        index=False
    )
)


# =========================================================
# 15. VISUALIZATION
# CONFUSION MATRIX
# =========================================================

print("\nGenerating confusion matrix...")

plt.figure(
    figsize=(8, 7)
)

plt.imshow(
    cm,
    interpolation="nearest"
)

plt.title(
    "Emergency Triage AI\nConfusion Matrix",
    fontsize=17,
    fontweight="bold"
)

plt.xlabel(
    "Predicted Class"
)

plt.ylabel(
    "Actual Class"
)


# Get actual class names
class_names = [
    str(label)
    for label in sorted(
        y.unique()
    )
]


plt.xticks(
    range(len(class_names)),
    class_names,
    rotation=20
)

plt.yticks(
    range(len(class_names)),
    class_names
)


for i in range(
    cm.shape[0]
):

    for j in range(
        cm.shape[1]
    ):

        plt.text(
            j,
            i,
            str(cm[i, j]),
            ha="center",
            va="center",
            fontsize=20,
            fontweight="bold"
        )


plt.tight_layout()

plt.savefig(
    confusion_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show(
    block=False
)

plt.pause(1)


# =========================================================
# 16. VISUALIZATION
# MODEL PERFORMANCE
# =========================================================

print(
    "Generating model performance graph..."
)


metric_names = [

    "Accuracy",

    "Precision",

    "Recall",

    "F1 Score"
]


metric_values = [

    accuracy_value,

    precision_value,

    recall_value,

    f1_value
]


plt.figure(
    figsize=(9, 7)
)

bars = plt.bar(
    metric_names,
    metric_values
)

plt.title(
    f"{best_model_name}\nModel Performance",
    fontsize=17,
    fontweight="bold"
)

plt.ylabel(
    "Score (%)"
)

plt.ylim(
    0,
    100
)

plt.grid(
    axis="y",
    alpha=0.2
)


for bar, value in zip(
    bars,
    metric_values
):

    plt.text(

        bar.get_x()
        + bar.get_width() / 2,

        value + 2,

        f"{value:.2f}%",

        ha="center",

        fontweight="bold"
    )


plt.tight_layout()

plt.savefig(
    performance_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show(
    block=False
)

plt.pause(1)


# =========================================================
# 17. VISUALIZATION
# CONFIDENCE DISTRIBUTION
# =========================================================

print(
    "Generating confidence distribution..."
)


plt.figure(
    figsize=(9, 7)
)

plt.hist(
    confidence_percent,
    bins=10,
    edgecolor="black"
)

plt.axvline(
    average_confidence,
    linestyle="--",
    linewidth=2,
    label=(
        f"Average: "
        f"{average_confidence:.2f}%"
    )
)

plt.title(
    "ML Confidence Score Distribution",
    fontsize=17,
    fontweight="bold"
)

plt.xlabel(
    "ML Confidence (%)"
)

plt.ylabel(
    "Number of Test Samples"
)

plt.xlim(
    0,
    100
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    confidence_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show(
    block=False
)

plt.pause(1)


# =========================================================
# 18. VISUALIZATION
# FEATURE IMPORTANCE
# =========================================================

print(
    "Generating feature importance..."
)


feature_plot = importance.sort_values(
    by="Importance",
    ascending=True
)


plt.figure(
    figsize=(10, 7)
)

bars = plt.barh(

    feature_plot["Feature"],

    feature_plot["Importance"]

)

plt.title(
    f"{best_model_name}\nFeature Importance",
    fontsize=17,
    fontweight="bold"
)

plt.xlabel(
    "Importance"
)

plt.ylabel(
    "Clinical Feature"
)


for bar, value in zip(
    bars,
    feature_plot["Importance"]
):

    plt.text(

        value + 0.005,

        bar.get_y()
        + bar.get_height() / 2,

        f"{value:.3f}",

        va="center",

        fontweight="bold"
    )


plt.grid(
    axis="x",
    alpha=0.2
)

plt.tight_layout()

plt.savefig(
    feature_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show(
    block=False
)

plt.pause(1)


# =========================================================
# 19. VISUALIZATION
# MODEL COMPARISON
# =========================================================

print(
    "Generating model comparison..."
)


plt.figure(
    figsize=(10, 7)
)

bars = plt.bar(

    comparison_df["model"],

    comparison_df["cv_accuracy"]

)

plt.title(
    "Model Comparison - 5 Fold Cross Validation",
    fontsize=17,
    fontweight="bold"
)

plt.ylabel(
    "Cross-Validation Accuracy (%)"
)

plt.xlabel(
    "Machine Learning Model"
)

plt.ylim(
    0,
    100
)

plt.xticks(
    rotation=20
)

plt.grid(
    axis="y",
    alpha=0.2
)


for bar, value in zip(

    bars,

    comparison_df["cv_accuracy"]

):

    plt.text(

        bar.get_x()
        + bar.get_width() / 2,

        value + 2,

        f"{value:.2f}%",

        ha="center",

        fontweight="bold"
    )


plt.tight_layout()

plt.savefig(
    comparison_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show(
    block=False
)

plt.pause(1)


# =========================================================
# 20. SAVE METRICS JSON
# =========================================================

metrics = {

    "best_model":
        best_model_name,

    "cross_validation_accuracy":
        round(
            best_cv_score * 100,
            2
        ),

    "test_accuracy":
        round(
            accuracy_value,
            2
        ),

    "precision":
        round(
            precision_value,
            2
        ),

    "recall":
        round(
            recall_value,
            2
        ),

    "f1_score":
        round(
            f1_value,
            2
        ),

    "training_samples":
        len(X_train),

    "testing_samples":
        len(X_test),

    "average_confidence":
        round(
            average_confidence,
            2
        ),

    "minimum_confidence":
        round(
            minimum_confidence,
            2
        ),

    "maximum_confidence":
        round(
            maximum_confidence,
            2
        ),

    "confusion_matrix":
        cm.tolist(),

    "best_parameters":
        best_params,

    "model_comparison":
        results,

    "feature_importance": [

        {

            "feature":
                row["Feature"],

            "importance":
                round(
                    float(
                        row["Importance"]
                    ),
                    4
                )
        }

        for _, row
        in importance.iterrows()
    ],

    "confidence_scores": [

        round(
            float(score),
            2
        )

        for score
        in confidence_percent
    ]
}


with open(
    metrics_path,
    "w"
) as f:

    json.dump(
        metrics,
        f,
        indent=4
    )


print(
    "\nModel metrics saved:",
    metrics_path
)


# =========================================================
# 21. SAVE BEST MODEL
# =========================================================

joblib.dump(
    best_model,
    model_path
)


print(
    "\n===== BEST MODEL SAVED ====="
)

print(
    "Model:",
    best_model_name
)

print(
    "Path:",
    model_path
)


# =========================================================
# 22. FINAL PERFORMANCE SUMMARY
# =========================================================

print("\n")
print("==========================================")
print("       FINAL MODEL PERFORMANCE")
print("==========================================")

print(
    f"Best Model           : "
    f"{best_model_name}"
)

print(
    f"CV Accuracy          : "
    f"{best_cv_score * 100:.2f}%"
)

print(
    f"Test Accuracy        : "
    f"{accuracy_value:.2f}%"
)

print(
    f"Precision            : "
    f"{precision_value:.2f}%"
)

print(
    f"Recall               : "
    f"{recall_value:.2f}%"
)

print(
    f"F1 Score             : "
    f"{f1_value:.2f}%"
)

print(
    f"Average Confidence   : "
    f"{average_confidence:.2f}%"
)

print(
    f"Minimum Confidence   : "
    f"{minimum_confidence:.2f}%"
)

print(
    f"Maximum Confidence   : "
    f"{maximum_confidence:.2f}%"
)

print("\nConfusion Matrix:")

print(cm)


# =========================================================
# 23. GENERATED FILES
# =========================================================

print("\n")
print("==========================================")
print("          GENERATED FILES")
print("==========================================")

print(
    confusion_path
)

print(
    performance_path
)

print(
    confidence_path
)

print(
    feature_path
)

print(
    comparison_path
)

print(
    metrics_path
)

print(
    model_path
)


# =========================================================
# 24. KEEP WINDOWS OPEN
# =========================================================

print("\n")
print("==========================================")
print("       VISUALIZATIONS READY")
print("==========================================")

print(
    "\nFour performance visualizations +"
    " model comparison have been generated."
)

print(
    "\nPress ENTER in this terminal to close them."
)

input()

plt.close("all")

print(
    "\nTraining process completed successfully."
)