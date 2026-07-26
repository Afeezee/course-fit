"""
train_model.py
---------------
Objective (ii)/(iv): trains the Random Forest ranking stage on the
rule-labelled dataset, and evaluates it with accuracy/precision/
recall/F1 on a held-out split — the classifier metrics half of
Objective (iv). (The other half — real-user relevance ratings — comes
from the usability testing described in the proposal, not from this
script.)

At inference time this model is only ever asked to rank courses that
eligibility.py has already confirmed the student qualifies for (see
recommend.py) — it is not relied on to enforce eligibility itself.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report

df = pd.read_csv("course_dataset.csv")

# One-hot encode the two categorical text columns; grades are already
# encoded, subject flags are already 0/1.
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

clf = RandomForestClassifier(
    n_estimators=300, max_depth=None, random_state=42, class_weight="balanced"
)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

print("Accuracy: ", accuracy_score(y_test, y_pred))
print("Precision (macro):", precision_score(y_test, y_pred, average="macro", zero_division=0))
print("Recall (macro):   ", recall_score(y_test, y_pred, average="macro", zero_division=0))
print("F1 (macro):       ", f1_score(y_test, y_pred, average="macro", zero_division=0))
print()
print(classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0))

# Feature importance — useful for the "why this course" explanation
# layer described in the proposal's deployed-interface section.
importances = pd.Series(clf.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\nTop 10 most influential features:")
print(importances.head(10))
