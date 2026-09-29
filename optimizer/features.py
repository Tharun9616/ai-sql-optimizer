import math

from .db import COL_INDEX

FEATURES = ["log_rows", "selectivity", "index_selectivity", "n_conditions", "n_indexed", "has_equality"]


def extract(query, stats):
    sels = [(f, stats.selectivity(f)) for f in query["filters"]]
    total = 1.0
    for _, s in sels:
        total *= s
    indexed = [s for f, s in sels if f["column"] in COL_INDEX]
    return {
        "log_rows": math.log10(stats.rows),
        "selectivity": total,
        "index_selectivity": min(indexed) if indexed else 1.0,
        "n_conditions": len(sels),
        "n_indexed": len(indexed),
        "has_equality": int(any(f["operator"] == "=" for f, _ in sels)),
    }
