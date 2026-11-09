"""
Music Career Development Consultancy - interactive analytics dashboard
=====================================================================
SYNTHETIC DATA: every respondent was simulated (Task 1). Use the dashboard to
explore the analysis workflow, not as evidence of real market demand.

Run from the project root:
    streamlit run 04_Dashboard/app.py

Data: ../Cleaned_Synthetic_Dataset.csv (frozen Task 2 output, read-only; MD5-checked)
Main analysis uses original questionnaire answers (no IMP_ columns). SIM_ pipeline
variables appear only on the "Simulated pipeline" tab.
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from load_cleaned_data import load_cleaned  # noqa: E402

DATA = ROOT / "Cleaned_Synthetic_Dataset.csv"
FROZEN_MD5 = "6d9b93d962b6b1d26b7c2ddd0f2dd298"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ORD3 = ["#86b6ef", "#3987e5", "#184f95"]
GREY = "#c3c2b7"

Q14 = {"Q14a_No_Career_Plan": "No clear career plan", "Q14b_Weak_Personal_Brand": "Weak personal brand",
       "Q14c_Low_Social_Visibility": "Low social media visibility", "Q14d_No_Portfolio": "No professional portfolio",
       "Q14e_Few_Paid_Performances": "Few paid performance opportunities",
       "Q14f_Lack_Industry_Contacts": "Lack of industry contacts", "Q14g_No_Mentor": "No mentor or guidance",
       "Q14h_Limited_Contract_Knowledge": "Limited contract/royalty knowledge"}
Q16 = {"Q16a_Career_Roadmap": "Career roadmap", "Q16b_Personal_Branding": "Personal branding",
       "Q16c_Social_Media_Mgmt": "Social media management", "Q16d_Portfolio_Development": "Portfolio development",
       "Q16e_Paid_Gigs_Access": "Paid gigs & live shows", "Q16f_Industry_Networking": "Networking events",
       "Q16g_Mentorship": "One-to-one mentorship", "Q16h_Vocal_Stage_Coaching": "Vocal & stage coaching",
       "Q16i_Contract_Royalty_Guidance": "Contract & royalty guidance"}
MATCH = {"Q14a_No_Career_Plan": "Q16a_Career_Roadmap", "Q14b_Weak_Personal_Brand": "Q16b_Personal_Branding",
         "Q14c_Low_Social_Visibility": "Q16c_Social_Media_Mgmt", "Q14d_No_Portfolio": "Q16d_Portfolio_Development",
         "Q14e_Few_Paid_Performances": "Q16e_Paid_Gigs_Access", "Q14f_Lack_Industry_Contacts": "Q16f_Industry_Networking",
         "Q14g_No_Mentor": "Q16g_Mentorship", "Q14h_Limited_Contract_Knowledge": "Q16i_Contract_Royalty_Guidance"}
NUMERIC = {"Q6_Years_Singing": "Years singing (Q6)", "Q10_Paid_Performances_3M": "Paid gigs, last 3 months (Q10)",
           "Q11_Monthly_Music_Income_INR": "Music income, INR/month (Q11)",
           "Q19_Current_Monthly_Spend_INR": "Current music spend, INR/month (Q19)",
           "Q20_WTP_Monthly_INR": "Willingness to pay, INR/month (Q20)",
           "DER_Income_Order": "Personal income band (1-5)", "DER_Age_Order": "Age group (1-4)",
           "DER_Followers_Order": "Followers band (1-5)", "DER_Challenge_Score": "Average challenge score (1-5)",
           "DER_Services_Count": "Services selected (0-9)", "DER_Interest_Score": "Interest (No=0, Maybe=1, Yes=2)"}
CATEG = {"Q1_Age_Group": "Age group", "Q2_Gender": "Gender", "Q3_Location": "Location", "Q4_Occupation": "Occupation",
         "Q5_Monthly_Personal_Income": "Personal income", "Q7_Vocal_Training": "Vocal training",
         "Q8_Primary_Genre": "Genre", "Q9_Artist_Status": "Artist status", "Q12_Followers_Band": "Followers",
         "Q13_Career_Goal": "Career goal", "Q17_Package_Preference": "Package preference",
         "Q18_Delivery_Mode": "Delivery mode", "Q21_Payment_Model": "Payment model",
         "Q22_Most_Important_Factor": "Most important factor", "Q23_Consultancy_Interest": "Interest",
         "DER_WTP_Band": "WTP band"}
NONRESP = {"Not provided", "Prefer not to say", "Unknown"}

st.set_page_config(page_title="Music Consultancy Analytics (synthetic)", page_icon="🎤", layout="wide")


@st.cache_data
def get_data():
    if not DATA.exists():
        st.error(f"Dataset not found: {DATA}")
        st.stop()
    if hashlib.md5(DATA.read_bytes()).hexdigest() != FROZEN_MD5:
        st.warning("Cleaned_Synthetic_Dataset.csv differs from the frozen Task 2 file - results may not match the report.")
    return load_cleaned(DATA)


def chart(fig, height=380):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", font=dict(size=13), legend_title_text="")
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.2)")
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.2)")
    st.plotly_chart(fig, width="stretch")


def pct_bar(series, title, order=None, horizontal=True):
    s = series.astype(object).value_counts()
    if order is not None:
        s = s.reindex([o for o in order if o in s.index] + [i for i in s.index if i not in order])
    d = pd.DataFrame({"Category": s.index.astype(str), "Count": s.values})
    d["Percent"] = 100 * d.Count / d.Count.sum()
    d["Label"] = d.apply(lambda r: f"{r.Percent:.1f}% ({r.Count})", axis=1)
    d["Colour"] = np.where(d.Category.isin(NONRESP), "Non-response", "Answer")
    fig = px.bar(d, x="Percent" if horizontal else "Category", y="Category" if horizontal else "Percent",
                 orientation="h" if horizontal else "v", text="Label", color="Colour",
                 color_discrete_map={"Answer": BLUE, "Non-response": GREY}, title=title)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    if horizontal:
        fig.update_yaxes(categoryorder="array", categoryarray=list(d.Category)[::-1], title="")
        fig.update_xaxes(title="% of filtered respondents", range=[0, d.Percent.max() * 1.35])
    return fig


def explain(shows, meaning):
    """Plain-language interpretation shown under every chart (recomputed for the current filters)."""
    st.markdown(f"<div style='font-size:0.92rem;line-height:1.45;margin:-0.4rem 0 1.1rem 0'>"
                f"<b>What it shows:</b> {shows}<br><b>Why it matters:</b> {meaning}</div>", unsafe_allow_html=True)


def top(series):
    s = series.astype(object)
    s = s[~s.isin(NONRESP)].value_counts(normalize=True)
    return (str(s.index[0]), 100 * s.iloc[0]) if len(s) else ("-", 0.0)


def share(series, values):
    s = series.astype(object)
    return 100 * s.isin(values).mean()


def cramers_v(ct):
    chi, p, dof, exp = stats.chi2_contingency(ct, correction=False)
    k = min(ct.shape) - 1
    return chi, p, dof, np.sqrt(chi / (ct.values.sum() * k)), (exp < 5).mean()


def strength_rho(r):
    a = abs(r)
    return "negligible" if a < .1 else "weak" if a < .3 else "moderate" if a < .5 else "strong"


df_all = get_data()

# ------------------------------------------------------------------ sidebar filters
st.sidebar.header("Filters")
st.sidebar.caption("Filters apply to every tab. Statistics are recalculated on the filtered respondents.")


def ms(col, label):
    opts = [c for c in df_all[col].cat.categories if c in set(df_all[col].astype(object))]
    return st.sidebar.multiselect(label, opts, default=opts)


f_age = ms("Q1_Age_Group", "Age group")
f_gender = ms("Q2_Gender", "Gender")
f_loc = ms("Q3_Location", "Location")
f_occ = ms("Q4_Occupation", "Occupation")
f_inc = ms("Q5_Monthly_Personal_Income", "Personal income (INR / month)")
f_int = ms("Q23_Consultancy_Interest", "Interest in consultancy (Q23)")
excl = st.sidebar.toggle("Exclude respondents with flagged unusual values (sensitivity check)", value=False,
                         help="FLAG_Any_Value_Review = 1: 15 respondents with retained unusual values or speeders")
mask = (df_all.Q1_Age_Group.isin(f_age) & df_all.Q2_Gender.isin(f_gender) & df_all.Q3_Location.isin(f_loc)
        & df_all.Q4_Occupation.isin(f_occ) & df_all.Q5_Monthly_Personal_Income.isin(f_inc)
        & df_all.Q23_Consultancy_Interest.isin(f_int))
if excl:
    mask &= df_all.FLAG_Any_Value_Review == 0
df = df_all[mask]
st.sidebar.metric("Respondents in view", f"{len(df):,}", f"{len(df) - len(df_all):,} vs all" if len(df) < len(df_all) else None)

st.title("Music Career Development Consultancy - analytics dashboard")
st.warning("**SYNTHETIC DATA.** All respondents are simulated. Results demonstrate the analysis workflow and do not "
           "prove real demand. Stated preferences are not purchases; the pipeline tab shows assumptions, not sales.",
           icon="⚠️")
if len(df) < 30:
    st.error("Fewer than 30 respondents match the filters - widen the filters to get meaningful results.")
    st.stop()

tabs = st.tabs(["Overview", "Customers", "Challenges & services", "Willingness to pay", "Packages & payment",
                "Diagnostics", "Simulated pipeline", "Key insights"])

# ------------------------------------------------------------------ 1 Overview
with tabs[0]:
    c = st.columns(5)
    c[0].metric("Respondents", f"{len(df):,}")
    c[1].metric("Interested (Yes)", f"{(df.Q23_Consultancy_Interest == 'Yes').mean():.0%}")
    c[2].metric("Median WTP / month", f"₹{df.Q20_WTP_Monthly_INR.median():,.0f}",
                help=f"n = {df.Q20_WTP_Monthly_INR.notna().sum()} valid answers; original answers only")
    c[3].metric("Median music income", f"₹{df.Q11_Monthly_Music_Income_INR.median():,.0f}")
    c[4].metric("Avg challenge score", f"{df.DER_Challenge_Score.mean():.2f} / 5")
    st.subheader("Dataset structure")
    groups = pd.DataFrame({"Column group": ["Questionnaire answers (Q…)", "Simulated pipeline (SIM_…)",
                                            "Imputed copies (IMP_…) - sensitivity only", "Cleaning flags (FLAG_…)",
                                            "Derived variables (DER_…)", "Metadata"],
                           "Columns": [sum(c.startswith("Q") for c in df_all), sum(c.startswith("SIM_") for c in df_all),
                                       sum(c.startswith("IMP_") for c in df_all), sum(c.startswith("FLAG_") for c in df_all),
                                       sum(c.startswith("DER_") for c in df_all), 4]})
    a, b = st.columns([1, 1])
    a.dataframe(groups, hide_index=True, width="stretch")
    miss = df[[c for c in df if c.startswith("Q")]].isna().sum()
    miss = miss[miss > 0].rename("Blank answers (kept blank)").to_frame()
    miss["% of view"] = (100 * miss.iloc[:, 0] / len(df)).round(1)
    b.dataframe(miss, width="stretch")
    st.caption("Frozen cleaned dataset: 1,000 rows × 86 columns (Task 2). Blanks are never filled in the original "
               "columns; categorical non-responses appear as 'Not provided'.")

# ------------------------------------------------------------------ 2 Customers
with tabs[1]:
    a, b = st.columns(2)
    with a:
        chart(pct_bar(df.Q1_Age_Group, "Age group (Q1)", list(df_all.Q1_Age_Group.cat.categories)))
        t_, v_ = top(df.Q1_Age_Group)
        explain(f"The largest age group is {t_} ({v_:.0f}%); all respondents are 18-35 by design.",
                "Messaging, content and channels should speak to early-career singers who are still building a path.")
        chart(pct_bar(df.Q3_Location, "Location (Q3)"))
        explain(f"{share(df.Q3_Location, ['Metro city', 'Tier-2 city']):.0f}% live in a metro or Tier-2 city.",
                "In-person services (gigs, networking events) should launch where venues are concentrated; "
                "smaller towns can be served online.")
        chart(pct_bar(df.Q5_Monthly_Personal_Income, "Personal income, INR/month (Q5)",
                      list(df_all.Q5_Monthly_Personal_Income.cat.categories)))
        inc_low = [c for c in df_all.Q5_Monthly_Personal_Income.cat.categories
                   if c not in NONRESP][:2]
        explain(f"{share(df.Q5_Monthly_Personal_Income, inc_low):.1f}% earn ₹30,000 a month or less.",
                "Most target customers have modest budgets, so a low-cost entry option and income-linked tiers are needed.")
    with b:
        chart(pct_bar(df.Q4_Occupation, "Occupation (Q4)"))
        t_, v_ = top(df.Q4_Occupation)
        explain(f"The most common occupation is '{t_}' ({v_:.0f}%); "
                f"{share(df.Q4_Occupation, ['Full-time musician']):.0f}% are full-time musicians.",
                "Most singers fit music around study or work, so sessions should be flexible (evenings, weekends, online).")
        chart(pct_bar(df.Q9_Artist_Status.astype(str).str.replace(", or occasional management", " / occasional mgmt"),
                      "Artist status (Q9)"))
        explain(f"{share(df.Q9_Artist_Status, ['Independent - no label or management']):.0f}% work with no label "
                "or manager at all.",
                "This is the gap the consultancy fills: most singers have no professional team guiding their career.")
        chart(pct_bar(df.Q8_Primary_Genre, "Primary genre (Q8)"))
        t_, v_ = top(df.Q8_Primary_Genre)
        explain(f"'{t_}' is the most common genre ({v_:.0f}%), but several genres are well represented.",
                "The mentor and venue network has to cover more than one genre to serve the market.")
    st.subheader("Experience and music earnings")
    a, b, c3 = st.columns(3)
    for col, box, unit in [(a, "Q6_Years_Singing", ""), (b, "Q10_Paid_Performances_3M", ""),
                           (c3, "Q11_Monthly_Music_Income_INR", "₹")]:
        s = df[box].dropna().astype(float)
        fig = px.histogram(s, nbins=30, title=f"{NUMERIC[box]}  (n={len(s)})", color_discrete_sequence=[BLUE])
        fig.add_vline(s.median(), line_dash="dash", annotation_text=f"median {unit}{s.median():,.0f}")
        fig.update_layout(showlegend=False, xaxis_title=NUMERIC[box], yaxis_title="Respondents")
        with col:
            chart(fig, 330)
    st.caption("Money and gig variables are right-skewed, so the dashed median is the typical value; a few high "
               "values pull the mean up.")
    explain(f"The typical singer has sung for {df.Q6_Years_Singing.median():.0f} years; "
            f"{100 * (df.Q10_Paid_Performances_3M.dropna() == 0).mean():.0f}% had no paid gig in the last three months "
            f"and {100 * (df.Q11_Monthly_Music_Income_INR.dropna() == 0).mean():.0f}% earn nothing from music "
            f"(median ₹{df.Q11_Monthly_Music_Income_INR.median():,.0f}).",
            "Experience is there but earnings are not: the core promise should be turning experience into paid work.")

# ------------------------------------------------------------------ 3 Challenges & services
with tabs[2]:
    rows = []
    for c_, lab in Q14.items():
        s = df[c_].dropna()
        rows.append({"Challenge": lab, "Mean (1-5)": s.mean(), "% rating 4-5": 100 * (s >= 4).mean(), "n": len(s)})
    ch = pd.DataFrame(rows).sort_values("Mean (1-5)")
    fig = px.bar(ch, x="Mean (1-5)", y="Challenge", orientation="h", text=ch["Mean (1-5)"].round(2),
                 title="Career challenges ranked by mean rating (Q14)", color_discrete_sequence=[BLUE],
                 hover_data={"% rating 4-5": ":.1f", "n": True})
    fig.update_xaxes(range=[1, 5], title="Mean rating (1 = none, 5 = major)")
    fig.update_yaxes(title="")
    a, b = st.columns(2)
    with a:
        chart(fig, 420)
        explain(f"Every challenge averages above the midpoint; the highest is '{ch.Challenge.iloc[-1]}' "
                f"({ch['Mean (1-5)'].iloc[-1]:.2f}) and the lowest is '{ch.Challenge.iloc[0]}' "
                f"({ch['Mean (1-5)'].iloc[0]:.2f}).",
                "The biggest pain points are about access to the industry, so the main promise should be opening doors.")
    sv = pd.DataFrame({"Service": list(Q16.values()), "% selecting": [100 * df[c].mean() for c in Q16]}
                      ).sort_values("% selecting")
    fig = px.bar(sv, x="% selecting", y="Service", orientation="h", text=sv["% selecting"].round(1).astype(str) + "%",
                 title="Services wanted (Q16, tick all that apply)", color_discrete_sequence=[ORANGE])
    fig.update_xaxes(range=[0, 100], title="% of filtered respondents")
    fig.update_yaxes(title="")
    with b:
        chart(fig, 420)
        t3 = list(sv.Service.iloc[::-1][:3])
        explain(f"The most wanted services are {t3[0]} ({sv['% selecting'].iloc[-1]:.0f}%), {t3[1]} and {t3[2]}; "
                f"the least wanted is {sv.Service.iloc[0]} ({sv['% selecting'].iloc[0]:.0f}%).",
                "Demand mirrors the challenges, so the core package should be built around the top services.")
    st.subheader("Does a challenge go with wanting its matching service?")
    pick = st.selectbox("Choose a challenge", list(Q14), format_func=Q14.get)
    svc = MATCH[pick]
    lvl = pd.cut(df[pick].astype(float), [0, 2, 3, 5], labels=["Low (1-2)", "Medium (3)", "High (4-5)"])
    t = pd.DataFrame({"Level": lvl, "Selected": df[svc]}).dropna()
    rate = t.groupby("Level", observed=False).Selected.agg(["mean", "size"]).reset_index()
    fig = px.bar(rate, x="Level", y=rate["mean"] * 100, text=(rate["mean"] * 100).round(0).astype(str) + "%",
                 color="Level", color_discrete_sequence=ORD3,
                 title=f"% selecting '{Q16[svc]}' by rating of '{Q14[pick]}'")
    fig.update_layout(showlegend=False, yaxis_title="% selecting service", xaxis_title="Challenge rating")
    fig.update_yaxes(range=[0, 100])
    a, b = st.columns([1.3, 1])
    with a:
        chart(fig, 360)
        if len(rate) == 3 and rate["size"].min() > 0:
            gap = 100 * (rate["mean"].iloc[2] - rate["mean"].iloc[0])
            explain(f"{100 * rate['mean'].iloc[2]:.0f}% of singers who rate this challenge 4-5 want "
                    f"'{Q16[svc]}', compared with {100 * rate['mean'].iloc[0]:.0f}% of those rating it 1-2 "
                    f"(a gap of {gap:.0f} points).",
                    "A bigger gap means the need is specific, which supports starting each sale with a short "
                    "challenge assessment and recommending the matching service." if gap >= 10 else
                    "The gap is small, so this challenge does not reliably drive demand for its service; it is "
                    "better offered as a free add-on or workshop than as a paid product.")
    ct = pd.crosstab(t.Level, t.Selected)
    with b:
        if ct.shape == (3, 2):
            chi, p, dof, v, low = cramers_v(ct)
            st.metric("Cramér's V (association strength)", f"{v:.2f}")
            st.write(f"Chi-square = {chi:.1f}, df = {dof}, p = {p:.3g}, n = {int(ct.values.sum())}")
            st.write("Cells with expected count < 5: " + ("none ✅" if low == 0 else f"{low:.0%} ⚠️ interpret with care"))
            st.caption("V ≈ .10 small, .30 medium, .50 large. A single test on a filtered subgroup is not "
                       "corrected for multiple comparisons; see the report appendix for the corrected results.")
        else:
            st.info("Not enough variation in this subgroup to run the test.")

# ------------------------------------------------------------------ 4 WTP
with tabs[3]:
    w = df.Q20_WTP_Monthly_INR.dropna()
    c = st.columns(4)
    c[0].metric("Valid WTP answers", f"{len(w):,}")
    c[1].metric("Median (IQR)", f"₹{w.median():,.0f}", f"IQR ₹{w.quantile(.25):,.0f}–{w.quantile(.75):,.0f}",
                delta_color="off")
    c[2].metric("Would pay ≥ ₹2,499 basic price", f"{(w >= 2499).mean():.0%}")
    c[3].metric("Would pay nothing", f"{(w == 0).mean():.0%}")
    a, b = st.columns(2)
    inc_order = [c for c in df_all.Q5_Monthly_Personal_Income.cat.categories if c not in NONRESP]
    d = df[df.Q5_Monthly_Personal_Income.isin(inc_order)]
    fig = px.box(d, x="Q5_Monthly_Personal_Income", y="Q20_WTP_Monthly_INR", points=False,
                 category_orders={"Q5_Monthly_Personal_Income": inc_order}, color_discrete_sequence=[BLUE],
                 title="WTP by personal income band")
    fig.update_layout(xaxis_title="Personal income, INR/month", yaxis_title="WTP, INR/month")
    fig.update_yaxes(range=[0, np.nanpercentile(d.Q20_WTP_Monthly_INR, 97)])
    with a:
        chart(fig, 400)
        dd = d[["DER_Income_Order", "Q20_WTP_Monthly_INR"]].dropna().astype(float)
        if len(dd) > 10:
            r, p = stats.spearmanr(dd.iloc[:, 0], dd.iloc[:, 1])
            st.caption(f"Spearman ρ = {r:.2f} ({strength_rho(r)}), p = {p:.3g}, n = {len(dd)}. Y-axis cut at the "
                       "97th percentile for readability; all values are used in the statistic.")
            med = d.groupby("Q5_Monthly_Personal_Income", observed=True).Q20_WTP_Monthly_INR.median().reindex(inc_order).dropna()
            if len(med) >= 2:
                explain(f"Median WTP rises from ₹{med.iloc[0]:,.0f} in the lowest income band to "
                        f"₹{med.iloc[-1]:,.0f} in the highest ({strength_rho(r)} positive link, ρ = {r:.2f}).",
                        "Singers pay from their overall budget, so prices should be tiered by income rather than "
                        "set as one flat fee.")
    bands = ["0", "1-999", "1,000-2,499", "2,500-4,999", "5,000+"]
    wb = df.DER_WTP_Band.astype(object).value_counts().reindex(bands).fillna(0)
    fig = px.bar(x=bands, y=100 * wb / wb.sum(), text=(100 * wb / wb.sum()).round(0).astype(int).astype(str) + "%",
                 title="WTP bands vs assumed price points (₹1,499 entry, ₹2,499 basic)",
                 color_discrete_sequence=[BLUE])
    fig.update_layout(xaxis_title="WTP band, INR/month", yaxis_title="% of valid answers")
    with b:
        chart(fig, 400)
        explain(f"{100 * (w >= 2499).mean():.0f}% would pay the assumed ₹2,499 basic price, "
                f"{100 * (w >= 1499).mean():.0f}% would pay the ₹1,499 entry price, and {100 * (w == 0).mean():.0f}% "
                "would pay nothing.",
                "Price is the main barrier: a lower entry tier widens the market, while the basic price suits only "
                "about a third of singers.")
    if st.checkbox("Show sensitivity: include imputed WTP values (IMP_ column)"):
        st.info(f"Imputed version (income-band median fills {df.FLAG_Q20_Imputed.sum()} blanks): median "
                f"₹{df.IMP_Q20_WTP_Monthly_INR.median():,.0f}, mean ₹{df.IMP_Q20_WTP_Monthly_INR.mean():,.0f} vs observed "
                f"median ₹{w.median():,.0f}, mean ₹{w.mean():,.0f}. Imputed values are assumptions, not answers.")

# ------------------------------------------------------------------ 5 Packages & payment
with tabs[4]:
    a, b = st.columns(2)
    with a:
        chart(pct_bar(df.Q17_Package_Preference, "Package preference (Q17) - stated, not purchased"))
        t_, v_ = top(df.Q17_Package_Preference)
        explain(f"'{t_}' is the most preferred format ({v_:.0f}%).",
                "This should be the default offer, with single services as a low-risk entry point.")
        chart(pct_bar(df.Q18_Delivery_Mode, "Delivery mode (Q18)"))
        t_, v_ = top(df.Q18_Delivery_Mode)
        explain(f"'{t_}' is the most preferred delivery mode ({v_:.0f}%).",
                "Combining online sessions with in-person events keeps costs down while still giving real industry access.")
    with b:
        chart(pct_bar(df.Q21_Payment_Model, "Payment model (Q21) - stated, not purchased"))
        t_, v_ = top(df.Q21_Payment_Model)
        explain(f"Preferences are spread out; the most common is '{t_}' ({v_:.0f}%).",
                "No single payment model suits everyone, so payment options should be matched to the package "
                "(see the comparison below).")
        chart(pct_bar(df.Q22_Most_Important_Factor, "Most important decision factor (Q22)"))
        t_, v_ = top(df.Q22_Most_Important_Factor)
        explain(f"'{t_}' is the most common deciding factor ({v_:.0f}%).",
                "The sales message should lead with this factor, backed by clear proof of results.")
    grp = st.selectbox("Compare package preference across", ["Q5_Monthly_Personal_Income", "DER_WTP_Band",
                                                              "Q4_Occupation", "Q23_Consultancy_Interest",
                                                              "Q21_Payment_Model"], format_func=CATEG.get)
    t = df[[grp, "Q17_Package_Preference"]].dropna()
    t = t[~t[grp].astype(str).isin(NONRESP)]
    ct = pd.crosstab(t[grp].astype(str), t.Q17_Package_Preference.astype(str))
    rp = (100 * ct.div(ct.sum(axis=1), axis=0)).reset_index().melt(id_vars=grp, var_name="Package", value_name="%")
    fig = px.bar(rp, y=grp, x="%", color="Package", orientation="h", text=rp["%"].round(0).astype(int).astype(str) + "%",
                 color_discrete_sequence=[BLUE, ORANGE, AQUA], title=f"Package preference by {CATEG[grp].lower()} (row %)")
    fig.update_layout(barmode="stack", xaxis_title="% of group", yaxis_title="")
    chart(fig, 420)
    if min(ct.shape) > 1:
        chi, p, dof, v, low = cramers_v(ct)
        st.caption(f"Chi-square = {chi:.1f}, df = {dof}, p = {p:.3g}, Cramér's V = {v:.2f}, n = {int(ct.values.sum())}."
                   + (" ⚠️ Some expected counts < 5." if low > .2 else ""))
        vs = "negligible" if v < .1 else "small" if v < .3 else "medium" if v < .5 else "large"
        explain(f"Each bar shows how package choice splits within one {CATEG[grp].lower()} group. The association is "
                f"{vs} (Cramér's V = {v:.2f}, p = {p:.3g}).",
                "Where the bars differ clearly, the package offer should be tailored to that group; where they look "
                "alike, one default offer works for everyone.")

# ------------------------------------------------------------------ 6 Diagnostics
with tabs[5]:
    st.subheader("Spearman correlation heatmap")
    sel = st.multiselect("Variables", list(NUMERIC), default=list(NUMERIC), format_func=NUMERIC.get)
    if len(sel) >= 2:
        corr = df[sel].astype(float).corr(method="spearman").rename(index=NUMERIC, columns=NUMERIC)
        fig = px.imshow(corr, text_auto=".2f", zmin=-.7, zmax=.7, color_continuous_scale=["#e34948", "#f0efec", BLUE],
                        aspect="auto")
        chart(fig, 560)
        st.caption("Spearman ρ uses ranks, so it suits ordinal answers and skewed money values. |ρ| < .1 negligible, "
                   ".1–.3 weak, .3–.5 moderate, > .5 strong. Correlation does not show causation.")
        cu = corr.where(~np.eye(len(corr), dtype=bool)).stack()
        if len(cu):
            i_ = cu.abs().idxmax()
            explain(f"Darker blue means a stronger positive link and red a negative one. The strongest link here is "
                    f"{i_[0]} with {i_[1]} (ρ = {cu[i_]:.2f}, {strength_rho(cu[i_])}).",
                    "The strongest links show which signals best identify likely customers, such as how many services "
                    "a singer wants and how much they are willing to pay.")
    st.subheader("Explore any pair")
    a, b = st.columns(2)
    xv = a.selectbox("X variable", list(NUMERIC), index=list(NUMERIC).index("Q19_Current_Monthly_Spend_INR"),
                     format_func=NUMERIC.get)
    yv = b.selectbox("Y variable", list(NUMERIC), index=list(NUMERIC).index("Q20_WTP_Monthly_INR"),
                     format_func=NUMERIC.get)
    d = df[[xv, yv, "Q23_Consultancy_Interest"]].dropna()
    d = d.assign(**{xv: d[xv].astype(float), yv: d[yv].astype(float)})
    logx = st.checkbox("Log scale (for money values)", value=True)
    fig = px.scatter(d, x=xv, y=yv, color="Q23_Consultancy_Interest", opacity=.5, log_x=logx and d[xv].min() > 0,
                     log_y=logx and d[yv].min() > 0, color_discrete_map={"Yes": BLUE, "Maybe": ORANGE, "No": AQUA},
                     labels={xv: NUMERIC[xv], yv: NUMERIC[yv]})
    if logx and (d[xv].min() <= 0 or d[yv].min() <= 0):
        fig.update_xaxes(type="log" if d[xv].min() > 0 else "linear")
        st.caption("Log scale skipped for axes that contain zeros (genuine zero answers are kept).")
    chart(fig, 460)
    if len(d) > 10:
        r, p = stats.spearmanr(d[xv], d[yv])
        st.write(f"**Spearman ρ = {r:.2f}** ({strength_rho(r)}), p = {p:.3g}, n = {len(d)}")
        explain(f"Each dot is one respondent, coloured by interest. The link between '{NUMERIC[xv]}' and "
                f"'{NUMERIC[yv]}' is {strength_rho(r)} (ρ = {r:.2f}).",
                "A moderate or strong link means one variable is a useful screening signal for the other; a "
                "negligible link means it should not be used for targeting.")

# ------------------------------------------------------------------ 7 Simulated pipeline
with tabs[6]:
    st.info("These SIM_ variables are **assumptions written into the Task 1 generator** (cost per lead, booking "
            "and conversion probabilities, prices, churn). They are not customer behaviour or a revenue forecast.")
    booked = df.SIM_Consultation_Booked == "Yes"
    cust = df.SIM_Converted_Customer == "Yes"
    fig = go.Figure(go.Funnel(y=["Leads", "Consultation booked", "Paying customer"],
                              x=[len(df), int(booked.sum()), int(cust.sum())], textinfo="value+percent initial",
                              marker=dict(color=ORD3)))
    fig.update_layout(title="Simulated funnel")
    a, b = st.columns(2)
    with a:
        chart(fig, 360)
        explain(f"Of {len(df):,} leads, {100 * booked.mean():.0f}% book a consultation and {100 * cust.mean():.1f}% "
                "become paying customers.",
                "Stated interest is much higher than simulated conversion, so a real pilot must measure actual "
                "bookings and payments before scaling.")
    spend = df.SIM_Lead_Cost_INR.sum() + 600 * booked.sum()
    with b:
        c = st.columns(2)
        c[0].metric("Customers", f"{cust.sum():,}")
        c[1].metric("Blended CAC", f"₹{spend / max(cust.sum(), 1):,.0f}")
        c = st.columns(2)
        c[0].metric("Mean 6-month revenue / customer", f"₹{df.loc[cust, 'SIM_Expected_Revenue_INR'].mean():,.0f}")
        c[1].metric("Gross revenue ÷ acquisition spend", f"{df.SIM_Expected_Revenue_INR.sum() / spend:.2f}×")
        st.caption("CAC = (lead cost + ₹600 per consultation) ÷ customers. Revenue is gross (before delivery cost, GST, refunds).")
    rows = []
    for src, g in df.groupby("SIM_Lead_Source", observed=True):
        b_, c_ = g.SIM_Consultation_Booked == "Yes", g.SIM_Converted_Customer == "Yes"
        sp = g.SIM_Lead_Cost_INR.sum() + 600 * b_.sum()
        if c_.sum():
            rows.append({"Lead source": src, "Leads": len(g), "Customers": int(c_.sum()), "CAC (₹)": round(sp / c_.sum()),
                         "Revenue ÷ spend": round(g.SIM_Expected_Revenue_INR.sum() / sp, 2)})
    if rows:
        chn = pd.DataFrame(rows).sort_values("CAC (₹)")
        fig = px.bar(chn, x="CAC (₹)", y="Lead source", orientation="h", text="CAC (₹)", color_discrete_sequence=[BLUE],
                     title="Simulated CAC by lead source (lower is better)", hover_data=["Customers", "Revenue ÷ spend"])
        fig.update_yaxes(categoryorder="total descending", title="")
        chart(fig, 380)
        explain(f"{chn['Lead source'].iloc[0]} has the lowest simulated cost per customer (₹{chn['CAC (₹)'].iloc[0]:,}) "
                f"and {chn['Lead source'].iloc[-1]} the highest (₹{chn['CAC (₹)'].iloc[-1]:,}).",
                "Marketing budget should start with the cheapest channels; these costs are assumptions to test, "
                "not observed results.")
    st.subheader("What-if: how sensitive is the model?")
    a, b, c3 = st.columns(3)
    cm = a.slider("Conversion vs assumption", 0.25, 1.5, 1.0, 0.05)
    pm = b.slider("Price vs assumption", 0.5, 1.5, 1.0, 0.05)
    rm = c3.slider("Retention vs assumption", 0.5, 1.5, 1.0, 0.05)
    cust_s = cust.sum() * cm
    rev_s = df.SIM_Expected_Revenue_INR.sum() * cm * pm * rm
    st.write(f"Customers ≈ **{cust_s:.0f}**, CAC ≈ **₹{spend / max(cust_s, 1):,.0f}**, gross revenue ÷ acquisition "
             f"spend ≈ **{rev_s / spend:.2f}×** (1× = revenue only repays acquisition; delivery costs not included).")

# ------------------------------------------------------------------ 8 Insights
with tabs[7]:
    st.markdown("""
**Key insights from the full synthetic dataset** (see the final report for the statistics; Benjamini–Hochberg corrected):

1. **Access problems lead.** Lack of industry contacts (mean 3.83/5) and few paid performances (3.78) are the top challenges;
   paid-gig access (65%), networking (62%) and mentorship (59%) are the most wanted services.
2. **Needs are specific.** People rating a challenge 4–5 are 23–43 points more likely to want the matching service
   (Cramér's V 0.19–0.33) - except contract guidance (V 0.08, not significant).
3. **Price is the main barrier.** Median WTP ₹1,500/month, below the assumed ₹2,499 basic price; WTP rises with personal
   income (ρ 0.42) and current spend (ρ 0.35) but not with music income (ρ −0.01).
4. **Interest builds with overall difficulty** (ρ 0.33) rather than any single challenge (ρ 0.16–0.23).
5. **Basic + add-ons is the default choice** in almost every group; end-to-end is favoured by high-income / high-WTP
   respondents. **Payment model follows the package**, not income.
6. **Simulated pipeline:** 13.6% of leads become customers; referral, WhatsApp and music-school partnerships have the
   lowest assumed CAC; results are most sensitive to the conversion rate.

*All findings are from synthetic data, and several relationships were built into the simulation. Treat them as
hypotheses to test with real singers.*
""")
    st.caption("Use the filters on the left to see how each pattern holds within subgroups.")
