import sqlite3

DB_PATH = "exam.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total de preguntas
    cursor.execute('SELECT COUNT(*) FROM questions')
    total = cursor.fetchone()[0]
    print(f'✓ Total preguntas en BD: {total}')
    
    # Verificar que hay explicaciones
    cursor.execute('SELECT COUNT(*) FROM questions WHERE explanation_a IS NOT NULL AND explanation_a != ""')
    with_expl_a = cursor.fetchone()[0]
    print(f'✓ Preguntas con explicación A: {with_expl_a}')
    
    cursor.execute('SELECT COUNT(*) FROM questions WHERE explanation_b IS NOT NULL AND explanation_b != ""')
    with_expl_b = cursor.fetchone()[0]
    print(f'✓ Preguntas con explicación B: {with_expl_b}')
    
    cursor.execute('SELECT COUNT(*) FROM questions WHERE explanation_c IS NOT NULL AND explanation_c != ""')
    with_expl_c = cursor.fetchone()[0]
    print(f'✓ Preguntas con explicación C: {with_expl_c}')
    
    cursor.execute('SELECT COUNT(*) FROM questions WHERE explanation_d IS NOT NULL AND explanation_d != ""')
    with_expl_d = cursor.fetchone()[0]
    print(f'✓ Preguntas con explicación D: {with_expl_d}')
    
    # Ejemplo de pregunta completa
    print('\n--- Ejemplo de Pregunta Completa ---')
    cursor.execute('''
        SELECT id, question_text, option_a, option_b, option_c, option_d, 
               correct_answer, explanation_a, explanation_b, explanation_c, explanation_d 
        FROM questions 
        WHERE explanation_a IS NOT NULL AND explanation_a != ""
        LIMIT 1
    ''')
    row = cursor.fetchone()
    if row:
        print(f'ID: {row[0]}')
        print(f'Pregunta: {row[1][:100]}...')
        print(f'Opciones: A) {row[2][:50]}... B) {row[3][:50]}...')
        print(f'Respuesta correcta: {row[6]}')
        print(f'Explicación A (primeros 100 chars): {row[7][:100]}...')
    
    conn.close()

if __name__ == "__main__":
    main()
