from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1111"
app.config["MYSQL_DB"] = "attendencedb"
# not need yet, but don't delete
# app.config["SECRET_KEY"] = "1254AHG"  # Required for flash messages & session

# MySQL connection
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            flash("All fields are required!", "error")
            return render_template("register.html")

        # this is the mode of hash generate for password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256') 

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username or Email already taken!", "error")
            return render_template("register.html")

        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                       (username, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')



# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required!", "error")
            return render_template('login.html')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            user_id, username, hashed_password = user

            if hashed_password is None:  # Check if password is NULL
                flash("Invalid login credentials!", "error")
                return render_template('login.html')

            if check_password_hash(hashed_password, password):
                session['user_id'] = user_id
                session['username'] = username
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password! Please try again.", "error")
        else:
            flash("Email not found! Please register first.", "error")

    return render_template('login.html')



# Dashboard Route (Dummy)
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return f"Welcome, {session['username']}! This is your dashboard."
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
