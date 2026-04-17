import sqlite3
import random
from pathlib import Path

DB_PATH = Path("exam.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM questions;")
    total = cur.fetchone()[0]
    print(f"Total preguntas en BD: {total}")

    cur.execute("""
        SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer
        FROM questions
        ORDER BY RANDOM()
        LIMIT 1;
    """)
    row = cur.fetchone()
    conn.close()

    if not row:
        print("No hay preguntas.")
        return

    id_, q, a, b, c, d, correct = row
    print(f"\nID {id_}")
    print(q)
    print("A)", a)
    print("B)", b)
    print("C)", c)
    print("D)", d)
    print("Correcta:", correct)

if __name__ == "__main__":
    main()