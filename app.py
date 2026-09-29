import streamlit as st

from optimizer.db import get_connection
from optimizer.engine import load_model, optimize
from optimizer.stats import Stats

st.title("AI SQL Query Optimizer")
rows = st.selectbox("Table size", [10_000, 50_000, 100_000, 200_000], index=2)
sql = st.text_area("Query", "SELECT * FROM students WHERE cgpa > 8.5;")

if st.button("Optimize"):
    con = get_connection(rows)
    try:
        r = optimize(con, Stats(con), sql, load_model())
    except Exception as e:
        st.error(str(e))
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Chosen plan", r["plan"].replace("_", " ").upper())
        c2.metric("Confidence", "n/a" if r["confidence"] is None else f"{r['confidence']:.1%}")
        c3.metric("Estimated selectivity", f"{r['features']['selectivity']:.1%}")
        st.bar_chart({"ms": {"Full scan": r["baseline_ms"], "Chosen plan": r["chosen_ms"]}})
        st.write(f"Improvement: {r['improvement_pct']:+.1f}%  |  Rule-based would pick: {r['rule_plan'].replace('_', ' ')}")
        st.dataframe(r["sample"])
