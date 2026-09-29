import re

QUERY = re.compile(
    r"^\s*SELECT\s+(?P<cols>.+?)\s+FROM\s+(?P<table>\w+)"
    r"(?:\s+WHERE\s+(?P<where>.+?))?"
    r"(?:\s+ORDER\s+BY\s+(?P<order>\w+(?:\s+(?:ASC|DESC))?))?"
    r"(?:\s+LIMIT\s+(?P<limit>\d+))?\s*;?\s*$",
    re.I | re.S,
)
CONDITION = re.compile(r"^\s*(\w+)\s*(<=|>=|=|<|>)\s*('[^']*'|-?\d+(?:\.\d+)?)\s*$")


def _value(raw):
    if raw.startswith("'"):
        return raw[1:-1]
    return float(raw) if "." in raw else int(raw)


def parse(sql):
    m = QUERY.match(sql)
    if not m:
        raise ValueError("Unsupported query. Use SELECT ... FROM ... [WHERE a op v AND ...] [ORDER BY c] [LIMIT n]")
    filters = []
    if m["where"]:
        for part in re.split(r"\s+AND\s+", m["where"], flags=re.I):
            c = CONDITION.match(part)
            if not c:
                raise ValueError(f"Unsupported condition: {part.strip()}")
            filters.append({"column": c[1], "operator": c[2], "value": _value(c[3])})
    return {
        "table": m["table"],
        "columns": [c.strip() for c in m["cols"].split(",")],
        "filters": filters,
        "order_by": m["order"],
        "limit": int(m["limit"]) if m["limit"] else None,
    }
