# GCP Study App

An interactive web application for studying Google Cloud Platform questions with detailed explanations, topic filtering, and score tracking.

## Overview

This application provides 110 practice questions across four Google Cloud study domains:
- Data Analysis and Presentation
- Data Management
- Data Pipeline Orchestration
- Data Preparation and Ingestion

Questions are sourced from online documentation and educational materials, with some synthetically generated to complement the curriculum. Each question includes detailed explanations for all answer options.

## Features

- 110 GCP practice questions with 4 options each
- Detailed explanations for every option
- Topic filtering to focus on specific areas
- Session-based score tracking (X/Y format)
- Responsive design for desktop, tablet, and mobile
- Question selection from full list
- Random question generation

## Requirements

- Python 3.8+
- pip

## Installation

1. Clone or download this repository
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify the database:
   ```bash
   python scripts/verify_db.py
   ```

## Running the Application

Start the application:
```bash
python app.py
```

Open your browser and navigate to `http://localhost:5000`

To stop the application, press `CTRL+C` in the terminal.

## Project Structure

```
├── app.py                          # Flask application
├── requirements.txt                # Python dependencies
├── data/
│   └── processed/
│       └── questions.csv           # Question data
├── scripts/
│   ├── create_db.py               # Initialize SQLite database
│   ├── import_csv_to_sqlite.py    # Import questions from CSV
│   ├── docx_to_csv.py             # Convert DOCX to CSV format
│   └── verify_db.py               # Verify database integrity
└── templates/
    ├── question.html              # Question display template
    └── questions_list.html        # Questions list template
```

## Technologies

- Flask - Web framework
- SQLite - Database
- Python - Backend language
| `/questions` | GET | Muestra lista de todas las preguntas |
| `/questions?topic=Data_analysis` | GET | Lista filtrada por tema |
| `/question/<id>` | GET | Carga pregunta específica por ID |
| `/reset` | GET | Reinicia contador |

---

## 🆕 Selector de Preguntas (Nueva Funcionalidad)

### Cómo Operador el Selector

#### Acceso a la Lista
- **Opción 1:** Click en botón "📋 Ver Lista" en la esquina superior derecha
- **Opción 2:** Ir directamente a `http://localhost:5000/questions`

#### Características de la Lista
- **Grid Responsivo:** Muestra preguntas en tarjetas
- **Vista Previa:** Cada tarjeta muestra:
  - Número de pregunta (Q1, Q2, etc.)
  - Primeras 2 líneas de la pregunta
  - Tema correspondiente
  
- **Filtrado:** Igual que en la página principal
  - "Todos" - todas las preguntas
  - Botones por tema
  - La URL actualiza dinámicamente

- **Selección:** Click en cualquier tarjeta lleva a esa pregunta específica

#### Flujo de Usuario
```
1. En página de pregunta aleatoria
2. Click en "📋 Ver Lista"
3. Se abre página con listado
4. Filtra por tema (opcional)
5. Click en pregunta que quieres ver
6. Se carga ese pregunta específica
7. Responde y vuelve a lista si quieres
```

#### Contador Mejorado
```
ANTES: X / Y
DESPUÉS: X / Y (de 110 preguntas)
```
- Muestra aciertos/intentos de la sesión
- Muestra total de preguntas en BD
- Se actualiza en tiempo real

---

## 📝 Añadir o Modificar Preguntas

### Opción 1: Editar el CSV Directamente (Más Rápido)

Si solo quieres **modificar** preguntas existentes:

#### Paso 1: Abre el CSV

```
data/processed/questions.csv
```

#### Paso 2: Estructura del CSV

```
source_question_number,question_text,option_a,option_b,option_c,option_d,correct_answer,explanation_a,explanation_b,explanation_c,explanation_d,source_file,topic
1,"¿Preguntas?",...,...,...,...,B,"Por que A es mal","Por que B es bien",...,...,archivo.docx,Data_analysis
```

**Campos obligatorios:**
- `source_question_number` - Número único (ej: 1, 2, 3...)
- `question_text` - Texto de la pregunta
- `option_a, option_b, option_c, option_d` - Las 4 opciones
- `correct_answer` - Letra de la respuesta correcta (A, B, C, D)
- `explanation_a, explanation_b, explanation_c, explanation_d` - Explicaciones de por qué
- `topic` - Categoría (ej: Data_analysis, Data_management)

#### Paso 3: Recrear BD desde CSV

```bash
python scripts/create_db.py
python scripts/import_csv_to_sqlite.py
```

#### Paso 4: Verifica

```bash
python scripts/verify_db.py
```

---

### Opción 2: Añadir Preguntas desde DOCX (Recomendado para Volumen)

Si quieres **añadir muchas preguntas nuevas** desde un archivo DOCX:

#### Paso 1: Crear Archivo DOCX

Crea un nuevo archivo en `data/raw/` con el siguiente formato:

```
Question 1
¿Cuál es el tema principal de esta pregunta?
A) Primera opción
B) Segunda opción
C) Tercera opción
D) Cuarta opción
Correct Answer: B
Explanation:
• B es correcto porque...
• A es incorrecto porque...
• C es incorrecto porque...
• D es incorrecto porque...

Question 2
¿Otra pregunta?
...
```

**Reglas importantes:**
- Cada pregunta comienza con `Question N`
- Opciones: `A)`, `B)`, `C)`, `D)` (o `A:`, `A.`, `A -`, etc.)
- Respuesta correcta: `Correct Answer: X`
- Explicaciones: Con viñetas `• A`, `• B`, `• C`, `• D`
- Las explicaciones pueden ocupar múltiples líneas

#### Paso 2: Ejemplo de Formato Correcto

```
Question 1
Your organization stores sensitive PII in BigQuery. How should you protect it?
A) Encrypt at application layer only
B) Use BigQuery Policy Tags for column-level security
C) Export all data regularly
D) Store in Cloud Storage instead
Correct Answer: B
Explanation:
• A is incorrect because application-level encryption doesn't provide fine-grained access control within BigQuery.
• B is correct because Policy Tags provide column-level masking, restricting access by role.
• C is incorrect because regular exports increase exposure risk.
• D is incorrect because Cloud Storage lacks query capabilities for analysis.

Question 2
...
```

#### Paso 3: Ejecutar Pipeline de Extracción

```bash
python scripts/docx_to_csv.py
```

**Salida:**
```
CSV generado en: data\processed\questions.csv
Total preguntas: 115
```

#### Paso 4: Importar a BD

```bash
python scripts/create_db.py
python scripts/import_csv_to_sqlite.py
```

#### Paso 5: Ejecutar Verificación

```bash
python scripts/verify_db.py
```

---

## 🔄 Pipeline de Datos

### Flujo Completo (DOCX → CSV → SQLite → Web)

```
1. DOCX FILES (data/raw/*.docx)
   └─ Archivos Word con preguntas
   
2. docx_to_csv.py
   ├─ Lee párrafos del DOCX
   ├─ Parsea: Question #, Texto, Opciones, Respuesta, Explicaciones
   ├─ Valida formato
   └─ Genera: questions.csv
   
3. CSV (data/processed/questions.csv)
   └─ Formato tabulado intermedio
   
4. create_db.py
   └─ Crea tabla 'questions' en SQLite
   
5. import_csv_to_sqlite.py
   ├─ Lee CSV
   ├─ Mapea campos
   └─ Inserta en exam.db
   
6. exam.db (SQLite Database)
   └─ 110 preguntas listas para consulta
   
7. app.py (Flask Web App)
   ├─ Query: SELECT * FROM questions
   ├─ Filtra por topic
   ├─ Renderiza template
   └─ Sirve HTML/CSS/JS
   
8. Browser (http://localhost:5000)
   └─ Interfaz interactiva
```

### Secuencia de Comandos para Actualizar

```bash
# Paso 1: Edita los DOCX en data/raw/
# ...

# Paso 2: Parsea DOCX → CSV
python scripts/docx_to_csv.py

# Paso 3: Valida CSV
python scripts/analyze_csv_issues.py

# Paso 4: Recrea BD
python scripts/create_db.py
python scripts/import_csv_to_sqlite.py

# Paso 5: Verifica
python scripts/verify_db.py

# Paso 6: Reinicia Flask (CTRL+C y luego)
python app.py
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.8+** - Lenguaje principal
- **Flask 3.1+** - Framework web
- **SQLite3** - Base de datos embebida
- **python-docx** - Parseo de archivos DOCX

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos modernos (gradientes, flexbox, animaciones)
- **Jinja2** - Motor de templates (integrado en Flask)

### Estructura del Código

#### `app.py` (150+ líneas)
```python
# Funciones principales:
- get_db_connection()          # Conecta a SQLite
- get_all_topics()             # Obtiene temas únicos
- get_random_question()        # Pregunta aleatoria (con filtro)
- get_question_by_id()         # Pregunta por ID
- initialize_session()         # Inicializa contador
- @app.route("/")              # Página principal
- @app.route("/answer")        # Procesa respuesta
- @app.route("/next")          # Siguiente pregunta
- @app.route("/reset")         # Reinicia contador
```

#### `templates/question.html` (300+ líneas)
```html
<!-- Secciones:
1. Head: Meta, estilos CSS embebidos
2. Header: Título + Contador
3. Filtros: Botones por tema + Reset
4. Card: Pregunta + Opciones
5. Resultado: Verde/Rojo + Explicaciones
6. Botones: Siguiente pregunta
-->
```

#### `scripts/docx_to_csv.py` (180+ líneas)
```python
# Funciones principales:
- read_docx_lines()            # Lee párrafos del DOCX
- _parse_option_line()         # Detecta opciones (A, B, C, D)
- parse_questions()            # Parsea estructura completa
- main()                       # Escribe CSV
```

---

## 🐛 Solución de Problemas

### Problema: "ModuleNotFoundError: No module named 'flask'"

**Solución:**
```bash
pip install flask
```

### Problema: "Database is locked"

**Solución:** Cierra todas las instancias de Flask y vuelve a intentar
```bash
# CTRL+C en todas las terminals Flask
python app.py
```

### Problema: Preguntas con "question_text" vacío

**Verificar:** Ejecuta analyze_csv_issues.py
```bash
python scripts/analyze_csv_issues.py
```

**Si hay problemas:** Revisa el formato del DOCX
- Las preguntas deben empezar con "Question N"
- No deben empezar con "A marketing..." directamente donde se espera pregunta

### Problema: La BD no tiene todas las preguntas

**Solución:**
```bash
# Elimina exam.db y recrea
del exam.db

# Regenera pipeline
python scripts/docx_to_csv.py
python scripts/create_db.py
python scripts/import_csv_to_sqlite.py
python scripts/verify_db.py
```

---

## 📊 Estadísticas del Proyecto

| Métrica | Valor |
|---------|-------|
| Total de Preguntas | 110 |
| Temas | 4 |
| Explicaciones por Pregunta | 4 (una por opción) |
| Líneas de Código (app.py) | ~150 |
| Líneas de CSS | ~300 |
| Líneas de Template | ~400 |
| BD Size | ~500 KB |

---

## 🎓 Cómo Estudiar Eficientemente

### 1. Practica por Tema
```
http://localhost:5000/?topic=Data_analysis
```
Enfócate en un área a la vez

### 2. Rep Review (Repetición Espaciada)
- Estudia un tema
- Reinicia con 🔄 Reset
- Estudia otro tema
- Vuelve al primero al día siguiente

### 3. Análisis de Debilidades
- Nota en qué temas tienes más errores
- Enfócate en esos temas específicos

### 4. Completa Sesiones
- Intenta llegar a 10/10 o 20/20 en un tema
- Aumenta dificultad: todos los temas juntos

---

## 📞 Contacto y Soporte

Para problemas o mejoras:
1. Revisa los scripts en `scripts/`
2. Verifica la BD con `verify_db.py`
3. Revisa el template en `templates/question.html`

---

## 📄 Licencia

Este proyecto es de código abierto para propósitos educativos.

---

## ✅ Checklist de Ejecución Rápida

```bash
# 1. Navega al proyecto
cd c:\Users\ppedrajas\Documents\StudyGCP

# 2. Activa entorno (si existe)
.venv\Scripts\activate

# 3. Instala dependencias
pip install flask python-docx

# 4. Verifica BD
python scripts/verify_db.py

# 5. Inicia app
python app.py

# 6. Abre navegador
http://localhost:5000

# 7. ¡A estudiar!
```

---

**¡Éxito en tu preparación para GCP! 🚀📚**
