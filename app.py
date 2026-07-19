import os
from google import genai
from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "freshmate_secret_key"

# -------------------------
# MySQL Configuration
# -------------------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Freshmate@123'
app.config['MYSQL_DB'] = 'freshmate_ai'

mysql = MySQL(app)

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

        cur = mysql.connection.cursor()

        # Check whether email already exists
        cur.execute("SELECT * FROM students WHERE email=%s", (email,))
        user = cur.fetchone()

        if user:
            cur.close()
            return "Email already registered! Please login."

        # Insert new student
        cur.execute(
            "INSERT INTO students(name, email, password) VALUES(%s, %s, %s)",
            (name, email, password)
        )

        mysql.connection.commit()
        cur.close()

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

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM students WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cur.fetchone()

        cur.close()

        if user:
            session['user'] = user[1]   # Store student name
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

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM events")

    event_data = cur.fetchall()

    cur.close()

    return render_template("events.html", events=event_data)
# -------------------------
# Clubs
# -------------------------
@app.route('/clubs')
def clubs():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM clubs")

    club_data = cur.fetchall()

    cur.close()

    return render_template("clubs.html", clubs=club_data)


@app.route('/faculty')
def faculty():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM faculty")

    faculty_data = cur.fetchall()

    cur.close()

    return render_template("faculty.html", faculty=faculty_data)

@app.route('/timetable')
def timetable():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM timetable")

    timetable_data = cur.fetchall()

    cur.close()

    return render_template("timetable.html", timetable=timetable_data)

@app.route('/notices')
def notices():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM notices ORDER BY notice_date DESC")

    notice_data = cur.fetchall()

    cur.close()

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

        except Exception as e:
            answer = "⚠️ AI service is temporarily unavailable. Please check your Gemini API key or quota."

    return render_template("chatbot.html", answer=answer)

@app.route('/profile')
def profile():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM students LIMIT 1")

    student = cur.fetchone()

    cur.close()

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
