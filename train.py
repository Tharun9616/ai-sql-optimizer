import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from optimizer.features import FEATURES

df = pd.read_csv("benchmarks/query_data.csv")
df["label"] = (df.index_ms < df.full_ms).astype(int)
train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df.label)

model = RandomForestClassifier(n_estimators=200, min_samples_leaf=3, random_state=42)
model.fit(train[FEATURES], train.label)
ai = model.predict(test[FEATURES])
rule = (test.index_selectivity < 0.30).astype(int).to_numpy()
y = test.label.to_numpy()


def avg_ms(pred):
    return float(np.where(pred == 1, test.index_ms, test.full_ms).mean())


rows = [
    ("Full Scan", test.full_ms.mean(), None),
    ("Rule Based", avg_ms(rule), accuracy_score(y, rule)),
    ("AI Optimizer", avg_ms(ai), accuracy_score(y, ai)),
    ("Oracle (best possible)", np.minimum(test.full_ms, test.index_ms).mean(), 1.0),
]
lines = ["| Method | Avg Execution Time | Plan Accuracy |", "|---|---:|---:|"]
for name, ms, acc in rows:
    lines.append(f"| {name} | {ms:.2f} ms | {'N/A' if acc is None else f'{acc:.1%}'} |")
metrics = (
    f"\nRandom Forest on {len(test)} held-out queries: accuracy {accuracy_score(y, ai):.3f}, "
    f"precision {precision_score(y, ai):.3f}, recall {recall_score(y, ai):.3f}, F1 {f1_score(y, ai):.3f}\n"
)
importance = "\n".join(f"- {f}: {i:.3f}" for f, i in sorted(zip(FEATURES, model.feature_importances_), key=lambda t: -t[1]))
report = "\n".join(lines) + "\n" + metrics + "\nFeature importance\n" + importance + "\n"

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/optimizer.joblib")
open("benchmarks/results.md", "w").write(report)
print(report)
