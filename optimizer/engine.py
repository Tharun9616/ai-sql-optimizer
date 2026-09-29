import os

import joblib
import pandas as pd

from .features import FEATURES, extract
from .parser import parse
from .plans import best_index, build_sql, execute, rule_based

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "optimizer.joblib")


def load_model(path=MODEL_PATH):
    return joblib.load(path) if os.path.exists(path) else None


def optimize(con, stats, sql, model=None, sample=10):
    query = parse(sql)
    feats = extract(query, stats)
    index = best_index(query, stats)
    rule_plan = rule_based(feats) if index else "full_scan"

    if index is None:
        plan, confidence, source = "full_scan", 1.0, "no usable index"
    elif model is None:
        plan, confidence, source = rule_plan, None, "rule-based (no trained model found)"
    else:
        p_index = model.predict_proba(pd.DataFrame([feats])[FEATURES])[0][1]
        plan = "index_scan" if p_index >= 0.5 else "full_scan"
        confidence, source = max(p_index, 1 - p_index), "random forest"

    baseline_rows, baseline_ms = execute(con, *build_sql(query, "full_scan"))
    if plan == "full_scan":
        rows, chosen_ms = baseline_rows, baseline_ms
    else:
        rows, chosen_ms = execute(con, *build_sql(query, plan, index))

    return {
        "features": feats,
        "index": index,
        "plan": plan,
        "source": source,
        "confidence": confidence,
        "rule_plan": rule_plan,
        "rows_returned": len(rows),
        "baseline_ms": baseline_ms,
        "chosen_ms": chosen_ms,
        "improvement_pct": 100 * (baseline_ms - chosen_ms) / baseline_ms if baseline_ms else 0.0,
        "sample": rows[:sample],
    }
