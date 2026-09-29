import os
import random
import sqlite3

DEPARTMENTS = ["CSE", "ECE", "EEE", "MECH", "CIVIL", "IT"]
DEPT_WEIGHTS = [35, 20, 15, 12, 10, 8]
COL_INDEX = {
    "cgpa": "idx_students_cgpa",
    "department": "idx_students_department",
    "id": "idx_students_id",
}


def build(path, rows, seed=42):
    if os.path.exists(path):
        os.remove(path)
    rng = random.Random(seed)
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE students (id INTEGER, name TEXT, department TEXT, cgpa REAL, year INTEGER)"
    )
    data = (
        (
            i,
            f"Student{i}",
            rng.choices(DEPARTMENTS, DEPT_WEIGHTS)[0],
            round(min(10.0, max(4.0, rng.gauss(7.4, 1.1))), 2),
            rng.randint(1, 4),
        )
        for i in range(1, rows + 1)
    )
    con.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?)", data)
    for col, name in COL_INDEX.items():
        con.execute(f"CREATE INDEX {name} ON students({col})")
    con.commit()
    return con


def get_connection(rows, directory="data"):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"students_{rows}.db")
    if not os.path.exists(path):
        build(path, rows).close()
    return sqlite3.connect(path)
