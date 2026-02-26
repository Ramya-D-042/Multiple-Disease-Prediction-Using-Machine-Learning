import numpy as np
import joblib
import os
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

os.makedirs('models', exist_ok=True)
rng = np.random.RandomState(42)

# ------------------------
# Generate realistic demo data for 1000 samples
# ------------------------
n_samples = 1000

# 16 features: Age, Sex, BP, Chol, BMI, Glucose, Skin, Insulin, CP, Thalach, Oldpeak, Slope, MDVP_Fo, MDVP_Jitter, MDVP_Shimmer, NHR
age = rng.randint(20, 80, n_samples)
sex = rng.randint(0, 2, n_samples)
trestbps = rng.randint(90, 180, n_samples)
chol = rng.randint(150, 300, n_samples)
bmi = rng.uniform(18, 40, n_samples)

glucose = rng.randint(70, 200, n_samples)
skin_thickness = rng.randint(10, 50, n_samples)
insulin = rng.randint(15, 300, n_samples)

cp = rng.randint(0, 4, n_samples)
thalach = rng.randint(90, 200, n_samples)
oldpeak = rng.uniform(0, 6, n_samples)
slope = rng.randint(0, 3, n_samples)

mdvp_fo = rng.uniform(100, 200, n_samples)
mdvp_jitter = rng.uniform(0.002, 0.01, n_samples)
mdvp_shimmer = rng.uniform(0.01, 0.05, n_samples)
nhr = rng.uniform(0.001, 0.05, n_samples)

# Combine into feature matrix
X = np.column_stack([
    age, sex, trestbps, chol, bmi,
    glucose, skin_thickness, insulin,
    cp, thalach, oldpeak, slope,
    mdvp_fo, mdvp_jitter, mdvp_shimmer, nhr
])

# ------------------------
# Create synthetic targets (demo)
# ------------------------
# Heart: depends on age, sex, BP, Chol, CP
y_heart = ((age>50) | (trestbps>140) | (chol>240) | (cp>1)).astype(int)

# Diabetes: depends on glucose, BMI, insulin
y_diabetes = ((glucose>120) | (bmi>30) | (insulin>180)).astype(int)

# Parkinson: depends on MDVP features
y_parkinsons = ((mdvp_jitter>0.006) | (mdvp_shimmer>0.03) | (nhr>0.02)).astype(int)

# ------------------------
# Scale features
# ------------------------
scaler = StandardScaler().fit(X)
Xs = scaler.transform(X)

# ------------------------
# Train models
# ------------------------
gb_heart = GradientBoostingClassifier(n_estimators=150, random_state=1).fit(Xs, y_heart)
gb_diabetes = GradientBoostingClassifier(n_estimators=150, random_state=2).fit(Xs, y_diabetes)
mlp_parkinsons = MLPClassifier(hidden_layer_sizes=(64,32), max_iter=500, random_state=3).fit(Xs, y_parkinsons)

# ------------------------
# Save models and scaler
# ------------------------
joblib.dump(gb_heart, 'models/unified_heart.pkl')
joblib.dump(gb_diabetes, 'models/unified_diabetes.pkl')
joblib.dump(mlp_parkinsons, 'models/unified_parkinsons.pkl')
joblib.dump(scaler, 'models/unified_scaler.pkl')

print("Unified demo models saved in 'models/' with realistic 16-input ranges.")
