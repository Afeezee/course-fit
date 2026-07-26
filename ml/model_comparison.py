"""
model_comparison.py
--------------------
Objective (ii)/(iv), extended: trains several classifier families on
the same rule-labelled dataset (course_dataset.csv) and evaluates
each on accuracy, precision, recall and F1 (all macro-averaged, since
course classes are imbalanced) on the same held-out split, so the
comparison is apples-to-apples.

Selection criterion: macro F1 is used as the primary tie-breaker
because it penalises models that do well on common courses but badly
on rare ones — for a recommendation system that has to serve students
across ALL faculties, ignoring the small classes defeats the purpose.
Accuracy alone would reward a model that's great at the big classes
(Statistics, International Relations) and quietly bad at everything
else. Change PRIMARY_METRIC below if you want to optimise for
something else instead.

Run: python model_comparison.py
Output: prints a comparison table, saves the winning model + encoder
+ feature column order to best_model.joblib for recommend.py to load.
"""

import time
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier

PRIMARY_METRIC = "f1_macro"  # one of: accuracy, precision_macro, recall_macro, f1_macro

# ---------- Load + prep data (same steps as train_model.py) ----------
df = pd.read_csv("course_dataset.csv")

grade_map = {"A1": 8, "B2": 7, "B3": 6, "C4": 5, "C5": 4, "C6": 3,
             "D7": 2, "E8": 1, "F9": 0, "NONE": -1}
for col in [c for c in df.columns if c.startswith("grade_")]:
    df[col] = df[col].map(grade_map)

df = pd.get_dummies(df, columns=["career_interest", "work_environment"])

X = df.drop(columns=["label"])
y = df["label"]

le = LabelEncoder()
y_enc = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)

# ---------- Candidate models ----------
# class_weight="balanced" (or equivalent) matters here because course
# classes are imbalanced by construction (some courses are eligible
# to far more simulated profiles than others).
MODELS = {
    "Logistic Regression": LogisticRegression(
        max_iter=2000, class_weight="balanced"
    ),
    "Decision Tree": DecisionTreeClassifier(
        max_depth=None, class_weight="balanced", random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=300, class_weight="balanced", random_state=42
    ),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "XGBoost": XGBClassifier(
        n_estimators=300, eval_metric="mlogloss", random_state=42
    ),
    "K-Nearest Neighbours": KNeighborsClassifier(n_neighbors=15),
    "Naive Bayes": GaussianNB(),
    "SVM (RBF)": SVC(kernel="rbf", class_weight="balanced", probability=True),
}

results = []
fitted_models = {}

for name, model in MODELS.items():
    start = time.time()
    model.fit(X_train, y_train)
    train_seconds = time.time() - start

    y_pred = model.predict(X_test)

    results.append({
        "model": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision_macro": precision_score(y_test, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_test, y_pred, average="macro", zero_division=0),
        "f1_macro": f1_score(y_test, y_pred, average="macro", zero_division=0),
        "train_seconds": round(train_seconds, 2),
    })
    fitted_models[name] = model

results_df = pd.DataFrame(results).sort_values(PRIMARY_METRIC, ascending=False)
pd.set_option("display.float_format", lambda v: f"{v:.3f}")
print("\n=== Model comparison (held-out test split, macro-averaged) ===\n")
print(results_df.to_string(index=False))

best_name = results_df.iloc[0]["model"]
best_model = fitted_models[best_name]
print(f"\nSelected model (highest {PRIMARY_METRIC}): {best_name}")

joblib.dump(
    {"model": best_model, "label_encoder": le, "feature_columns": list(X.columns),
     "model_name": best_name},
    "best_model.joblib",
)
print("Saved to best_model.joblib for use by recommend.py")

results_df.to_csv("model_comparison_results.csv", index=False)
