import sqlite3

conn = sqlite3.connect("sample.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE employees (
    id INTEGER,
    name TEXT,
    salary INTEGER
)
""")

cursor.execute("""
CREATE TABLE departments (
    id INTEGER,
    dept_name TEXT
)
""")

# Insert data
cursor.executemany("INSERT INTO employees VALUES (?, ?, ?)", [
    (1, "Alice", 50000),
    (2, "Bob", 70000),
    (3, "Charlie", 40000),
    (4, "David", 90000)
])

cursor.executemany("INSERT INTO departments VALUES (?, ?)", [
    (1, "HR"),
    (2, "IT"),
    (3, "Finance"),
    (4, "Management")
])

conn.commit()
conn.close()

print("✅ sample.db created!")