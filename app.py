import os

print("Current folder:", os.getcwd())
print("Templates:", os.listdir("templates"))
from dotenv import load_dotenv
from google import genai
from flask import Flask, render_template, request, redirect, session
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    print("HOST =", os.getenv("MYSQLHOST"))
    print("PORT =", os.getenv("MYSQLPORT"))
    print("USER =", os.getenv("MYSQLUSER"))
    print("DATABASE =", os.getenv("MYSQLDATABASE"))

    conn = pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT")),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        ssl={"ssl": {}}
    )

    return conn

    cursor = conn.cursor()

    cursor.execute("SELECT DATABASE()")
    print(cursor.fetchone())

    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())

    cursor.close()

    return conn

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
            "SELECT * FROM `user` WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        if user:
            cursor.close()
            conn.close()
            return "Email already registered! Please login."


        # Insert new user
        cursor.execute(
            "INSERT INTO `user`(username,email,password) VALUES(%s,%s,%s)",
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
            "SELECT * FROM user WHERE email=%s AND password=%s",
            (email, password)
        )

        student = cursor.fetchone()

        cursor.close()
        conn.close()

        if student:
            session['email'] = student['email']
            session['name'] = student['username']

            return redirect('/dashboard')

        else:
            return "Invalid Email or Password"


    return render_template('login.html')
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

    clubs = cursor.fetchall()

   

    return render_template("clubs.html", clubs=clubs)


@app.route('/faculty')
def faculty():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM faculty")

    faculty = cursor.fetchall()
    print(faculty)
    cursor.close()
    conn.close()

    return render_template("faculty.html", faculty=faculty)

@app.route('/timetable')
def timetable():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM timetable")

    timetable = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("timetable.html", timetable=timetable)

@app.route('/notices')
def notices():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM notices ORDER BY id DESC"
    )

    notices = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("notices.html", notices=notices)

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

    if 'email' not in session:
        return redirect('/login')


    conn = get_db_connection()
    cursor = conn.cursor()


    cursor.execute(
        "SELECT * FROM user WHERE email=%s",
        (session['email'],)
    )


    student = cursor.fetchone()


    cursor.close()
    conn.close()


    return render_template(
        'profile.html',
        student=student
    )
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# -------------------------
# Run Flask
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
