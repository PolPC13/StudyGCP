import sqlite3
import csv
from pathlib import Path

DB_PATH = Path("exam.db")
CSV_PATH = Path("data/processed/questions.csv")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(row["source_question_number"]) if row["source_question_number"] else None,
                row["question_text"],
                row["option_a"],
                row["option_b"],
                row["option_c"],
                row["option_d"],
                row["correct_answer"].strip(),
                row["explanation_a"],
                row["explanation_b"],
                row["explanation_c"],
                row["explanation_d"],
                row["source_file"],
                row.get("topic", None),
            )
            for row in reader
        ]

    cur.executemany("""
        INSERT INTO questions (
            source_question_number,
            question_text,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer,
            explanation_a,
            explanation_b,
            explanation_c,
            explanation_d,
            source_file,
            topic
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, rows)

    conn.commit()
    conn.close()
    print(f"Importadas {len(rows)} preguntas desde {CSV_PATH} a {DB_PATH}")

if __name__ == "__main__":
    main()