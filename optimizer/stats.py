import bisect
import operator

OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "=": operator.eq}


class Stats:
    def __init__(self, con, table="students"):
        self.rows = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        self.categorical, self.quantiles, self.distinct = {}, {}, {}
        for _, col, ctype, *_ in con.execute(f"PRAGMA table_info({table})").fetchall():
            d = con.execute(f"SELECT COUNT(DISTINCT {col}) FROM {table}").fetchone()[0]
            self.distinct[col] = d
            if d <= 50:
                self.categorical[col] = dict(
                    con.execute(f"SELECT {col}, COUNT(*) FROM {table} GROUP BY {col}").fetchall()
                )
            elif ctype.upper() != "TEXT":
                vals = [r[0] for r in con.execute(f"SELECT {col} FROM {table} ORDER BY {col}")]
                n = len(vals)
                self.quantiles[col] = [vals[i * (n - 1) // 100] for i in range(101)]

    def selectivity(self, f):
        col, op, val = f["column"], f["operator"], f["value"]
        if col in self.categorical:
            try:
                hits = sum(c for v, c in self.categorical[col].items() if OPS[op](v, val))
            except TypeError:
                hits = 0
            s = hits / self.rows
        elif col in self.quantiles:
            if op == "=":
                s = 1 / self.distinct[col]
            else:
                q = self.quantiles[col]
                le = bisect.bisect_right(q, val) / len(q)
                lt = bisect.bisect_left(q, val) / len(q)
                s = {"<": lt, "<=": le, ">": 1 - le, ">=": 1 - lt}[op]
        else:
            s = 1 / max(self.distinct.get(col, 1), 1) if op == "=" else 0.5
        return min(1.0, max(s, 1 / self.rows))
