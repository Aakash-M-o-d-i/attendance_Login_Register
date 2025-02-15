from flask import render_template, request, redirect, url_for, flash, session
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection 

app = Flask(__name__)

@app.route('/')
def index(name=None):
    return render_template('index.html', person=name)

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username or Email already taken!", "error")
            return render_template("register.html")

        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                       (username, email, hashed_password))
        db.commit()
        db.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  # Use .get() to safely access the form data
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required!", "error")
            return render_template('login.html')

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        db.close()

        if user and check_password_hash(user[3], password):  # user[3] refers to the hashed password in DB
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))

        flash("Invalid credentials! Please try again.", "error")

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)