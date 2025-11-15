import sqlite3
import datetime

DB_NAME = "gym_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            workout_name TEXT, 
            name TEXT NOT NULL,
            weight REAL NOT NULL,
            reps INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_user(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def validate_login(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_exercise(user_id, workout_name, name, weight, reps):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    if not workout_name.strip():
        workout_name = "Antrenament"

    cursor.execute("INSERT INTO exercises (user_id, workout_name, name, weight, reps, date) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, workout_name, name, weight, reps, today))
    conn.commit()
    conn.close()

def get_user_exercises(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, workout_name, name, weight, reps, date FROM exercises WHERE user_id = ? ORDER BY date DESC, id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_last_exercise(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM exercises WHERE user_id = ?", (user_id,))
    last_id_result = cursor.fetchone()
    
    if last_id_result and last_id_result[0] is not None:
        last_id = last_id_result[0]
        cursor.execute("DELETE FROM exercises WHERE id = ?", (last_id,))
        conn.commit()
    conn.close()

def delete_exercise_by_id(exercise_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exercises WHERE id = ?", (exercise_id,))
    conn.commit()
    conn.close()

def get_unique_exercise_names(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT name FROM exercises WHERE user_id = ? ORDER BY name ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# --- FUNCȚIE NOUĂ PENTRU UPDATE (EDITARE) ---
def update_exercise(exercise_id, new_name, new_weight, new_reps):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE exercises 
        SET name = ?, weight = ?, reps = ? 
        WHERE id = ?
    ''', (new_name, new_weight, new_reps, exercise_id))
    conn.commit()
    conn.close()

def get_exercise_history(user_id, exercise_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Luăm ultimele 30 de intrări (DESC = de la nou la vechi)
    cursor.execute('''
        SELECT date, weight, reps 
        FROM exercises 
        WHERE user_id = ? AND name = ? 
        ORDER BY date DESC 
        LIMIT 30
    ''', (user_id, exercise_name))
    
    rows = cursor.fetchall()
    conn.close()
    
    # 2. Le inversăm în Python ca să apară pe grafic de la stânga (vechi) la dreapta (nou)
    return rows[::-1]