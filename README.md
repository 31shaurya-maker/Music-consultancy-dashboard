# Music Career Development Consultancy: Business Analytics Submission

> **SYNTHETIC DATA.** Every respondent is computer-generated. The results demonstrate an analytics workflow and give testable business hypotheses. They are **not** real market research or proof of demand.

**Individual assignment:**

| Task | Component | Marks |
|---|---|---|
| Task 1 | Synthetic data generation and business validation | 10 |
| Task 2 | Data cleaning and transformation | 10 |
| Task 3 | Descriptive and diagnostic analytics | 30 |

## 1. What to read first

| File | Purpose |
|---|---|
| **`Final_Business_Analytics_Report.pdf`** / `.docx` | The main report: 7 pages, 8 interpreted figures; Times New Roman, 14 pt black headings, 12 pt text |
| `Supplementary_Full_Technical_Report.pdf` | Optional 38-page technical version: all 56 tests, full data dictionary, every chart |
| `Rubric_Compliance_Checklist.md` | Requirement-by-requirement mapping to the brief and rubric |
| `Project_Audit_and_Test_Log.md` | Audit findings, fixes made, and every test run, with results |

## 2. Folder structure

```
Music_Consultancy_Final_Submission/
├── Final_Business_Analytics_Report.pdf / .docx   main report (7 pages)
├── Supplementary_Full_Technical_Report.pdf      optional detailed version (38 pages)
├── Raw_Synthetic_Dataset.csv          raw data, 1,018 × 53 (frozen; MD5 9de2660a…)
├── Cleaned_Synthetic_Dataset.csv      cleaned data, 1,000 × 86 (frozen; MD5 6d9b93d9…)
├── Data_Dictionary.csv                all 86 variables: question text, type, allowed values
├── load_cleaned_data.py               shared loader (restores ordered categories / types)
├── run_all.py                         one-command reproduction with hash checks
├── requirements.txt
├── README.md, Rubric_Compliance_Checklist.md, Project_Audit_and_Test_Log.md
├── 01_Task1_Data_Generation/
│   ├── Questionnaire_Music_Consultancy.docx    the 23-question questionnaire
│   ├── Task1_Business_Validation.md            business problem, framework, generation, pipeline
│   ├── generate_synthetic_data.py              synthetic data generator (seed 42)
│   ├── task1_sales_pipeline_analysis.py        simulated funnel, CAC, channel economics, scenarios
│   └── outputs/                                injection ground-truth log; pipeline/ tables + charts
├── 02_Task2_Cleaning/
│   ├── clean_music_consultancy.py              full cleaning and transformation pipeline
│   ├── independent_verification.py             13 independent checks (imports no cleaning code)
│   └── outputs/                                data-quality report, validation report, cleaning log,
│                                               outlier / near-duplicate / missing / logic tables,
│                                               verification/ evidence
├── 03_Task3_Analysis/
│   ├── task3a_descriptive_analysis.py   task3a_findings_report.md   task3a_business_questions.md
│   ├── task3b_diagnostic_analysis.py    task3b_findings_report.md   task3b_business_implications.md
│   └── outputs/task3a/ (statistics, frequency tables, 9 charts)
│       outputs/task3b/ (56 tests, cross-tabs, group summaries, 9 charts)
├── 04_Dashboard/
│   ├── app.py                           Streamlit dashboard (8 tabs, live filters and statistics)
│   └── test_dashboard.py                automated dashboard test
└── 05_Report_Source/                    scripts that build the report and check its numbers
```

## 3. How to run

**Requirements:** Python 3.10+ (tested on 3.13). Install the packages with:

```bash
pip install -r requirements.txt
```

`pdftotext` (Poppler) is needed only for `05_Report_Source/check_report_numbers.py`.

**Run from this folder:**

```bash
python run_all.py                   # everything, in order, with PASS/FAIL summary (~20 s)
streamlit run 04_Dashboard/app.py   # open the interactive dashboard in the browser
```

`run_all.py` runs these steps:

1. Regenerates the raw data and checks it is **byte-identical** to `Raw_Synthetic_Dataset.csv`.
2. Re-runs the cleaning and checks the rebuilt cleaned file and dictionary are byte-identical to the frozen ones.
3. Runs the independent verification (13 checks).
4. Runs the simulated sales-pipeline analysis.
5. Runs Task 3A and Task 3B.
6. Runs the dashboard smoke test.

The frozen datasets are never overwritten. Rebuilds go to temporary files, which are compared and then deleted.

**Individual scripts** can also be run from anywhere, e.g. `python 03_Task3_Analysis/task3b_diagnostic_analysis.py`. Paths are resolved relative to each script.

**Rebuild the reports** (optional; needs Node.js with the `docx` package):

```bash
node 05_Report_Source/build_short_report.js Final_Business_Analytics_Report.docx   # 7-page main report
python 05_Report_Source/extract_report_data.py                                     # tables for the long version
node 05_Report_Source/main.js Supplementary_Full_Technical_Report.docx             # 38-page version
python 05_Report_Source/check_report_numbers.py                                    # verify the report's numbers (PDF)
```

## 4. Key conventions

**Column prefixes:**

| Prefix | Meaning |
|---|---|
| `Q…` | Questionnaire answers |
| `SIM_` | Simulated sales pipeline (assumptions, not behaviour) |
| `IMP_` | Imputed copies, used only for sensitivity analysis |
| `FLAG_` | Cleaning flags |
| `DER_` | Derived variables |

**Rules followed throughout:**

- The main analysis uses **original answers only**. Blanks are never filled in the original columns, and genuine zeros are kept.
- Unusual values are **kept and flagged**. Results are re-run without `FLAG_Any_Value_Review = 1` as a sensitivity check.
- Statistics are non-parametric (chi-square + Cramér's V, Spearman, Kruskal–Wallis + ε², Mann–Whitney + rank-biserial r), with Benjamini–Hochberg correction across all 56 tests.

## 5. Important limitations

- The data is synthetic. Several relationships were deliberately built into the generator, so strong findings partly reflect simulation assumptions.
- Stated WTP and interest are not payment or conversion.
- The `SIM_` pipeline numbers (cost per lead, conversion, prices, churn) are placeholders.
- Association does not mean causation.
