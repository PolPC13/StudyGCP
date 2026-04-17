from docx import Document
import csv
import re
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_CSV = Path("data/processed/questions.csv")

def read_docx_lines(path):
    doc = Document(path)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return lines

def parse_questions(lines, source_file):
    questions = []
    i = 0

    def _parse_option_line(line):
        """Detect an option line and return (LETTER, text) or (None, None).

        Matches variants like:
        - A) text
        - A. text
        - (A) text
        - •\tB text
        - B - text
        - a) text
        
        Does NOT match:
        - Correct, Explanation, etc
        - Text that happens to start with A/B/C/D like "A marketing team..."
        """
        # Remove common leading bullet characters and whitespace
        cleaned = line.lstrip(" \t•*-\u2022")
        
        # STRICTER: Must start with letter A-D followed by:
        # - closing paren: ) 
        # - colon: :
        # - period: .
        # - dash/hyphen: -
        # OR exactly one space followed by non-letter (to avoid "A marketing" matching)
        m = re.match(r"^([A-Da-d])[:\)\.\-](.*)$", cleaned)
        if m:
            return m.group(1).upper(), m.group(2).strip()
        
        # Also match: "A " or "B " etc but only if NOT followed by a lowercase word
        m = re.match(r"^([A-Da-d])\s+([A-Z].*)$", cleaned)
        if m:
            return m.group(1).upper(), m.group(2).strip()
        
        return None, None

    while i < len(lines):
        line = lines[i]

        if line.startswith("Question "):
            q_number_match = re.match(r"Question\s+(\d+)", line)
            source_question_number = q_number_match.group(1) if q_number_match else ""

            i += 1

            # Collect question text until the first option or until Correct/Explanation/next Question
            question_parts = []
            while i < len(lines):
                letter, _ = _parse_option_line(lines[i])
                if letter or lines[i].startswith("Correct Answer:") or lines[i].startswith("Explanation:") or lines[i].startswith("Question "):
                    break
                question_parts.append(lines[i])
                i += 1
            question_text = " ".join(question_parts).strip()

            # Parse options A-D. Options can span multiple lines.
            options = {"A": "", "B": "", "C": "", "D": ""}
            while i < len(lines):
                letter, text = _parse_option_line(lines[i])
                if not letter:
                    break
                options[letter] = text
                i += 1
                # gather continuation lines for this option
                while i < len(lines):
                    next_letter, _ = _parse_option_line(lines[i])
                    if next_letter or lines[i].startswith("Correct Answer:") or lines[i].startswith("Explanation:") or lines[i].startswith("Question "):
                        break
                    options[letter] += " " + lines[i].strip()
                    i += 1

            option_a = options.get("A", "")
            option_b = options.get("B", "")
            option_c = options.get("C", "")
            option_d = options.get("D", "")

            correct_answer = ""
            if i < len(lines) and lines[i].startswith("Correct Answer:"):
                correct_answer = lines[i].split(":", 1)[1].strip()
                i += 1

            # Skip a bare Explanation: header if present
            if i < len(lines) and lines[i].startswith("Explanation:"):
                i += 1

            explanation_a = ""
            explanation_b = ""
            explanation_c = ""
            explanation_d = ""
            last_expl = None

            # Parse explanation lines until next question
            while i < len(lines) and not lines[i].startswith("Question "):
                ln = lines[i].lstrip()
                # Remove leading bullets/dashes but preserve structure
                ln_stripped = ln.lstrip("•*-\u2022 \t")
                
                # Skip empty lines
                if not ln_stripped:
                    i += 1
                    continue
                
                # Improved regex: captures letter followed by colon, paren, period, dash, or space
                # Matches: "A is correct", "A) text", "A: text", "A. text", "A - text"
                m = re.match(r"^([A-Da-d])[\s:\)\.\-]*(.+)$", ln_stripped)
                if m:
                    opt = m.group(1).upper()
                    expl = m.group(2).strip()
                    if opt == "A":
                        explanation_a = expl
                    elif opt == "B":
                        explanation_b = expl
                    elif opt == "C":
                        explanation_c = expl
                    elif opt == "D":
                        explanation_d = expl
                    last_expl = opt
                else:
                    # continuation of last explanation
                    if last_expl and ln_stripped:
                        text_to_append = ln_stripped.strip()
                        if last_expl == "A":
                            explanation_a = (explanation_a + " " + text_to_append).strip()
                        elif last_expl == "B":
                            explanation_b = (explanation_b + " " + text_to_append).strip()
                        elif last_expl == "C":
                            explanation_c = (explanation_c + " " + text_to_append).strip()
                        elif last_expl == "D":
                            explanation_d = (explanation_d + " " + text_to_append).strip()
                i += 1

            topic = Path(source_file).stem

            questions.append({
                "source_question_number": source_question_number,
                "question_text": question_text,
                "option_a": option_a,
                "option_b": option_b,
                "option_c": option_c,
                "option_d": option_d,
                "correct_answer": correct_answer,
                "explanation_a": explanation_a,
                "explanation_b": explanation_b,
                "explanation_c": explanation_c,
                "explanation_d": explanation_d,
                "source_file": source_file,
                "topic": topic,
            })
        else:
            i += 1

    return questions

def main():
    all_questions = []

    for docx_file in RAW_DIR.glob("*.docx"):
        lines = read_docx_lines(docx_file)
        parsed = parse_questions(lines, docx_file.name)
        all_questions.extend(parsed)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_question_number",
                "question_text",
                "option_a",
                "option_b",
                "option_c",
                "option_d",
                "correct_answer",
                "explanation_a",
                "explanation_b",
                "explanation_c",
                "explanation_d",
                "source_file",
                "topic",
            ],
        )
        writer.writeheader()
        writer.writerows(all_questions)

    print(f"CSV generado en: {OUT_CSV}")
    print(f"Total preguntas: {len(all_questions)}")

if __name__ == "__main__":
    main()