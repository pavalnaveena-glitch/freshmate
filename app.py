import os
from dotenv import load_dotenv
from google import genai
from flask import Flask, render_template, request, redirect, session
import sqlite3
DATABASE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
load_dotenv()

app = Flask(__name__)
app.secret_key = "freshmate_secret_key"


def create_table():
    conn = get_db_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)
    conn.execute("""
INSERT OR IGNORE INTO users (name, email, password)
VALUES (?, ?, ?)
""", ("Admin", "admin@gmail.com", "1234"))

    conn.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        description TEXT
    )
    """)
    conn.execute("""
INSERT OR IGNORE INTO events (id, title, date, description)
VALUES (1, 'AI Workshop', '2026-08-10', 'Workshop on Artificial Intelligence')
""")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS clubs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT
    )
    """)
    conn.execute("""
INSERT OR IGNORE INTO clubs (id, name, description)
VALUES (1, 'Coding Club', 'Learn programming and participate in coding contests')
""")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS faculty(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT
    )
    """)
    conn.execute("""
INSERT OR IGNORE INTO faculty (id, name, department)
VALUES (1, 'Dr. Priya', 'Computer Science')
""")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS timetable(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        time TEXT
    )
    """)
    conn.execute("""
INSERT OR IGNORE INTO timetable (id, subject, time)
VALUES (1, 'Python Programming', '10:00 AM - 11:00 AM')
""")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS notices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        notice_date TEXT
    )
    """)
    conn.execute("""
INSERT OR IGNORE INTO notices (id, title, notice_date)
VALUES (1, 'Semester Exams Start', '2026-08-15')
""")

    conn.commit()
    conn.close()

create_table()


client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# -------------------------
# Home Page
# -------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -------------------------
# Register
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()
        

        if user:
            conn.close()
            return "Email already registered! Please login."

        # Insert new student
        conn.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name,email,password)
        )

        conn.commit()
        conn.close()
        
        return redirect('/login')

    return render_template('register.html')

# -------------------------
# Login
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email,password)
        ).fetchone()

        conn.close()

        
    

        if user:
            session['user'] = user['name']
            return redirect('/dashboard')
        else:
            return "Invalid Email or Password"
    
    return render_template("login.html")
# -------------------------
# Dashboard
# -------------------------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# -------------------------
# Events
# -------------------------
@app.route('/events')
def events():

    conn = get_db_connection()
    

    event_data = conn.execute("SELECT * FROM events").fetchall()
    conn.close()

    return render_template("events.html", events=event_data)
# -------------------------
# Clubs
# -------------------------
# -------------------------
# Clubs
# -------------------------
@app.route('/clubs')
def clubs():

    conn = get_db_connection()

    club_data = conn.execute(
        "SELECT * FROM clubs"
    ).fetchall()

    conn.close()

    return render_template("clubs.html", clubs=club_data)


@app.route('/faculty')
def faculty():

    conn=get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM faculty")

    faculty_data = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("faculty.html", faculty=faculty_data)

@app.route('/timetable')
def timetable():
    conn=get_db_connection()

    cur = conn.cursor()

    cur.execute("SELECT * FROM timetable")

    timetable_data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("timetable.html", timetable=timetable_data)

@app.route('/notices')
def notices():

    conn=get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM notices ORDER BY notice_date DESC")

    notice_data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("notices.html", notices=notice_data)

# -------------------------
# Chatbot
# -------------------------


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():

    answer = ""

    if request.method == 'POST':
        question = request.form['question']

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=question
            )

            answer = response.text

        except Exception:
            answer = """
🤖 FreshMate AI

I'm sorry, I couldn't answer your question right now.

💭 Thinking...

The AI service is currently unavailable. Please try again in a few moments.

Meanwhile, you can continue exploring FreshMate AI features such as:
• 📅 Events
• 👥 Clubs
• 👨‍🏫 Faculty
• 📝 Notices
• 📖 Timetable

Thank you for your patience! 😊
"""

    return render_template("chatbot.html", answer=answer)

@app.route('/profile')
def profile():

    conn=get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users LIMIT 1")

    student = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("profile.html", student=student)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# -------------------------
# Run Flask
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
