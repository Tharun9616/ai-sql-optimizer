import re
import statistics
import time

from .db import COL_INDEX

PLANS = ("full_scan", "index_scan")


def best_index(query, stats):
    cands = [
        (stats.selectivity(f), COL_INDEX[f["column"]])
        for f in query["filters"]
        if f["column"] in COL_INDEX
    ]
    return min(cands)[1] if cands else None


def build_sql(query, plan, index=None):
    hint = "NOT INDEXED" if plan == "full_scan" else f"INDEXED BY {index}"
    sql = f"SELECT {', '.join(query['columns'])} FROM {query['table']} {hint}"
    params = []
    if query["filters"]:
        sql += " WHERE " + " AND ".join(f"{f['column']} {f['operator']} ?" for f in query["filters"])
        params = [f["value"] for f in query["filters"]]
    if query["order_by"]:
        sql += f" ORDER BY {query['order_by']}"
    if query["limit"]:
        sql += f" LIMIT {int(query['limit'])}"
    return sql, params


def execute(con, sql, params, repeats=3):
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        rows = con.execute(sql, params).fetchall()
        times.append((time.perf_counter() - start) * 1000)
    return rows, statistics.median(times)


def rule_based(features, threshold=0.30):
    return "index_scan" if features["index_selectivity"] < threshold else "full_scan"
