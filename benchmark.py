import csv
import os
import random
import sys

from optimizer.db import COL_INDEX, DEPARTMENTS, get_connection
from optimizer.features import extract
from optimizer.parser import parse
from optimizer.plans import best_index, build_sql, execute
from optimizer.stats import Stats

SIZES = [10_000, 50_000, 100_000, 200_000]


def condition(rng, col, rows):
    if col == "cgpa":
        return f"cgpa {rng.choice(['<', '<=', '>', '>='])} {round(rng.uniform(4, 10), 1)}"
    if col == "department":
        return f"department = '{rng.choice(DEPARTMENTS)}'"
    if col == "id":
        return f"id {rng.choice(['=', '<', '>'])} {rng.randint(1, rows)}"
    return f"year = {rng.randint(1, 4)}"


def random_sql(rng, rows):
    cols = rng.sample(["cgpa", "department", "id", "year"], rng.choice([1, 1, 2, 3]))
    if not any(c in COL_INDEX for c in cols):
        cols.append("cgpa")
    return "SELECT * FROM students WHERE " + " AND ".join(condition(rng, c, rows) for c in cols)


def main(per_size=300):
    rng = random.Random(7)
    out = []
    for size in SIZES:
        con = get_connection(size)
        stats = Stats(con)
        for _ in range(per_size):
            sql = random_sql(rng, size)
            q = parse(sql)
            idx = best_index(q, stats)
            _, full_ms = execute(con, *build_sql(q, "full_scan"))
            _, index_ms = execute(con, *build_sql(q, "index_scan", idx))
            out.append({"rows": size, "query": sql, **extract(q, stats), "full_ms": full_ms, "index_ms": index_ms})
        con.close()
        print(f"{size:>7} rows done")
    os.makedirs("benchmarks", exist_ok=True)
    with open("benchmarks/query_data.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"saved {len(out)} queries to benchmarks/query_data.csv")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
