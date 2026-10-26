"""Credit-risk analytics on synthetic borrower data.

Steps: load -> quick checks -> EDA charts -> one-hot encode -> train/test split
-> scale (for logistic regression only) -> Logistic Regression and Decision Tree
-> evaluate -> save figures and metrics.

Run from anywhere:  python src/analyze_credit_risk.py
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")  # script mode: write figures to files, don't open windows

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score, RocCurveDisplay,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "borrowers.csv"
FIGURES = ROOT / "reports" / "figures"
METRICS_PATH = ROOT / "reports" / "model_metrics.json"

TARGET = "default_flag"
ID_COL = "borrower_id"
CATEGORICAL = ["home_ownership", "loan_purpose"]
RANDOM_STATE = 42


def save_eda_charts(df):
    plt.figure()
    df[TARGET].value_counts().sort_index().plot(kind="bar")
    plt.title("Simulated Default Label Counts")
    plt.xlabel("default_flag (0 = no simulated default, 1 = simulated default)")
    plt.ylabel("Borrower count")
    plt.tight_layout()
    plt.savefig(FIGURES / "default_label_counts.png", dpi=160)
    plt.close()

    for column, title, ylabel, filename in [
        ("credit_score", "Credit Score by Simulated Default Label", "Credit score",
         "credit_score_by_default.png"),
        ("debt_to_income_ratio", "Debt-to-Income Ratio by Simulated Default Label",
         "Debt-to-income ratio", "dti_by_default.png"),
    ]:
        plt.figure()
        df.boxplot(column=column, by=TARGET)
        plt.suptitle("")
        plt.title(title)
        plt.xlabel(TARGET)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(FIGURES / filename, dpi=160)
        plt.close()


def evaluate(y_true, predictions, probabilities):
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "confusion_matrix": confusion_matrix(y_true, predictions).tolist(),
        "classification_report": classification_report(
            y_true, predictions, zero_division=0, output_dict=True),
    }


def print_result(name, result):
    print(f"\n=== {name} ===")
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        print(f"{key:>10}: {result[key]:.3f}")
    print("Confusion matrix [ [TN, FP], [FN, TP] ]:")
    print(np.array(result["confusion_matrix"]))


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"CSV not found at {DATA_PATH}. Restore data/raw/borrowers.csv.")

    # 1. Load and check ------------------------------------------------------
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df):,} synthetic borrowers.")
    print(f"Simulated default rate: {df[TARGET].mean():.1%}")
    print(f"Missing values: {int(df.isna().sum().sum())}")
    if df.isna().any().any():
        raise ValueError("Unexpected missing values - handle them before modelling.")
    print("\nNumeric summary:")
    print(df.describe().round(2).to_string())

    # 2. EDA charts ----------------------------------------------------------
    save_eda_charts(df)

    # 3. Features: drop ID + target, one-hot encode the two categorical columns
    X = df.drop(columns=[TARGET, ID_COL])
    y = df[TARGET]
    numeric_cols = [c for c in X.columns if c not in CATEGORICAL]
    X = pd.get_dummies(X, columns=CATEGORICAL, drop_first=True, dtype=int)

    # 4. Stratified train/test split (keeps the ~26% default rate in both)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y)

    # 5. Scale numeric columns for Logistic Regression.
    #    Fit on the TRAIN set only, then apply to test -> no information leaks from test.
    scaler = StandardScaler().fit(X_train[numeric_cols])
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    X_train_scaled[numeric_cols] = scaler.transform(X_train[numeric_cols])
    X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])

    # 6. Model 1: Logistic Regression (needs scaled inputs)
    logreg = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)
    logreg.fit(X_train_scaled, y_train)
    logreg_proba = logreg.predict_proba(X_test_scaled)[:, 1]
    logreg_result = evaluate(y_test, logreg.predict(X_test_scaled), logreg_proba)

    # 7. Model 2: Decision Tree (no scaling needed).
    #    Choose max_depth with 5-fold CV on the TRAINING data only (never the test set).
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    depth_scores = {}
    for depth in range(2, 9):
        candidate = DecisionTreeClassifier(
            max_depth=depth, min_samples_leaf=20,
            class_weight="balanced", random_state=RANDOM_STATE)
        depth_scores[depth] = float(
            cross_val_score(candidate, X_train, y_train, cv=cv, scoring="roc_auc").mean())
    best_depth = max(depth_scores, key=depth_scores.get)
    print("\nDecision tree: mean CV ROC-AUC by max_depth (training data only)")
    for depth, score in depth_scores.items():
        print(f"  depth {depth}: {score:.3f}")
    print(f"Chosen max_depth = {best_depth}")

    tree = DecisionTreeClassifier(
        max_depth=best_depth, min_samples_leaf=20,
        class_weight="balanced", random_state=RANDOM_STATE)
    tree.fit(X_train, y_train)
    tree_proba = tree.predict_proba(X_test)[:, 1]
    tree_result = evaluate(y_test, tree.predict(X_test), tree_proba)

    print_result("Logistic Regression", logreg_result)
    print_result("Decision Tree", tree_result)

    # 8. Figures: ROC (both models on ONE axes), tree diagram, feature importance
    fig, ax = plt.subplots()
    RocCurveDisplay.from_predictions(y_test, logreg_proba, name="Logistic Regression", ax=ax)
    RocCurveDisplay.from_predictions(y_test, tree_proba, name="Decision Tree", ax=ax)
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", label="Chance")
    ax.set_title("ROC Curves (Synthetic Test Set)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES / "roc_curves.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(22, 10))
    plot_tree(tree, feature_names=list(X.columns), class_names=["no default", "default"],
              filled=True, rounded=True, max_depth=3, fontsize=8, ax=ax)
    ax.set_title("Decision Tree (top 3 levels shown)")
    fig.tight_layout()
    fig.savefig(FIGURES / "decision_tree.png", dpi=110)
    plt.close(fig)

    importances = pd.Series(tree.feature_importances_, index=X.columns).sort_values(ascending=False)
    top = importances.head(10).sort_values()
    fig, ax = plt.subplots(figsize=(7, 5))
    top.plot(kind="barh", ax=ax)
    ax.set_title("Decision Tree: Top 10 Feature Importances")
    ax.set_xlabel("Importance")
    fig.tight_layout()
    fig.savefig(FIGURES / "feature_importance.png", dpi=160)
    plt.close(fig)

    # 9. Save metrics ----------------------------------------------------------
    metrics = {
        "data_notice": "All records and labels are synthetic. Scores are illustrative only.",
        "rows": int(len(df)),
        "simulated_default_rate": float(y.mean()),
        "decision_tree_cv_roc_auc_by_depth": depth_scores,
        "decision_tree_chosen_max_depth": int(best_depth),
        "decision_tree_top_features": {k: float(v) for k, v in importances.head(10).items()},
        "models": {"Logistic Regression": logreg_result, "Decision Tree": tree_result},
    }
    with open(METRICS_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nSaved figures to: {FIGURES}")
    print(f"Saved metrics to: {METRICS_PATH}")
    print("\nCaution: these metrics measure performance on simulated labels only, "
          "not real-world borrower defaults.")


if __name__ == "__main__":
    main()
