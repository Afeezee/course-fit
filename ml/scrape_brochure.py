"""
scrape_brochure.py
-------------------
Template for scaling jamb_data.py from 15 hand-curated courses to the
full brochure (all faculties, several hundred courses).

WHY THIS IS A TEMPLATE, NOT A FINISHED SCRAPER:
The brochure text is NOT uniformly structured — each course entry mixes
a baseline requirement with a long, free-text list of per-institution
waivers ("(i) OAU accepts...", "(ii) BENIN requires..."). A fully
general parser that never mis-splits a course boundary would need
hand-tuning per faculty PDF and manual spot-checking against the
rendered brochure. Budget a working session per faculty PDF (~9
faculties total for universities, plus separate COE/Poly/IEI course
lists) rather than expecting one script to do all of it unattended.

Run this on a machine with normal internet access — the direct PDF
links below are the official JAMB brochure PDFs (mirrored by a
JAMB-focused site, since the JAMB IBASS portal itself is a JavaScript
app that serves per-course PDFs interactively rather than one static
file).

Usage:
    pip install requests pdfplumber
    python scrape_brochure.py
"""

import re
import requests
import pdfplumber
import io

FACULTY_PDFS = {
    "Administration": "https://awajis.com/wp-content/uploads/2024/04/brochure-degree-administration.pdf",
    "Agriculture": "https://awajis.com/wp-content/uploads/2024/04/brochure-degree-agriculture.pdf",
    "Arts": "https://awajis.com/wp-content/uploads/2024/04/brochure-degree-arts.pdf",
    "Education": "https://awajis.com/wp-content/uploads/2024/04/brochure-degree-education.pdf",
    "Engineering": "https://awajis.com/wp-content/uploads/2024/04/brochure-degree-engineering.pdf",
    "Law": "https://awajis.com/wp-content/uploads/2024/04/brochure-degree-law.pdf",
    "Medical": "https://awajis.com/wp-content/uploads/2024/04/brochure-degree-medical.pdf",
    "Sciences": "https://awajis.com/wp-content/uploads/2024/04/brochure-degree-sciences.pdf",
    "Social Sciences": "https://awajis.com/wp-content/uploads/2024/04/brochure-degree-social-sciences.pdf",
}

# A course-entry header in the brochure is an ALL-CAPS line (the course
# name) followed by a block of institution codes, then a requirements
# table. This regex catches likely course-name header lines as a
# starting point for a human to review, not a final ground truth.
COURSE_HEADER_RE = re.compile(r"^[A-Z][A-Z /&'\-]{3,60}$")


def fetch_faculty_text(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    text_parts = []
    with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def candidate_course_headers(text: str) -> list:
    """Returns likely course-name lines for a human to review and
    turn into jamb_data.py COURSES entries. This intentionally
    over-selects (false positives like institution-code blocks will
    slip in) — treat this as a checklist to work through, not an
    auto-populated dataset."""
    return [ln.strip() for ln in text.splitlines() if COURSE_HEADER_RE.match(ln.strip())]


if __name__ == "__main__":
    for faculty, url in FACULTY_PDFS.items():
        print(f"\n=== {faculty} ===")
        text = fetch_faculty_text(url)
        headers = candidate_course_headers(text)
        print(f"{len(headers)} candidate course/section headers found — "
              f"review manually and add confirmed entries to jamb_data.py")
        for h in headers[:15]:
            print(" -", h)
