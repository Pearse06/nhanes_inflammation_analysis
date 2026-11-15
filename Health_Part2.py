# Health_ml.py
# Part 2 of the NHANES inflammation project.
#
# Part 1 (Health.py) asked: which factors are associated with inflammation (CRP)?
# Part 2 asks: how much of the difference in CRP between men can these same factors
# explain, when the model has to predict men it has never seen?
#
# Run this in the same folder as combined.csv (Health.py creates it).
 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.inspection import permutation_importance
 
# ---- Load the cleaned data and rebuild the two columns Health.py adds afterward ----
df = pd.read_csv("combined.csv")
df["fish_eater"] = (df["fish_omega3"] >= 0.25).astype(int)   # same rule as Health.py
df["log_crp"] = np.log(df["crp"])                              # same outcome as the regression
print("Men in the data:", len(df))
 
# ---- The same factors as the regression, split into diet and everything else ----
diet_features = ["fiber", "sugar", "starch", "protein", "sat_fat", "mono_fat",
                 "omega6", "fish_eater", "magnesium", "calories"]
other_features = ["age", "bmi", "sleep_hours", "vigorous_exercise",
                  "smoker", "former_smoker"]
all_features = diet_features + other_features
 
X = df[all_features]
y = df["log_crp"]
 
# ---- Hide 20% of the men. The model learns from the other 80% only. ----
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)
print("Training men:", len(X_train), "| Test men (hidden from the model):", len(X_test))
 
 
# ---- The model: a random forest ----
# Many decision trees that each sort men with yes/no questions about the factors,
# then vote. It can pick up curved patterns and interactions between factors.
def make_forest():
    return RandomForestRegressor(n_estimators=300, min_samples_leaf=10,
                                 random_state=42, n_jobs=-1)
 
 
# Cross validation: split the training men into 5 groups, train on 4, score on the 5th,
# and repeat so every group gets a turn. The average is steadier than a single score.
cv = KFold(n_splits=5, shuffle=True, random_state=42)
 
# ---- Score: R squared ----
# R squared is the share of the differences in log CRP between men that the model explains.
# 0 means no better than guessing the average man's CRP for everyone. 1 means perfect.
feature_sets = [("Diet factors only", diet_features),
                ("Age, BMI, sleep, exercise, smoking only", other_features),
                ("All factors", all_features)]
 
rows = []
for set_name, cols in feature_sets:
    model = make_forest()
    cv_r2 = cross_val_score(model, X_train[cols], y_train, cv=cv, scoring="r2").mean()
    model.fit(X_train[cols], y_train)
    test_r2 = r2_score(y_test, model.predict(X_test[cols]))
    rows.append([set_name, round(cv_r2, 3), round(test_r2, 3)])
 
results = pd.DataFrame(rows, columns=["Factors used",
                                      "Cross validated R2 (training men)",
                                      "Test R2 (hidden men)"])
print("\nHow much of the difference in CRP the random forest explains:")
print(results.to_string(index=False))
 
# ---- Typical miss in plain units (all factors) ----
# Predictions are on the log scale, so convert back to mg/L to read them easily.
rf = make_forest()
rf.fit(X_train, y_train)
predicted_crp = np.exp(rf.predict(X_test))
actual_crp = np.exp(y_test)
forest_miss = mean_absolute_error(actual_crp, predicted_crp)
 
# For comparison: the lazy guess, the typical (median) CRP of the training men for everyone
lazy_guess = np.median(np.exp(y_train))
lazy_miss = mean_absolute_error(actual_crp, np.full(len(actual_crp), lazy_guess))
 
print(f"\nOn hidden men, the random forest's guess missed by about {forest_miss:.2f} mg/L on average")
print(f"Guessing {lazy_guess:.2f} mg/L (the typical man) for everyone would miss by about {lazy_miss:.2f} mg/L")
 
# ---- Which factors does the random forest lean on? ----
# Shuffle one factor at a time among the hidden men and see how much R squared drops.
# A big drop means the model was relying on that factor.
imp = permutation_importance(rf, X_test, y_test, scoring="r2",
                             n_repeats=20, random_state=42)
importance = pd.Series(imp.importances_mean, index=all_features).sort_values()
print("\nDrop in test R2 when each factor is shuffled (random forest):")
print(importance.sort_values(ascending=False).round(4))
 
# ---- Chart ----
plt.figure(figsize=(10, 5))
plt.barh(importance.index, importance.values, color="tab:blue")
plt.axvline(0, color="black", linewidth=1)
plt.xlabel("Drop in test R2 when the factor is shuffled")
plt.title("Factors the random forest relies on to predict CRP in men")
plt.tight_layout()
plt.savefig("crp_model_importance.png", dpi=300)
plt.show()
 