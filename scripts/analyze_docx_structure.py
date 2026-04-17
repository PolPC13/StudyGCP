from docx import Document
from pathlib import Path
import re

RAW_DIR = Path("data/raw")

def analyze_docx_line_by_line(filepath):
    doc = Document(filepath)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    question_numbers = []
    for i, line in enumerate(lines):
        if line.startswith("Question "):
            q_match = re.match(r"Question\s+(\d+)", line)
            q_num = q_match.group(1) if q_match else "?"
            next_line = lines[i+1] if i+1 < len(lines) else "EOF"
            question_numbers.append((q_num, next_line[:100]))
    
    return question_numbers

print("Analizando estructura de preguntas en archivos DOCX:\n")

for docx_file in sorted(RAW_DIR.glob("*.docx")):
    print(f"Archivo: {docx_file.name}")
    print("-" * 80)
    
    questions = analyze_docx_line_by_line(docx_file)
    
    # Mostrar solo los primeros 5 ejemplos por archivo
    for q_num, next_line in questions[:5]:
        print(f"  Question {q_num} → Siguiente línea: {next_line}")
    
    if len(questions) > 5:
        print(f"  ... y {len(questions) - 5} preguntas más")
    
    # Mostrar también si hay algo extraño
    problematic = []
    for q_num, next_line in questions:
        if not next_line or next_line.startswith("Question ") or next_line.startswith("Correct"):
            problematic.append((q_num, next_line))
    
    if problematic:
        print(f"\n  ⚠️  PREGUNTAS POTENCIALMENTE PROBLEMÁTICAS:")
        for q_num, next_line in problematic[:3]:
            print(f"    Question {q_num} → {next_line[:80]}")
    
    print()
