import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

os.makedirs('models', exist_ok=True)

def train(name, path, model_class, args=None, is_binary_target=True):
    if not os.path.exists(path):
        print(f"{path} not found, skipping {name}")
        return

    df = pd.read_csv(path)
    # Take only numeric columns except target
    X = df.iloc[:, :-1].select_dtypes(include='number')
    y = df.iloc[:, -1]

    # If Parkinson or any continuous target, convert to binary
    if is_binary_target:
        y = (y > 0.5).astype(int)

    # Scale features
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)

    # Split
    Xtr, Xts, ytr, yts = train_test_split(Xs, y, test_size=0.2, random_state=42)

    # Train model
    m = model_class(**(args or {}))
    m.fit(Xtr, ytr)

    # Save model and scaler
    pickle.dump(m, open(f"models/{name}_raw.pkl", 'wb'))
    pickle.dump(scaler, open(f"models/{name}_raw_scaler.pkl", 'wb'))

    # Evaluate
    ypred = m.predict(Xts)
    acc = accuracy_score(yts, ypred)
    print(f"{name} trained and saved. Accuracy: {acc*100:.2f}%")

# ----------------------------
# Train models
# ----------------------------
train('heart', 'dataset/heart.csv', GradientBoostingClassifier, {'n_estimators':200})
train('diabetes', 'dataset/diabetes.csv', GradientBoostingClassifier, {'n_estimators':200})
train('parkinsons', 'dataset/parkinsons.csv', MLPClassifier, {'hidden_layer_sizes':(128,64),'max_iter':500}, is_binary_target=True)
