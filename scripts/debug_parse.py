from docx import Document
from pathlib import Path
import re

RAW_DIR = Path("data/raw")

def debug_parse(filepath):
    """Debug version of parse_questions that tracks when question_text becomes empty"""
    doc = Document(filepath)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    def _parse_option_line(line):
        """Detect an option line and return (LETTER, text) or (None, None)."""
        cleaned = line.lstrip(" \t•*-\u2022")
        m = re.match(r"^([A-Da-d])(?:\s*[:\)\.\-]|\s+)(.*)$", cleaned)
        if m:
            return m.group(1).upper(), m.group(2).strip()
        return None, None
    
    questions_with_empty_text = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if line.startswith("Question "):
            q_number_match = re.match(r"Question\s+(\d+)", line)
            source_question_number = q_number_match.group(1) if q_number_match else ""
            
            i += 1
            
            # Collect question text until first option
            question_parts = []
            while i < len(lines):
                letter, _ = _parse_option_line(lines[i])
                if letter or lines[i].startswith("Correct Answer:") or lines[i].startswith("Explanation:") or lines[i].startswith("Question "):
                    break
                question_parts.append(lines[i])
                i += 1
            
            question_text = " ".join(question_parts).strip()
            
            if not question_text:
                next_line_preview = lines[i][:100] if i < len(lines) else "EOF"
                questions_with_empty_text.append({
                    'q_number': source_question_number,
                    'reason': f'next line type: {next_line_preview}'
                })
        else:
            i += 1
    
    return questions_with_empty_text

print("Buscando preguntas con question_text vacío por archivo:\n")

for docx_file in sorted(RAW_DIR.glob("*.docx")):
    print(f"Archivo: {docx_file.name}")
    problematic = debug_parse(docx_file)
    
    if problematic:
        print(f"  ⚠️  {len(problematic)} pregunta(s) problemática(s):")
        for item in problematic:
            print(f"    Question {item['q_number']}: {item['reason']}")
    else:
        print(f"  ✓ Todas las preguntas tienen texto")
    print()
