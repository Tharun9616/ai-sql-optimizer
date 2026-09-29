import argparse

from optimizer.db import get_connection
from optimizer.engine import load_model, optimize
from optimizer.stats import Stats

ap = argparse.ArgumentParser()
ap.add_argument("sql")
ap.add_argument("--rows", type=int, default=100_000)
args = ap.parse_args()

con = get_connection(args.rows)
r = optimize(con, Stats(con), args.sql, load_model())
conf = f" ({r['confidence']:.1%} confidence)" if r["confidence"] is not None else ""
print(f"Table rows       : {args.rows:,}")
print(f"Selectivity      : {r['features']['selectivity']:.1%}")
print(f"Index available  : {r['index'] or 'none'}")
print(f"Chosen plan      : {r['plan'].upper()}{conf} via {r['source']}")
print(f"Rule-based plan  : {r['rule_plan'].upper()}")
print(f"Rows returned    : {r['rows_returned']:,}")
print(f"Full scan        : {r['baseline_ms']:.2f} ms")
print(f"Chosen plan      : {r['chosen_ms']:.2f} ms  ({r['improvement_pct']:+.1f}%)")
for row in r["sample"][:5]:
    print(row)
