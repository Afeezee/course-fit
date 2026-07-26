"""
generate_dataset.py
--------------------
Objective (i): builds the labelled training dataset by simulating a
large population of plausible student profiles and labelling each one
with label_engine.best_fit_course(). This is the dataset the Random
Forest in train_model.py is trained on — NOT raw survey data (see the
proposal's ground-truth-strategy note for why).

Output: course_dataset.csv, one row per simulated student with their
input features and the rule-engine label.
"""

import csv
import random
from jamb_data import COURSES
from label_engine import best_fit_course

random.seed(42)

ALL_SUBJECTS = ["ENG", "MTH", "PHY", "CHM", "BIO", "ECO", "GEO",
                "GOV", "HIS", "LIT", "ACC", "COM", "ARA", "ISL"]
CAREER_CLUSTERS = sorted(set(c["career_cluster"] for c in COURSES))
GRADES = ["A1", "B2", "B3", "C4", "C5", "C6", "D7", "E8", "F9"]
CREDIT_GRADES = ["A1", "B2", "B3", "C4", "C5", "C6"]


def random_olevel_profile():
    """Simulate a WAEC result: English + Mathematics always sat, plus
    6 more subjects drawn from the pool, with a grade each. Grades are
    weighted so a 'strong' student profile is plausible (more credits)
    without making everyone a straight-A candidate."""
    subjects = {"ENG", "MTH"}
    while len(subjects) < 8:
        subjects.add(random.choice(ALL_SUBJECTS))

    grades = {}
    for s in subjects:
        # Skew towards credits (this models WAEC candidates who
        # actually intend to proceed to UTME) but leave some failures.
        grades[s] = random.choices(
            GRADES,
            weights=[8, 10, 12, 14, 10, 8, 5, 4, 3],
        )[0]
    return grades


def random_utme_subjects(olevel_grades):
    """UTME subjects are drawn from the student's credited O-Level
    subjects (a student won't usually register a UTME subject they
    didn't sit/pass at O-Level), always including English."""
    credited = [s for s, g in olevel_grades.items() if g in CREDIT_GRADES]
    if "ENG" not in credited:
        credited.append("ENG")
    if len(credited) < 4:
        # top up from full pool if the student didn't get enough credits
        credited = list(set(credited) | set(random.sample(ALL_SUBJECTS, 4)))
    chosen = set(random.sample(credited, min(4, len(credited))))
    chosen.add("ENG")
    return chosen


def random_student():
    olevel_grades = random_olevel_profile()
    utme_subjects = random_utme_subjects(olevel_grades)
    credited = [s for s, g in olevel_grades.items() if g in CREDIT_GRADES]

    strengths = random.sample(credited, min(3, len(credited))) if credited else []
    remaining = [s for s in credited if s not in strengths]
    weaknesses = random.sample(remaining, min(2, len(remaining))) if remaining else []

    return {
        "olevel_grades": olevel_grades,
        "utme_subjects": utme_subjects,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "career_interest": random.choice(CAREER_CLUSTERS),
        "work_environment": random.choice(CAREER_CLUSTERS),
        "aptitude": random.randint(1, 5),
    }


def flatten_for_csv(student, label):
    row = {}
    for subj in ALL_SUBJECTS:
        row[f"grade_{subj}"] = student["olevel_grades"].get(subj, "NONE")
    for subj in ALL_SUBJECTS:
        row[f"utme_{subj}"] = int(subj in student["utme_subjects"])
    for subj in ALL_SUBJECTS:
        row[f"strength_{subj}"] = int(subj in student["strengths"])
    for subj in ALL_SUBJECTS:
        row[f"weakness_{subj}"] = int(subj in student["weaknesses"])
    row["career_interest"] = student["career_interest"]
    row["work_environment"] = student["work_environment"]
    row["aptitude"] = student["aptitude"]
    row["label"] = label
    return row


def generate(n=5000, out_path="course_dataset.csv"):
    rows = []
    discarded = 0
    while len(rows) < n:
        student = random_student()
        label = best_fit_course(student)
        if label is None:
            discarded += 1
            continue
        rows.append(flatten_for_csv(student, label))

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} labelled rows to {out_path} "
          f"({discarded} simulated profiles had no eligible course and were skipped)")


if __name__ == "__main__":
    generate()
