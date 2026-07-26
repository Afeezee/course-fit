"""
recommend.py
------------
Objective (iii): ties eligibility.py (hard filter) and the trained
Random Forest (ranking) together into the function the web interface
in the proposal's "HOW THE DEPLOYED INTERFACE WORKS" section would
call when the student clicks 'Get My Course Recommendations'.

This is illustrative wiring, not a trained-model-in-production script —
run train_model.py first and save the fitted `clf`, `le`, and the
X.columns list (e.g. with joblib) before using this for real.
"""

from eligibility import eligible_courses
from jamb_data import SUBJECT_NAMES


def explain(student: dict, course: dict) -> str:
    matched_strengths = [SUBJECT_NAMES[s] for s in student["strengths"]
                          if s in course["utme_subjects"] or s in course["olevel_subjects"]]
    reason = f"{course['course']} is recommended because "
    parts = []
    if matched_strengths:
        parts.append(f"you have credits in {', '.join(matched_strengths)} "
                      f"and identified them as subject strengths")
    if course["career_cluster"] == student["career_interest"]:
        parts.append(f"you indicated a career interest in {course['career_cluster']}")
    if not parts:
        parts.append("it matches your subject combination and profile")
    return reason + ", and ".join(parts) + "."


def load_best_model(path="best_model.joblib"):
    """Loads the model_comparison.py winner for use in recommend()."""
    import joblib
    bundle = joblib.load(path)
    return bundle["model"], bundle["label_encoder"], bundle["feature_columns"]


def top_n_recommendations(student: dict, clf, label_encoder, feature_columns, n=3):
    """
    student: same shape as in generate_dataset.py's random_student()
    clf, label_encoder, feature_columns: from a fitted train_model.py run
    """
    candidates = eligible_courses(student)
    if not candidates:
        return []

    # Build the same feature row shape the model was trained on.
    import pandas as pd
    row = {}
    for subj in SUBJECT_NAMES:
        row[f"grade_{subj}"] = student["olevel_grades"].get(subj, "NONE")
    grade_map = {"A1": 8, "B2": 7, "B3": 6, "C4": 5, "C5": 4, "C6": 3,
                 "D7": 2, "E8": 1, "F9": 0, "NONE": -1}
    for k in list(row):
        row[k] = grade_map[row[k]]
    for subj in SUBJECT_NAMES:
        row[f"utme_{subj}"] = int(subj in student["utme_subjects"])
        row[f"strength_{subj}"] = int(subj in student["strengths"])
        row[f"weakness_{subj}"] = int(subj in student["weaknesses"])

    # Aptitude is a real training feature; it must be populated at
    # inference too, otherwise `reindex(fill_value=0)` silently defaults
    # every student to aptitude=0 and the model never sees this signal.
    row["aptitude"] = student["aptitude"]

    df_row = pd.DataFrame([row])
    for col in feature_columns:
        if col.startswith("career_interest_"):
            df_row[col] = int(col == f"career_interest_{student['career_interest']}")
        elif col.startswith("work_environment_"):
            df_row[col] = int(col == f"work_environment_{student['work_environment']}")
    df_row = df_row.reindex(columns=feature_columns, fill_value=0)

    proba = clf.predict_proba(df_row)[0]
    course_names = list(label_encoder.classes_)
    eligible_names = {c["course"] for c in candidates}

    ranked = sorted(
        [(course_names[i], p) for i, p in enumerate(proba) if course_names[i] in eligible_names],
        key=lambda x: -x[1],
    )
    top = ranked[:n]

    course_lookup = {c["course"]: c for c in candidates}
    return [
        {"course": name, "probability": round(prob, 3),
         "explanation": explain(student, course_lookup[name])}
        for name, prob in top
    ]
