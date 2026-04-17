import csv
from pathlib import Path

CSV_PATH = Path("data/processed/questions.csv")

def analyze_csv():
    missing_data = []
    total_rows = 0
    
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
            total_rows += 1
            issues = []
            
            # Check for empty critical fields
            if not row["question_text"] or row["question_text"].strip() == "":
                issues.append("question_text VACÍO")
            
            if not row["option_a"] or row["option_a"].strip() == "":
                issues.append("option_a VACÍO")
                
            if not row["option_b"] or row["option_b"].strip() == "":
                issues.append("option_b VACÍO")
                
            if not row["option_c"] or row["option_c"].strip() == "":
                issues.append("option_c VACÍO")
                
            if not row["option_d"] or row["option_d"].strip() == "":
                issues.append("option_d VACÍO")
            
            if not row["correct_answer"] or row["correct_answer"].strip() == "":
                issues.append("correct_answer VACÍO")
            
            if issues:
                missing_data.append({
                    "row_num": row_num,
                    "source_question_number": row.get("source_question_number", "?"),
                    "issues": issues
                })
    
    print(f"Total filas procesadas: {total_rows}")
    print(f"Filas con datos faltantes: {len(missing_data)}\n")
    
    if missing_data:
        print("FILAS CON PROBLEMAS:")
        print("-" * 80)
        for item in missing_data:
            print(f"Fila {item['row_num']} (Pregunta #{item['source_question_number']}):")
            for issue in item['issues']:
                print(f"  ❌ {issue}")
            print()
    else:
        print("✓ Todas las filas tienen datos completos")

if __name__ == "__main__":
    analyze_csv()
