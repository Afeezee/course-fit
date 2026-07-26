"""
jamb_data.py
------------
Objective (i) output: JAMB brochure data compiled into a structured,
machine-readable form.

Source: the current JAMB Brochure, Faculty of Sciences and Faculty of
Administration PDFs (fetched directly from JAMB's published faculty
brochures, 2026/2027 cycle). Each record below is the GENERAL / baseline
UTME subject requirement and O-Level credit requirement for the course
as printed in the brochure — i.e. the requirement before any
institution-specific waiver is applied. Per-institution waivers (there
are dozens per course, e.g. "OAU accepts Physics or Biology", "BENIN
does not accept Mathematics at A Level") are documented in the source
PDFs but are deliberately NOT modelled here: they vary the DE/O-Level
edge cases for specific universities, not the UTME registration
decision a JAMB candidate makes before choosing a course, which is
what this system advises on.

This file covers 50 courses across nine faculties (Sciences,
Administration, Medical/Pharmaceutical/Health Sciences, Law, Social
Sciences, Agriculture, Arts, Education, Engineering/Environmental/
Technology) — every faculty in the standard JAMB university brochure
is represented, compiled from the brochure PDFs the user supplied
directly (medical.pdf, law.pdf, sciences.pdf, social_sciences.pdf,
agric.pdf, arts.pdf, education.pdf, engineering.pdf).

FIELD SCHEMA per course dict:
  - utme_subjects: 4 required UTME subjects (ENG + 3 others)
  - utme_alt_subject: an optional 5th subject that may substitute for
      exactly one missing subject from utme_subjects
  - olevel_subjects: subjects the brochure requires at CREDIT (>= C6)
  - olevel_pass_subjects: subjects the brochure only asks for at PASS
      (>= D7). Used for the "a pass in Mathematics is required" wording
      that appears across Political Science, Psychology, Sociology, and
      several other Social Sciences courses — treating those as
      credit-required would silently reject students who in fact
      qualify per the brochure.

A DATA-QUALITY NOTE for the writeup: an earlier version of this file
left Psychology out on suspicion that the Social Sciences PDF's
extracted O-Level cell for Psychology was a column-misalignment copy
of the Political Science row above it. Re-extracting the same PDF
with pdfplumber's table parser (rather than plain-text extraction)
confirmed that the two courses genuinely share the same O-Level
requirement per the brochure — the extracted duplicate was not an
artifact but the actual entry. Psychology has now been added with
the same requirement as Political Science, and the "pass in
Mathematics" wording has been modelled explicitly through the new
olevel_pass_subjects field. Sociology, Social Work, and Demography &
Social Statistics were added in the same pass, all cross-checked
against the source brochure's table rows.

Scaling further within a faculty (adding more of its courses beyond
the representative sample below) is the same mechanical pattern —
see scrape_brochure.py for the scraper template.

Subject codes used throughout this project:
ENG=English Language, MTH=Mathematics, PHY=Physics, CHM=Chemistry,
BIO=Biology, ECO=Economics, GEO=Geography, GOV=Government,
HIS=History, LIT=Literature in English, FRN=French, ACC=Accounting/
Financial Accounting, COM=Commerce, AGR=Agricultural Science,
ARA=Arabic, ISL=Islamic Studies
"""

COURSES = [
    # ---- FACULTY OF SCIENCES ----
    {
        "course": "Biochemistry",
        "faculty": "Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "BIO", "CHM", "PHY"],  # PHY or MTH accepted for the 4th
        "utme_alt_subject": "MTH",  # may substitute for PHY
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM", "BIO"],
    "specialty_subjects": ['CHM', 'BIO'],
    },
    {
        # PDF: O-Level "include English Language, Biology, Chemistry
        # and Mathematics/Physics" — Math OR Physics, not both. Earlier
        # version forced both, rejecting arts-leaning bio students who
        # sat Math but not Physics (or vice versa).
        "course": "Biological Sciences",
        "faculty": "Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "BIO", "CHM", "PHY"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "CHM", "BIO"],
    "specialty_subjects": ['BIO'],
    },
    {
        "course": "Physics",
        "faculty": "Sciences",
        "career_cluster": "Sciences & Mathematics",
        "utme_subjects": ["ENG", "PHY", "MTH", "CHM"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "PHY", "CHM", "MTH", "BIO"],
    "specialty_subjects": ['PHY'],
    },
    {
        "course": "Chemistry",
        "faculty": "Sciences",
        "career_cluster": "Sciences & Mathematics",
        "utme_subjects": ["ENG", "CHM", "PHY", "MTH"],  # + 2 of PHY/BIO/MTH
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM", "BIO"],
    "specialty_subjects": ['CHM'],
    },
    {
        "course": "Industrial Chemistry",
        "faculty": "Sciences",
        "career_cluster": "Sciences & Mathematics",
        "utme_subjects": ["ENG", "CHM", "MTH", "PHY"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "MTH", "CHM", "PHY", "BIO"],
    "specialty_subjects": ['CHM'],
    },
    {
        # PDF: O-Level "English Language, Mathematics, Physics and two
        # (2) other Science subjects" — the 4th and 5th slots are
        # explicitly flexible. Earlier version forced BIO which is
        # stricter than the brochure.
        "course": "Industrial Mathematics",
        "faculty": "Sciences",
        "career_cluster": "Sciences & Mathematics",
        "utme_subjects": ["ENG", "MTH", "PHY", "CHM"],
        "utme_alt_subject": "ECO",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM"],
    "specialty_subjects": ['MTH'],
    },
    {
        # PDF: O-Level "including English Language, Mathematics and
        # Physics or Chemistry" — only three strict subjects; the 4th
        # and 5th are any relevant. Earlier version forced BIO.
        "course": "Mathematics",
        "faculty": "Sciences",
        "career_cluster": "Sciences & Mathematics",
        "utme_subjects": ["ENG", "MTH", "PHY", "CHM"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM"],
    "specialty_subjects": ['MTH'],
    },
    {
        # PDF: O-Level "including English Language, Mathematics and at
        # least three (3) credit passes in relevant subjects from
        # Statistics, Chemistry, Further Mathematics, Economics and
        # Geography" — Physics is NOT strictly required; the extra 3
        # come from the science/social-science pool.
        "course": "Statistics",
        "faculty": "Sciences",
        "career_cluster": "Sciences & Mathematics",
        "utme_subjects": ["ENG", "MTH", "PHY", "ECO"],
        "utme_alt_subject": "CHM",
        "olevel_subjects": ["ENG", "MTH", "CHM", "ECO"],
    "specialty_subjects": ['MTH'],
    },
    {
        # PDF: UTME "Mathematics, Physics and one (1) of Biology,
        # Chemistry, Agric Science, Economics and Geography";
        # O-Level "English Language, Mathematics, Physics plus two (2)
        # other Science subjects". BIO was previously forced, but the
        # brochure only requires ENG + MTH + PHY strictly; the
        # remaining two slots are any Science.
        "course": "Computer Science",
        "faculty": "Sciences",
        "career_cluster": "Engineering & Computing",
        "utme_subjects": ["ENG", "MTH", "PHY", "CHM"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM"],
    "specialty_subjects": ['MTH'],
    },
    # ---- FACULTY OF ADMINISTRATION ----
    {
        "course": "Accounting",
        "faculty": "Administration",
        "career_cluster": "Business & Management",
        "utme_subjects": ["ENG", "MTH", "ECO", "ACC"],  # + any Social Science
        "utme_alt_subject": "GOV",
        "olevel_subjects": ["ENG", "MTH", "ECO", "ACC", "COM"],
    "specialty_subjects": ['ACC', 'MTH'],
    },
    {
        "course": "Business Administration",
        "faculty": "Administration",
        "career_cluster": "Business & Management",
        "utme_subjects": ["ENG", "MTH", "ECO", "ACC"],
        "utme_alt_subject": "GOV",
        "olevel_subjects": ["ENG", "MTH", "ECO", "COM", "ACC"],
    "specialty_subjects": ['ECO'],
    },
    {
        "course": "Economics",
        "faculty": "Administration",
        "career_cluster": "Business & Management",
        "utme_subjects": ["ENG", "ECO", "MTH", "GOV"],  # + one of GOV/HIS/GEO/LIT/FRN
        "utme_alt_subject": "GEO",
        "olevel_subjects": ["ENG", "MTH", "ECO", "GOV", "GEO"],
    "specialty_subjects": ['ECO', 'MTH'],
    },
    {
        "course": "Banking and Finance",
        "faculty": "Administration",
        "career_cluster": "Business & Management",
        "utme_subjects": ["ENG", "MTH", "ECO", "GOV"],
        "utme_alt_subject": "GEO",
        "olevel_subjects": ["ENG", "MTH", "ECO", "ACC", "COM"],
    "specialty_subjects": ['ECO', 'MTH'],
    },
    {
        "course": "Marketing",
        "faculty": "Administration",
        "career_cluster": "Business & Management",
        "utme_subjects": ["ENG", "MTH", "ECO", "ACC"],
        "utme_alt_subject": "GOV",
        "olevel_subjects": ["ENG", "MTH", "ECO", "COM", "ACC"],
    "specialty_subjects": ['ECO'],
    },
    {
        "course": "Public Administration",
        "faculty": "Administration",
        "career_cluster": "Public Service & Social Science",
        "utme_subjects": ["ENG", "GOV", "ECO", "MTH"],  # GOV/HIS, ECO, +Mgt/Arts/SocSci
        "utme_alt_subject": "HIS",
        "olevel_subjects": ["ENG", "ECO", "GOV", "MTH", "ACC"],
    "specialty_subjects": ['GOV'],
    },
    {
        # PDF (Administration brochure, Mass Communication row): UTME
        # "Literature in English, Economics and Government"; O-Level
        # "to include English Language, Literature in English and
        # Government plus a pass in Mathematics". So the three credit-
        # required subjects are ENG + LIT + GOV; Mathematics is
        # required only at pass level (D7+), which is what the
        # olevel_pass_subjects field is for. Economics was in the
        # earlier entry but is not in the brochure's baseline.
        "course": "Mass Communication",
        "faculty": "Administration",
        "career_cluster": "Public Service & Social Science",
        "utme_subjects": ["ENG", "LIT", "ECO", "GOV"],
        "utme_alt_subject": "HIS",
        "olevel_subjects": ["ENG", "LIT", "GOV"],
    "specialty_subjects": ['LIT'],
        "olevel_pass_subjects": ["MTH"],
    },
    {
        "course": "International Relations",
        "faculty": "Administration",
        "career_cluster": "Public Service & Social Science",
        "utme_subjects": ["ENG", "MTH", "GOV", "HIS"],  # GOV/ECO + one of HIS/GEO/LIT
        "utme_alt_subject": "GEO",
        "olevel_subjects": ["ENG", "MTH", "GOV", "HIS", "GEO"],
    "specialty_subjects": ['GOV'],
    },
    # ---- FACULTY OF SOCIAL SCIENCES ----
    {
        # PDF: UTME "Geography and any one of Economics, Government,
        # Physics, Chemistry, Biology, and Mathematics"; O-Level
        # "English, Geography and any three (3) from Arts or Social
        # Science subjects with at least a pass in Mathematics".
        # MTH moved to olevel_pass_subjects — was previously required
        # as a credit, which is stricter than the brochure.
        "course": "Geography",
        "faculty": "Social Sciences",
        "career_cluster": "Public Service & Social Science",
        "utme_subjects": ["ENG", "GEO", "ECO", "MTH"],
        "utme_alt_subject": "GOV",
        "olevel_subjects": ["ENG", "GEO", "GOV", "ECO"],
    "specialty_subjects": ['GEO'],
        "olevel_pass_subjects": ["MTH"],
    },
    {
        # PDF: UTME "Government or History plus two (2) other Social
        # Science/Arts subjects"; O-Level "Five (5) SSC credit passes
        # in Government or History, English Language and three (3)
        # other subjects. A pass in Mathematics is required." MTH is
        # therefore pass-required, not credit-required.
        "course": "Political Science",
        "faculty": "Social Sciences",
        "career_cluster": "Public Service & Social Science",
        "utme_subjects": ["ENG", "GOV", "ECO", "HIS"],
        "utme_alt_subject": "GEO",
        "olevel_subjects": ["ENG", "GOV", "HIS", "ECO"],
    "specialty_subjects": ['GOV'],
        "olevel_pass_subjects": ["MTH"],
    },
    {
        # PDF: UTME "Any three (3) subjects from Arts or Social
        # Science"; O-Level identical to Political Science ("Five (5)
        # SSC credit passes in Government or History, English Language
        # and three (3) other subjects. A pass in Mathematics is
        # required"). Confirmed via pdfplumber table extraction that
        # this duplicate is real, not a column-misalignment artefact.
        "course": "Psychology",
        "faculty": "Social Sciences",
        "career_cluster": "Public Service & Social Science",
        "utme_subjects": ["ENG", "GOV", "HIS", "ECO"],
        "utme_alt_subject": "LIT",
        "olevel_subjects": ["ENG", "GOV", "HIS", "ECO"],
    "specialty_subjects": ['GOV'],
        "olevel_pass_subjects": ["MTH"],
    },
    {
        # PDF: UTME "Three (3) Social Science or Arts subjects";
        # O-Level same as Political Science / Psychology (Gov or Hist
        # + English + 3 others, pass in Math required).
        "course": "Sociology",
        "faculty": "Social Sciences",
        "career_cluster": "Public Service & Social Science",
        "utme_subjects": ["ENG", "GOV", "HIS", "ECO"],
        "utme_alt_subject": "LIT",
        "olevel_subjects": ["ENG", "GOV", "HIS", "ECO"],
    "specialty_subjects": ['GOV'],
        "olevel_pass_subjects": ["MTH"],
    },
    {
        # PDF: UTME "Mathematics, Economics/Geography and any other
        # subject"; O-Level "Five (5) SSC credits including English
        # Language and Mathematics".
        "course": "Social Work",
        "faculty": "Social Sciences",
        "career_cluster": "Public Service & Social Science",
        "utme_subjects": ["ENG", "MTH", "ECO", "GEO"],
        "utme_alt_subject": "GOV",
        "olevel_subjects": ["ENG", "MTH", "ECO", "GEO"],
    "specialty_subjects": ['ECO'],
    },
    {
        # PDF: UTME "Mathematics, Economics/Geography and any other
        # subject"; O-Level "Five (5) SSC credit passes in Geography,
        # Economics, Government and Mathematics and any one of
        # Geography or Biology".
        "course": "Demography and Social Statistics",
        "faculty": "Social Sciences",
        "career_cluster": "Public Service & Social Science",
        "utme_subjects": ["ENG", "MTH", "ECO", "GEO"],
        "utme_alt_subject": "GOV",
        "olevel_subjects": ["ENG", "MTH", "ECO", "GEO", "GOV"],
    "specialty_subjects": ['MTH'],
    },
    # ---- FACULTY OF MEDICAL/PHARMACEUTICAL/HEALTH SCIENCES ----
    # Baseline across almost every course in this faculty: UTME
    # Physics, Chemistry, Biology; O-Level English, Mathematics,
    # Physics, Chemistry, Biology (5 credits). A handful of courses
    # (e.g. Nutrition/Dietetics) are otherwise identical, so they are
    # not duplicated here — see the source PDF for the full list.
    {
        "course": "Medicine and Surgery",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "PHY", "CHM", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM", "BIO"],
    "specialty_subjects": ['BIO', 'CHM'],
    },
    {
        "course": "Nursing Science",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "PHY", "CHM", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "CHM", "BIO", "PHY"],
    "specialty_subjects": ['BIO'],
    },
    {
        "course": "Pharmacy",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "PHY", "CHM", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM", "BIO"],
    "specialty_subjects": ['CHM'],
    },
    {
        "course": "Anatomy",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "BIO", "CHM", "PHY"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "BIO", "CHM", "PHY"],
    "specialty_subjects": ['BIO'],
    },
    {
        "course": "Physiology",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "CHM", "PHY", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM", "BIO"],
    "specialty_subjects": ['BIO'],
    },
    {
        "course": "Physiotherapy",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "PHY", "CHM", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "BIO", "PHY", "CHM"],
    "specialty_subjects": ['BIO'],
    },
    {
        "course": "Radiography",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "PHY", "CHM", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "BIO", "PHY", "CHM"],
    "specialty_subjects": ['PHY'],
    },
    {
        "course": "Medical Laboratory Science",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "PHY", "CHM", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM", "BIO"],
    "specialty_subjects": ['BIO', 'CHM'],
    },
    {
        "course": "Pharmacology",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "PHY", "CHM", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM", "BIO"],
    "specialty_subjects": ['CHM'],
    },
    {
        "course": "Optometry",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "PHY", "CHM", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM", "BIO"],
    "specialty_subjects": ['BIO'],
    },
    {
        "course": "Veterinary Medicine",
        "faculty": "Medical/Pharmaceutical/Health Sciences",
        "career_cluster": "Health & Life Sciences",
        "utme_subjects": ["ENG", "PHY", "CHM", "BIO"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "MTH", "BIO", "PHY", "CHM"],
    "specialty_subjects": ['BIO'],
    },
    # ---- FACULTY OF LAW ----
    {
        # Baseline: UTME "any three (3) Arts or Social Science
        # subjects" — most institutions specifically require
        # Literature in English as one of the three.
        "course": "Law",
        "faculty": "Law",
        "career_cluster": "Law & Legal Studies",
        "utme_subjects": ["ENG", "LIT", "GOV", "ECO"],
        "utme_alt_subject": "HIS",
        "olevel_subjects": ["ENG", "LIT", "MTH", "GOV", "ECO"],
    "specialty_subjects": ['LIT'],
    },
    {
        # PDF (Law brochure): O-Level "Five (5) 'O' Level credit
        # passes in Arts or Social Sciences to include English
        # Language and Islamic Studies OR Arabic" — either subject
        # satisfies the requirement, not both. The earlier entry
        # forced BOTH ISL and ARA, rejecting students who sat only
        # one. ISL is by far the more commonly-sat of the two in
        # Nigerian secondary schools; ARA is kept in the UTME slot
        # so a student sitting Arabic instead can still qualify at
        # UTME registration.
        "course": "Islamic Law (Sharia)",
        "faculty": "Law",
        "career_cluster": "Law & Legal Studies",
        "utme_subjects": ["ENG", "ISL", "ARA", "GOV"],
        "utme_alt_subject": "LIT",
        "olevel_subjects": ["ENG", "ISL", "GOV", "LIT"],
    "specialty_subjects": ['ISL'],
    },
    {
        # PDF (Law brochure, Common Law row): O-Level "Five (5) SSC
        # credit passes to include English Language, Literature-in-
        # English and any other three (3) Arts/or Social Science
        # subjects". No Mathematics requirement — the earlier entry's
        # MTH credit was stricter than the brochure. (The separately-
        # modelled "Law" entry above, which reflects the Civil Law
        # variant, DOES require Math per its brochure text.)
        "course": "Common Law",
        "faculty": "Law",
        "career_cluster": "Law & Legal Studies",
        "utme_subjects": ["ENG", "LIT", "GOV", "ECO"],
        "utme_alt_subject": "HIS",
        "olevel_subjects": ["ENG", "LIT", "GOV", "ECO"],
    "specialty_subjects": ['LIT'],
    },
    # ---- FACULTY OF AGRICULTURE ----
    {
        # PDF (Agriculture brochure): O-Level "Five (5) SSC credit
        # passes to include English Language, Biology/Agricultural
        # Science, Chemistry and any one of Mathematics, Physics,
        # Geography and Economics." So the strict 4 are ENG + BIO +
        # CHM + one flex from {MTH, PHY, GEO, ECO}. The earlier entry
        # forced BOTH PHY and MTH (5 credits, all rigid), rejecting
        # students who satisfied the 5-credit total another way.
        # Keeping MTH as the flex pick (most commonly sat).
        "course": "Agriculture",
        "faculty": "Agriculture",
        "career_cluster": "Agriculture & Environmental Science",
        "utme_subjects": ["ENG", "CHM", "BIO", "PHY"],
        "utme_alt_subject": "MTH",
        "olevel_subjects": ["ENG", "BIO", "CHM", "MTH"],
    "specialty_subjects": ['BIO'],
    },
    # ---- FACULTY OF ARTS/HUMANITIES ----
    {
        # Baseline: UTME "Literature in English, one other Arts
        # subject and another Arts or Social Science subject" —
        # O-Level: English, Literature + 3 other Arts/Social Science.
        "course": "English Language",
        "faculty": "Arts",
        "career_cluster": "Arts & Humanities",
        "utme_subjects": ["ENG", "LIT", "GOV", "HIS"],
        "utme_alt_subject": "GEO",
        "olevel_subjects": ["ENG", "LIT", "GOV", "HIS", "ECO"],
    "specialty_subjects": ['LIT'],
    },
    {
        # Baseline: UTME "History and any other two (2) subjects
        # from Arts and Social Sciences" — O-Level: English,
        # History + 3 other Arts/Social Science.
        "course": "History",
        "faculty": "Arts",
        "career_cluster": "Arts & Humanities",
        "utme_subjects": ["ENG", "HIS", "GOV", "LIT"],
        "utme_alt_subject": "ECO",
        "olevel_subjects": ["ENG", "HIS", "GOV", "LIT", "ECO"],
    "specialty_subjects": ['HIS'],
    },
    # ---- FACULTY OF EDUCATION ----
    {
        # PDF (Education brochure): O-Level "to include English
        # Language, Mathematics and any two (2) other Science
        # subjects" — the extra Science slots are flexible; the
        # earlier entry pinned both CHM and BIO, forcing every
        # applicant to have sat Biology even though the brochure
        # allows Chemistry + Physics + anything.
        "course": "Education and Mathematics",
        "faculty": "Education",
        "career_cluster": "Education & Teaching",
        "utme_subjects": ["ENG", "MTH", "PHY", "CHM"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM"],
    "specialty_subjects": ['MTH'],
    },
    {
        # PDF: O-Level "in English Language, Biology, Chemistry,
        # Mathematics and one (1) other subject" — 4 strict + 1 flex.
        # The earlier entry pinned Physics as the 5th, over-strict.
        "course": "Education and Biology",
        "faculty": "Education",
        "career_cluster": "Education & Teaching",
        "utme_subjects": ["ENG", "BIO", "CHM", "MTH"],
        "utme_alt_subject": "PHY",
        "olevel_subjects": ["ENG", "BIO", "CHM", "MTH"],
    "specialty_subjects": ['BIO'],
    },
    {
        # Baseline ("Education and English Language"): UTME
        # Literature in English + 1 Art + 1 other subject —
        # O-Level: English, Literature + 3 other Arts/Social Science.
        "course": "Education and English Language",
        "faculty": "Education",
        "career_cluster": "Education & Teaching",
        "utme_subjects": ["ENG", "LIT", "GOV", "HIS"],
        "utme_alt_subject": "ECO",
        "olevel_subjects": ["ENG", "LIT", "GOV", "HIS", "ECO"],
    "specialty_subjects": ['LIT'],
    },
    {
        # Baseline ("Education and Economics"): UTME Economics,
        # Mathematics + 1 of Geography/Physics/History/Government/
        # Literature — O-Level: English, Economics, Mathematics + 2.
        "course": "Education and Economics",
        "faculty": "Education",
        "career_cluster": "Education & Teaching",
        "utme_subjects": ["ENG", "ECO", "MTH", "GEO"],
        "utme_alt_subject": "GOV",
        "olevel_subjects": ["ENG", "ECO", "MTH", "GEO", "GOV"],
    "specialty_subjects": ['ECO'],
    },
    # ---- FACULTY OF ENGINEERING/ENVIRONMENTAL/TECHNOLOGY ----
    {
        # PDF: O-Level "to include Physics, Chemistry, Mathematics and
        # English Language and any other Science subject" — the 5th
        # slot is any Science, not BIO specifically.
        "course": "Chemical Engineering",
        "faculty": "Engineering",
        "career_cluster": "Engineering & Computing",
        "utme_subjects": ["ENG", "MTH", "PHY", "CHM"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "PHY", "CHM", "MTH"],
    "specialty_subjects": ['CHM'],
    },
    {
        # PDF: O-Level "to include Physics, Chemistry, Mathematics,
        # English Language and one Science subject" — 5th slot flex.
        "course": "Civil Engineering",
        "faculty": "Engineering",
        "career_cluster": "Engineering & Computing",
        "utme_subjects": ["ENG", "PHY", "CHM", "MTH"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "PHY", "CHM", "MTH"],
    "specialty_subjects": ['PHY', 'MTH'],
    },
    {
        # PDF: O-Level "including Mathematics, Physics, Chemistry and
        # English Language" — 4 required; no BIO in the brochure list.
        "course": "Electrical Engineering",
        "faculty": "Engineering",
        "career_cluster": "Engineering & Computing",
        "utme_subjects": ["ENG", "MTH", "PHY", "CHM"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM"],
    "specialty_subjects": ['PHY', 'MTH'],
    },
    {
        # PDF: O-Level "to include Physics, Chemistry, Mathematics,
        # English Language and any other Science subject" — flex 5th.
        "course": "Mechanical Engineering",
        "faculty": "Engineering",
        "career_cluster": "Engineering & Computing",
        "utme_subjects": ["ENG", "MTH", "PHY", "CHM"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "PHY", "CHM", "MTH"],
    "specialty_subjects": ['PHY', 'MTH'],
    },
    {
        # PDF: O-Level "to include Mathematics, Further Mathematics,
        # Chemistry, Physics and English Language" — Further Maths, not
        # Biology, is the 5th subject; but Further Maths isn't in this
        # project's subject set, so we drop the 5th slot rather than
        # substitute an unrelated subject (BIO) that the brochure
        # doesn't list.
        "course": "Computer Engineering",
        "faculty": "Engineering",
        "career_cluster": "Engineering & Computing",
        "utme_subjects": ["ENG", "MTH", "PHY", "CHM"],
        "utme_alt_subject": "BIO",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM"],
    "specialty_subjects": ['MTH'],
    },
    {
        # Baseline: UTME Physics, Mathematics + any of Chemistry,
        # Geography, Art — O-Level: English, Mathematics, Physics,
        # Chemistry + Fine Art or another relevant subject.
        "course": "Architecture",
        "faculty": "Engineering",
        "career_cluster": "Engineering & Computing",
        "utme_subjects": ["ENG", "PHY", "MTH", "CHM"],
        "utme_alt_subject": "GEO",
        "olevel_subjects": ["ENG", "MTH", "PHY", "CHM", "GEO"],
    "specialty_subjects": ['MTH'],
    },
]

SUBJECT_NAMES = {
    "ENG": "English Language", "MTH": "Mathematics", "PHY": "Physics",
    "CHM": "Chemistry", "BIO": "Biology", "ECO": "Economics",
    "GEO": "Geography", "GOV": "Government", "HIS": "History",
    "LIT": "Literature in English", "FRN": "French",
    "ACC": "Financial Accounting", "COM": "Commerce",
    "AGR": "Agricultural Science", "ARA": "Arabic",
    "ISL": "Islamic Studies",
}
