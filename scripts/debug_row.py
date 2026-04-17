import csv
from pathlib import Path

CSV_PATH = Path("data/processed/questions.csv")

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
    # Mirar la pregunta #4 (Index 4 = fila 5)
    print("=" * 80)
    print("PREGUNTA #4 (fila 5) - INCOMPLETA:")
    print("=" * 80)
    row = rows[4]
    print(f"source_question_number: {row['source_question_number']}")
    print(f"question_text: '{row['question_text']}'")
    print(f"option_a: {row['option_a'][:80]}")
    print(f"option_b: {row['option_b'][:80]}")
    print(f"option_c: {row['option_c'][:80]}")
    print(f"option_d: {row['option_d'][:80]}")
    print(f"correct_answer: '{row['correct_answer']}'")
    print()
    
    print("=" * 80)
    print("PREGUNTA #3 (fila 4) - COMPLETA (para comparación):")
    print("=" * 80)
    row = rows[3]
    print(f"source_question_number: {row['source_question_number']}")
    print(f"question_text: {row['question_text'][:150]}...")
    print(f"option_a: {row['option_a'][:80]}")
    print(f"option_b: {row['option_b'][:80]}")
    print(f"option_c: {row['option_c'][:80]}")
    print(f"option_d: {row['option_d'][:80]}")
    print(f"correct_answer: '{row['correct_answer']}'")
