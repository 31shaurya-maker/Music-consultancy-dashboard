"""Automated smoke test of the Streamlit dashboard (no browser needed).
Runs the app with streamlit.testing.AppTest, exercises every interactive control and
checks the respondent counts against the analysis. Run: python 04_Dashboard/test_dashboard.py"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent / "app.py")
results = []


def by(widgets, label):
    return next(w for w in widgets if w.label.startswith(label))


def check(name, at, expect_n=None):
    exc = [e.value for e in at.exception]
    n = at.sidebar.metric[0].value
    ok = not exc and (expect_n is None or n == expect_n)
    results.append((name, "PASS" if ok else "FAIL", n, exc[:1]))


at = AppTest.from_file(APP, default_timeout=180).run()
check("Initial load: 8 tabs, all 1,000 respondents", at, "1,000")
if len(at.tabs) != 8:
    results.append(("Tab count = 8", "FAIL", len(at.tabs), []))
by(at.multiselect, "Interest").set_value(["Yes"]).run()
check("Filter interest = Yes (expect 513)", at, "513")
by(at.multiselect, "Interest").set_value(["Yes", "Maybe", "No"]).run()
by(at.toggle, "Exclude").set_value(True).run()
check("Exclude flagged respondents (expect 985)", at, "985")
by(at.toggle, "Exclude").set_value(False).run()
by(at.selectbox, "Choose a challenge").set_value("Q14h_Limited_Contract_Knowledge").run()
check("Challenge -> service picker", at)
by(at.selectbox, "Compare package").set_value("Q21_Payment_Model").run()
check("Package comparison selector", at)
by(at.selectbox, "X variable").set_value("DER_Income_Order").run()
check("Correlation pair explorer", at)
by(at.checkbox, "Show sensitivity").check().run()
check("Imputed-WTP sensitivity toggle", at)
by(at.slider, "Conversion").set_value(0.5).run()
check("Pipeline what-if slider", at)
by(at.multiselect, "Age group").set_value(["31-35"]).run()
by(at.multiselect, "Occupation").set_value(["Not currently working"]).run()
guard = any("Fewer than 30" in e.value for e in at.error)
results.append(("Small-subgroup guard (< 30 respondents)", "PASS" if guard and not at.exception else "FAIL",
                at.sidebar.metric[0].value, []))
for r in results:
    print(f"{r[1]:4}  {r[0]}  (respondents in view: {r[2]}){'  ' + str(r[3]) if r[3] else ''}")
sys.exit(0 if all(r[1] == "PASS" for r in results) else 1)
