import sqlite3
from pathlib import Path

DB_PATH = Path("exam.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    DROP TABLE IF EXISTS questions;
    """)

    cur.execute("""
    CREATE TABLE questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_question_number INTEGER,
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        explanation_a TEXT,
        explanation_b TEXT,
        explanation_c TEXT,
        explanation_d TEXT,
        source_file TEXT,
        topic TEXT
    );
    """)

    conn.commit()
    conn.close()
    print(f"Base de datos creada en {DB_PATH}")

if __name__ == "__main__":
    main()