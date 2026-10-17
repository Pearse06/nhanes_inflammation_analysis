import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
 
# Load each type of file from both cycles and stack them together.
# Files ending in _I are 2015-2016. Files starting with P_ are 2017-2020.
crp   = pd.concat([pd.read_sas("HSCRP_I.xpt"),  pd.read_sas("P_HSCRP.xpt")])   # inflammation
day1  = pd.concat([pd.read_sas("DR1TOT_I.xpt"), pd.read_sas("P_DR1TOT.xpt")])  # diet, day 1
day2  = pd.concat([pd.read_sas("DR2TOT_I.xpt"), pd.read_sas("P_DR2TOT.xpt")])  # diet, day 2
demo  = pd.concat([pd.read_sas("DEMO_I.xpt"),   pd.read_sas("P_DEMO.xpt")])    # age and sex
bmx   = pd.concat([pd.read_sas("BMX_I.xpt"),    pd.read_sas("P_BMX.xpt")])     # BMI
sleep = pd.concat([pd.read_sas("SLQ_I.xpt"),    pd.read_sas("P_SLQ.xpt")])     # sleep
pa    = pd.concat([pd.read_sas("PAQ_I.xpt"),    pd.read_sas("P_PAQ.xpt")])     # physical activity
smoke = pd.concat([pd.read_sas("SMQ_I.xpt"),    pd.read_sas("P_SMQ.xpt")])     # smoking
 
# Combine them into one table, matched on participant ID
df = (crp.merge(day1, on="SEQN")
         .merge(day2, on="SEQN")
         .merge(demo, on="SEQN")
         .merge(bmx, on="SEQN")
         .merge(sleep, on="SEQN")
         .merge(pa, on="SEQN")
         .merge(smoke, on="SEQN"))
 
# Average each nutrient across Day 1 (DR1) and Day 2 (DR2)
df["calories"]  = (df["DR1TKCAL"] + df["DR2TKCAL"]) / 2
df["protein"]   = (df["DR1TPROT"] + df["DR2TPROT"]) / 2
df["carbs"]     = (df["DR1TCARB"] + df["DR2TCARB"]) / 2
df["fiber"]     = (df["DR1TFIBE"] + df["DR2TFIBE"]) / 2
df["sugar"]     = (df["DR1TSUGR"] + df["DR2TSUGR"]) / 2
df["sat_fat"]   = (df["DR1TSFAT"] + df["DR2TSFAT"]) / 2
df["mono_fat"]  = (df["DR1TMFAT"] + df["DR2TMFAT"]) / 2
df["epa"]       = (df["DR1TP205"] + df["DR2TP205"]) / 2
df["dha"]       = (df["DR1TP226"] + df["DR2TP226"]) / 2
df["omega6"]    = (df["DR1TP182"] + df["DR2TP182"]) / 2
df["magnesium"] = (df["DR1TMAGN"] + df["DR2TMAGN"]) / 2
 
# Rename the other columns to plain English
df = df.rename(columns={
    "LBXHSCRP": "crp", "RIDAGEYR": "age", "RIAGENDR": "sex", "BMXBMI": "bmi",
    "SLD012": "sleep_hours",   # weekday sleep (2015-2016 only asked about weekdays)
    "PAQ650": "vigorous_exercise", "SMQ040": "smoking_status"
})
 
# Keep only the columns needed for the question
df = df[["SEQN", "crp",
         "calories", "protein", "carbs", "fiber", "sugar", "sat_fat", "mono_fat",
         "epa", "dha", "omega6", "magnesium",
         "age", "sex", "bmi", "sleep_hours", "vigorous_exercise", "smoking_status"]]
 
# Create new columns from existing ones
df["starch"] = df["carbs"] - df["sugar"] - df["fiber"]
df["fish_omega3"] = df["epa"] + df["dha"]
 
# Smoking: current smokers (answered 1 or 2) and former smokers (answered 3)
df["smoker"] = df["smoking_status"].isin([1, 2]).astype(int)
df["former_smoker"] = (df["smoking_status"] == 3).astype(int)
 
# Clean the data
print("Starting rows:", len(df))
 
df = df[(df["age"] >= 18) & (df["sex"] == 1)]
print("After keeping adult men:", len(df))
 
# Missing calories here also removes men without a second day of diet records
df = df.dropna(subset=["crp", "calories", "bmi", "sleep_hours"])
print("After removing missing values:", len(df))
 
df = df[df["vigorous_exercise"].isin([1, 2])].copy()
df["vigorous_exercise"] = (df["vigorous_exercise"] == 1).astype(int)
print("After cleaning exercise answers:", len(df))
 
df = df[df["crp"] <= 10]
print("After removing CRP above 10 mg/L:", len(df))
 
df = df[df["calories"].between(800, 4000)]
print("After removing implausible calories:", len(df))
 
# Summary of the cleaned data
print(df.describe().T)
 
# Save the cleaned data
df.to_csv("combined.csv", index=False)
 
# Prepare for the regression
df["fish_eater"] = (df["fish_omega3"] >= 0.25).astype(int)  # 1 if at least 0.25 g per day on average
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

# ---- Chart of the results for all men ----
import matplotlib.pyplot as plt
 
# The statistically significant factors to chart, the realistic amount for each, and their labels.
# Diet factors use 100 calories so fat, protein, and starch are compared fairly.
factors = ["bmi", "smoker", "calories", "age", "vigorous_exercise", "protein", "starch", "mono_fat"]
amounts = [7, 1, 500, 10, 1, 25, 25, 100/9]   # 25 g of protein or starch = 100 calories, 100/9 g of fat = 100 calories
labels  = ["BMI (per 7 points)", "Current smoker (vs. never)", "Calories (per 500)",
           "Age (per 10 years)", "Vigorous exercise (vs. none)", "Protein (per 100 calories)",
           "Starch (per 100 calories)", "Monounsaturated fat (per 100 calories)"]
 
# Pull each factor's coefficient and 95% confidence interval from the regression,
# scaled to the realistic amount
coef  = model.params[factors] * amounts
ci    = model.conf_int().loc[factors]
lower = ci[0] * amounts
upper = ci[1] * amounts
 
# Convert from the log scale to a percentage change in CRP
pct       = (np.exp(coef) - 1) * 100
pct_lower = (np.exp(lower) - 1) * 100
pct_upper = (np.exp(upper) - 1) * 100
 
# Put everything in one table and sort it, which groups the factors by direction
chart = pd.DataFrame({"label": labels, "pct": pct.values,
                      "lower": pct_lower.values, "upper": pct_upper.values})
chart = chart.sort_values("pct")
 
# Red for factors linked to higher CRP, green for factors linked to lower CRP
colors = np.where(chart["pct"] > 0, "tab:red", "tab:green")
 
# Draw the chart
plt.figure(figsize=(10, 5))
plt.barh(chart["label"], chart["pct"],
         xerr=[chart["pct"] - chart["lower"], chart["upper"] - chart["pct"]],
         color=colors, capsize=4)
plt.axvline(0, color="black", linewidth=1)
plt.xlabel("Change in CRP (%)")
plt.title("Factors linked to inflammation (CRP) in 4,477 U.S. men, NHANES 2015 to 2020")
plt.tight_layout()
plt.savefig("crp_factors_chart.png", dpi=300)
plt.show()
# ---- Chart of the results for men aged 18 to 29 ----
# Same steps as the chart above, using the young men's regression (young_model)
# and the factors that were statistically significant for them.
factors = ["bmi", "omega6", "age", "vigorous_exercise", "mono_fat"]
amounts = [7, 100/9, 5, 1, 100/9]   # 100/9 g of fat = 100 calories; age uses 5 years since ages only span 18 to 29
labels  = ["BMI (per 7 points)", "Omega-6 (per 100 calories)", "Age (per 5 years)",
           "Vigorous exercise (vs. none)", "Monounsaturated fat (per 100 calories)"]
 
coef  = young_model.params[factors] * amounts
ci    = young_model.conf_int().loc[factors]
lower = ci[0] * amounts
upper = ci[1] * amounts
 
pct       = (np.exp(coef) - 1) * 100
pct_lower = (np.exp(lower) - 1) * 100
pct_upper = (np.exp(upper) - 1) * 100
 
chart = pd.DataFrame({"label": labels, "pct": pct.values,
                      "lower": pct_lower.values, "upper": pct_upper.values})
chart = chart.sort_values("pct")
 
colors = np.where(chart["pct"] > 0, "tab:red", "tab:green")
 
plt.figure(figsize=(10, 4))
plt.barh(chart["label"], chart["pct"],
         xerr=[chart["pct"] - chart["lower"], chart["upper"] - chart["pct"]],
         color=colors, capsize=4)
plt.axvline(0, color="black", linewidth=1)
plt.xlabel("Change in CRP (%)")
plt.title("Factors linked to inflammation (CRP) in 843 U.S. men aged 18 to 29, NHANES 2015 to 2020")
plt.tight_layout()
plt.savefig("crp_factors_chart_young_men.png", dpi=300)
plt.show()
 
 