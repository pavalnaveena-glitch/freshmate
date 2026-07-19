import os
from dotenv import load_dotenv
from google import genai
from flask import Flask, render_template, request, redirect, session
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQL_PORT")),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        ssl={"ssl": {}}
    )
load_dotenv()

app = Flask(__name__)
app.secret_key = "freshmate_secret_key"



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
        cursor = conn.cursor()

        # Check existing email
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        if user:
            cursor.close()
            conn.close()
            return "Email already registered! Please login."


        # Insert new user
        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, password)
        )

        conn.commit()

        cursor.close()
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
        cursor = conn.cursor()


        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()


        cursor.close()
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
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events")

    event_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("events.html", events=event_data)
# -------------------------
# Clubs
# -------------------------
@app.route('/clubs')
def clubs():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clubs")

    club_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("clubs.html", clubs=club_data)


@app.route('/faculty')
def faculty():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM faculty")

    faculty_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("faculty.html", faculty=faculty_data)

@app.route('/timetable')
def timetable():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM timetable")

    timetable_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("timetable.html", timetable=timetable_data)

@app.route('/notices')
def notices():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM notices ORDER BY notice_date DESC"
    )

    notice_data = cursor.fetchall()

    cursor.close()
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

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users LIMIT 1"
    )

    student = cursor.fetchone()

    cursor.close()
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
