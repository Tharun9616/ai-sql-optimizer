from optimizer.db import build
from optimizer.parser import parse
from optimizer.plans import build_sql, execute
from optimizer.stats import Stats


def test_parse():
    q = parse("SELECT name, cgpa FROM students WHERE cgpa > 8.0 AND department = 'CSE' LIMIT 5;")
    assert q["columns"] == ["name", "cgpa"]
    assert q["filters"][1] == {"column": "department", "operator": "=", "value": "CSE"}
    assert q["limit"] == 5


def test_plans_return_same_rows(tmp_path):
    con = build(str(tmp_path / "t.db"), 2000)
    q = parse("SELECT * FROM students WHERE cgpa > 8.0")
    full, _ = execute(con, *build_sql(q, "full_scan"), repeats=1)
    idx, _ = execute(con, *build_sql(q, "index_scan", "idx_students_cgpa"), repeats=1)
    assert sorted(full) == sorted(idx)


def test_selectivity_close_to_truth(tmp_path):
    con = build(str(tmp_path / "t.db"), 5000)
    q = parse("SELECT * FROM students WHERE cgpa > 8.0")
    truth = len(con.execute("SELECT 1 FROM students WHERE cgpa > 8.0").fetchall()) / 5000
    assert abs(Stats(con).selectivity(q["filters"][0]) - truth) < 0.03
