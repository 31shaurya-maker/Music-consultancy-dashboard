"""
Loader for the CLEANED SYNTHETIC Music Consultancy dataset.
CSV files cannot store data types such as ordered categories or nullable integers,
so this function restores them. Use it in notebooks and Streamlit:

    from load_cleaned_data import load_cleaned
    df = load_cleaned()                       # or load_cleaned("path/to/file.csv")

    # Streamlit: cache it
    # @st.cache_data
    # def get_data(): return load_cleaned()
"""
from pathlib import Path

import pandas as pd

DEFAULT = Path(__file__).resolve().parent / "music_consultancy_cleaned_synthetic.csv"

ORDERED = {
    "Q1_Age_Group": ["18-21", "22-25", "26-30", "31-35"],
    "Q5_Monthly_Personal_Income": ["Below 15,000", "15,000 - 30,000", "30,001 - 50,000", "50,001 - 1,00,000",
                                   "Above 1,00,000", "Prefer not to say", "Not provided"],
    "Q12_Followers_Band": ["Under 1,000", "1,000 - 10,000", "10,001 - 50,000", "50,001 - 1,00,000",
                           "Above 1,00,000", "Not provided"],
    "Q23_Consultancy_Interest": ["No", "Maybe", "Yes"],
    "DER_WTP_Band": ["0", "1-999", "1,000-2,499", "2,500-4,999", "5,000+"],
    "DER_Funnel_Stage": ["1 Lead only", "2 Consultation booked", "3 Customer"],
}
UNORDERED = ["Q2_Gender", "Q3_Location", "Q4_Occupation", "Q7_Vocal_Training", "Q8_Primary_Genre",
             "Q9_Artist_Status", "Q13_Career_Goal", "Q15_Biggest_Challenge", "Q17_Package_Preference",
             "Q18_Delivery_Mode", "Q21_Payment_Model", "Q22_Most_Important_Factor", "SIM_Lead_Source",
             "SIM_Consultation_Booked", "SIM_Converted_Customer", "DER_Biggest_Challenge_Label"]
NULLABLE_INT = ["Q6_Years_Singing", "Q10_Paid_Performances_3M", "SIM_Months_Retained",
                "DER_Age_Order", "DER_Income_Order", "DER_Followers_Order", "DER_Interest_Score"]


def load_cleaned(path=DEFAULT):
    df = pd.read_csv(path, parse_dates=["Response_Timestamp"], dtype={"DER_WTP_Band": "string"})
    for c, order in ORDERED.items():
        df[c] = pd.Categorical(df[c], categories=order, ordered=True)
    for c in UNORDERED:
        df[c] = df[c].astype("category")
    for c in NULLABLE_INT + [c for c in df.columns if c.startswith("Q14")]:
        df[c] = df[c].astype("Int64")
    return df


if __name__ == "__main__":
    d = load_cleaned()
    print("[SYNTHETIC]", d.shape)
    print(d["Q1_Age_Group"].value_counts(sort=False))
