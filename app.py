from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from pathlib import Path
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Para sesiones
DB_PATH = Path("exam.db")

# Mapeo de nombres de topics para una mejor presentación visual
TOPIC_DISPLAY_NAMES = {
    "Data_analysis": "Data Analysis and Presentation",
    "Data_management": "Data Management",
    "Data_pipeline_orchestration": "Data Pipeline Orchestration",
    "Data_preparation": "Data Preparation and Ingestion"
}

def get_display_name(topic):
    """Obtiene el nombre de visualización para un topic"""
    return TOPIC_DISPLAY_NAMES.get(topic, topic)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_topics():
    """Obtiene todos los topics únicos en la BD"""
    conn = get_db_connection()
    topics = conn.execute("""
        SELECT DISTINCT topic FROM questions WHERE topic IS NOT NULL
        ORDER BY topic
    """).fetchall()
    conn.close()
    return [row["topic"] for row in topics]

def get_total_questions():
    """Obtiene el total de preguntas en la BD"""
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) as count FROM questions").fetchone()["count"]
    conn.close()
    return total

def get_questions_count_by_topic(topic):
    """Obtiene el total de preguntas en un tema específico"""
    conn = get_db_connection()
    total = conn.execute(
        "SELECT COUNT(*) as count FROM questions WHERE topic = ?",
        (topic,)
    ).fetchone()["count"]
    conn.close()
    return total

def get_all_questions(topic_filter=None):
    """Obtiene lista de todas las preguntas (metadatos para listado)"""
    conn = get_db_connection()
    
    if topic_filter and topic_filter != "all":
        questions = conn.execute("""
            SELECT id, source_question_number, question_text, topic, correct_answer
            FROM questions
            WHERE topic = ?
            ORDER BY source_question_number
        """, (topic_filter,)).fetchall()
    else:
        questions = conn.execute("""
            SELECT id, source_question_number, question_text, topic, correct_answer
            FROM questions
            ORDER BY source_question_number
        """).fetchall()
    
    conn.close()
    return [dict(q) for q in questions]

def get_random_question(topic_filter=None):
    """Obtiene una pregunta aleatoria, opcionalmente filtrada por topic"""
    conn = get_db_connection()
    
    if topic_filter and topic_filter != "all":
        question = conn.execute("""
            SELECT id, question_text, option_a, option_b, option_c, option_d,
                   correct_answer, explanation_a, explanation_b, explanation_c, 
                   explanation_d, topic, source_question_number
            FROM questions
            WHERE topic = ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (topic_filter,)).fetchone()
    else:
        question = conn.execute("""
            SELECT id, question_text, option_a, option_b, option_c, option_d,
                   correct_answer, explanation_a, explanation_b, explanation_c, 
                   explanation_d, topic, source_question_number
            FROM questions
            ORDER BY RANDOM()
            LIMIT 1
        """).fetchone()
    
    conn.close()
    return question

def get_question_by_id(question_id):
    """Obtiene una pregunta por ID"""
    conn = get_db_connection()
    question = conn.execute("""
        SELECT id, question_text, option_a, option_b, option_c, option_d,
               correct_answer, explanation_a, explanation_b, explanation_c, 
               explanation_d, topic, source_question_number
        FROM questions
        WHERE id = ?
    """, (question_id,)).fetchone()
    conn.close()
    return question

def get_ordered_question(topic_filter=None, order="random", pool_index=0):
    """Obtiene pregunta del pool ordenado o aleatoria (sin acceder a session)"""
    conn = get_db_connection()
    
    if order == "asc":
        # Modo ascendente: obtener de lista ordenada por índice
        if topic_filter and topic_filter != "all":
            questions = conn.execute("""
                SELECT id FROM questions
                WHERE topic = ?
                ORDER BY source_question_number ASC
            """, (topic_filter,)).fetchall()
        else:
            questions = conn.execute("""
                SELECT id FROM questions
                ORDER BY source_question_number ASC
            """).fetchall()
        
        conn.close()
        
        if questions and pool_index < len(questions):
            question_id = questions[pool_index]["id"]
            return get_question_by_id(question_id), len(questions), pool_index
        else:
            return None, len(questions) if questions else 0, pool_index
    else:  # random
        if topic_filter and topic_filter != "all":
            question = conn.execute("""
                SELECT id FROM questions
                WHERE topic = ?
                ORDER BY RANDOM()
                LIMIT 1
            """, (topic_filter,)).fetchone()
        else:
            question = conn.execute("""
                SELECT id FROM questions
                ORDER BY RANDOM()
                LIMIT 1
            """).fetchone()
        
        conn.close()
        if question:
            return get_question_by_id(question["id"]), 1, 0
        return None, 0, 0

def get_question_position_in_topic(question_id):
    """Obtiene la posición (numero) de una pregunta dentro de su tema"""
    conn = get_db_connection()
    
    # Obtener tema de la pregunta
    question = conn.execute(
        "SELECT topic FROM questions WHERE id = ?",
        (question_id,)
    ).fetchone()
    
    if not question:
        conn.close()
        return None, None
    
    topic = question["topic"]
    
    # Contar cuántas preguntas del mismo tema vienen antes (ordenadas por source_question_number)
    position = conn.execute(
        """SELECT COUNT(*) as count FROM questions 
           WHERE topic = ? AND source_question_number <= (
               SELECT source_question_number FROM questions WHERE id = ?
           )""",
        (topic, question_id)
    ).fetchone()["count"]
    
    # Total de preguntas en el tema
    total = conn.execute(
        "SELECT COUNT(*) as count FROM questions WHERE topic = ?",
        (topic,)
    ).fetchone()["count"]
    
    conn.close()
    return position, total

def initialize_session():
    """Inicializa el contador de la sesión"""
    if "score" not in session:
        session["score"] = {"correct": 0, "total": 0}
    if "selected_topic" not in session:
        session["selected_topic"] = "all"

@app.route("/", methods=["GET"])
def home():
    initialize_session()
    topic_filter = request.args.get("topic", session.get("selected_topic", "all"))
    order = request.args.get("order", "random")  # random o asc
    session["selected_topic"] = topic_filter
    session["order"] = order
    
    # Obtener pool index si estamos en modo asc
    pool_index = session.get("question_pool_index", 0)
    
    question, pool_length, pool_index = get_ordered_question(topic_filter, order, pool_index)
    
    # Guardar el índice en sesión
    session["question_pool_index"] = pool_index
    session["question_pool_length"] = pool_length
    session.modified = True
    
    topics = get_all_topics()
    total_questions = get_total_questions()
    
    # Obtener posición en el tema
    question_pos = None
    question_total = None
    if question:
        question_pos, question_total = get_question_position_in_topic(question["id"])
    
    return render_template(
        "question.html",
        question=question,
        answered=False,
        topics=topics,
        current_topic=topic_filter,
        current_order=order,
        score=session.get("score", {"correct": 0, "total": 0}),
        total_questions=total_questions,
        question_pos=question_pos,
        question_total=question_total,
        topic_display_names=TOPIC_DISPLAY_NAMES
    )

@app.route("/answer", methods=["POST"])
def answer():
    initialize_session()
    question_id = int(request.form.get("question_id"))
    selected = request.form.get("selected_option")
    topic_filter = request.form.get("topic_filter", "all")

    if not question_id or not selected:
        return redirect(url_for("home"))

    question = get_question_by_id(question_id)
    if question is None:
        return redirect(url_for("home"))

    is_correct = selected == question["correct_answer"]
    
    # Actualizar contador
    session["score"]["total"] += 1
    if is_correct:
        session["score"]["correct"] += 1
    session.modified = True
    
    # Obtener explicaciones indexadas por opción
    explanations = {
        "A": question["explanation_a"],
        "B": question["explanation_b"],
        "C": question["explanation_c"],
        "D": question["explanation_d"]
    }
    
    topics = get_all_topics()
    total_questions = get_total_questions()
    
    # Obtener posición en el tema
    question_pos, question_total = get_question_position_in_topic(question["id"])

    return render_template(
        "question.html",
        question=question,
        answered=True,
        selected=selected,
        is_correct=is_correct,
        explanations=explanations,
        topics=topics,
        current_topic=topic_filter,
        current_order=request.form.get("order", "random"),
        score=session.get("score", {"correct": 0, "total": 0}),
        total_questions=total_questions,
        question_pos=question_pos,
        question_total=question_total,
        topic_display_names=TOPIC_DISPLAY_NAMES
    )

@app.route("/questions", methods=["GET"])
def questions_list():
    """Devuelve lista de todas las preguntas"""
    initialize_session()
    topic_filter = request.args.get("topic", "all")
    order = request.args.get("order", "random")
    
    all_questions = get_all_questions(topic_filter)
    total_questions = get_total_questions()
    topics = get_all_topics()
    
    return render_template(
        "questions_list.html",
        questions=all_questions,
        topics=topics,
        current_topic=topic_filter,
        current_order=order,
        total_questions=total_questions,
        score=session.get("score", {"correct": 0, "total": 0}),
        topic_display_names=TOPIC_DISPLAY_NAMES
    )

@app.route("/question/<int:question_id>", methods=["GET"])
def view_question(question_id):
    """Carga una pregunta específica por ID"""
    initialize_session()
    
    question = get_question_by_id(question_id)
    if question is None:
        return redirect(url_for("home"))
    
    topics = get_all_topics()
    total_questions = get_total_questions()
    
    # Obtener posición en el tema
    question_pos, question_total = get_question_position_in_topic(question["id"])
    
    return render_template(
        "question.html",
        question=question,
        answered=False,
        topics=topics,
        current_topic="all",
        current_order="random",
        score=session.get("score", {"correct": 0, "total": 0}),
        total_questions=total_questions,
        question_pos=question_pos,
        question_total=question_total,
        from_list=True,
        topic_display_names=TOPIC_DISPLAY_NAMES
    )

@app.route("/next", methods=["GET"])
def next_question():
    initialize_session()
    topic_filter = request.args.get("topic", session.get("selected_topic", "all"))
    order = request.args.get("order", session.get("order", "random"))
    
    # Si estamos en modo ascendente, incrementar el índice del pool
    if order == "asc":
        session["question_pool_index"] = session.get("question_pool_index", 0) + 1
        session.modified = True
    
    return redirect(url_for("home", topic=topic_filter, order=order))

@app.route("/retry", methods=["GET"])
def retry_question():
    """Vuelve a la pregunta anterior sin mostrar resultado"""
    initialize_session()
    question_id = request.args.get("question_id", type=int)
    
    if question_id:
        return redirect(url_for("view_question", question_id=question_id))
    
    return redirect(url_for("home"))

@app.route("/previous", methods=["GET"])
def previous_question():
    """Va a la pregunta anterior sin mostrar resultado"""
    initialize_session()
    question_id = request.args.get("question_id", type=int)
    topic_filter = request.args.get("topic", "all")
    order = session.get("order", "random")
    
    if not question_id:
        return redirect(url_for("home"))
    
    # Si estamos en modo ascendente, retroceder en el pool
    if order == "asc":
        session["question_pool_index"] = max(0, session.get("question_pool_index", 0) - 1)
        session.modified = True
    
    return redirect(url_for("home", topic=topic_filter, order=order))

@app.route("/reset", methods=["GET"])
def reset():
    """Reinicia el contador"""
    session["score"] = {"correct": 0, "total": 0}
    session.modified = True
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)