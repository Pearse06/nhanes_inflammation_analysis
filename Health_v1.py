import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
 
# Load the seven NHANES files
crp   = pd.read_sas("P_HSCRP.xpt")   # inflammation
diet  = pd.read_sas("P_DR1TOT.xpt")  # diet
demo  = pd.read_sas("P_DEMO.xpt")    # age and sex
bmx   = pd.read_sas("P_BMX.xpt")     # BMI
sleep = pd.read_sas("P_SLQ.xpt")     # sleep
pa    = pd.read_sas("P_PAQ.xpt")     # physical activity
smoke = pd.read_sas("P_SMQ.xpt")     # smoking
 
# Combine them into one table, matched on participant ID
df = (crp.merge(diet, on="SEQN")
         .merge(demo, on="SEQN")
         .merge(bmx, on="SEQN")
         .merge(sleep, on="SEQN")
         .merge(pa, on="SEQN")
         .merge(smoke, on="SEQN"))
 
# Keep only the columns needed for the question
cols = ["SEQN", "LBXHSCRP",
        # diet
        "DR1TKCAL", "DR1TPROT", "DR1TCARB", "DR1TFIBE", "DR1TSUGR",
        "DR1TSFAT", "DR1TMFAT", 
        "DR1TP205", "DR1TP226", "DR1TMAGN","DR1TP182",
        # controls
        "RIDAGEYR", "RIAGENDR", "BMXBMI",
        "SLD012", "SLD013", "PAQ650", "SMQ040"]
df = df[cols]
 
# Rename columns to plain English
df = df.rename(columns={
    "LBXHSCRP": "crp",
    "DR1TKCAL": "calories", "DR1TPROT": "protein", "DR1TCARB": "carbs",
    "DR1TFIBE": "fiber", "DR1TSUGR": "sugar",
    "DR1TSFAT": "sat_fat", "DR1TMFAT": "mono_fat", 
    "DR1TP205": "epa", "DR1TP226": "dha", "DR1TMAGN": "magnesium","DR1TP182":"omega6",
    "RIDAGEYR": "age", "RIAGENDR": "sex", "BMXBMI": "bmi",
    "SLD012": "sleep_weekday", "SLD013": "sleep_weekend",
    "PAQ650": "vigorous_exercise", "SMQ040": "smoking_status"
})
 
# Create new columns from existing ones
df["starch"] = df["carbs"] - df["sugar"] - df["fiber"]
df["fish_omega3"] = df["epa"] + df["dha"]
 
# Average nightly sleep: 5 weekday nights and 2 weekend nights
df["sleep_hours"] = (5 * df["sleep_weekday"] + 2 * df["sleep_weekend"]) / 7
 
# Smoking: current smokers (answered 1 or 2) and former smokers (answered 3)
df["smoker"] = df["smoking_status"].isin([1, 2]).astype(int)
df["former_smoker"] = (df["smoking_status"] == 3).astype(int)
 
# Clean the data
print("Starting rows:", len(df))
 
df = df[(df["age"] >= 18) & (df["sex"] == 1)]
print("After keeping adult men:", len(df))
 
df = df.dropna(subset=["crp", "calories", "bmi", "sleep_hours"])
print("After removing missing values:", len(df))
 
df = df[df["vigorous_exercise"].isin([1, 2])].copy()
df["vigorous_exercise"] = (df["vigorous_exercise"] == 1).astype(int)
print("After cleaning exercise answers:", len(df))
 
df = df[df["crp"] <= 10]
print("After removing CRP above 10 mg/L:", len(df))
 
df = df[df["calories"].between(800, 4000)]
print("After removing implausible calories:", len(df))
 
# How many young men are left?
young_men = df[df["age"] <= 29]
print("Young men (18 to 29):", len(young_men))
 
# Save and check the result
df.to_csv("combined.csv", index=False)
print(df.shape)
print(df.head())
print(df.describe())
print(df.describe().T)

# Prepare for the regression
df["fish_eater"] = (df["fish_omega3"] >= 0.25).astype(int)  # 1 if at least 0.25 g that day
df["log_crp"] = np.log(df["crp"])                            # evens out CRP's lopsidedness
 
# The regression formula: outcome on the left, factors on the right
formula = ("log_crp ~ fiber + sugar + starch + protein + sat_fat + mono_fat"
           " + omega6 + fish_eater + magnesium"
           " + calories + age + bmi + sleep_hours + vigorous_exercise"
           " + smoker + former_smoker")
 
# Run it on all adult men
model = smf.ols(formula, data=df).fit()
print(model.summary())
 
# Run it again on men aged 18 to 29
young = df[df["age"] <= 29]
print("Young men (18 to 29):", len(young))
young_model = smf.ols(formula, data=young).fit()
print(young_model.summary())