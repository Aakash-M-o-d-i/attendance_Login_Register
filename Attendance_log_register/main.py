from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import base64
import os
from datetime import datetime

app = Flask(__name__)

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "rajeshji11"
app.config["MYSQL_DB"] = "attendancedb"
app.config["SECRET_KEY"] = "1254AHG"  # Required for flash messages & session

# MySQL connection
mysql = MySQL(app)

# Define Upload Folder
UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Ensure the folder exists


@app.route('/index', methods=['GET', 'POST'])
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

        # Hash the password
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

# submit attendance in the database
@app.route('/submit', methods=['POST'])
def submit():
    required_fields = ['name', 'enrollment_number', 'department', 'semester', 'email', 'datetime', 'image_data']

    if not all(field in request.form for field in required_fields):
        flash("All fields are required!", "error")
        return redirect(url_for('index'))

    name = request.form['name']
    roll_no = request.form['enrollment_number']  # Mapping form field to DB column
    department = request.form['department']
    semester = request.form['semester']
    email = request.form['email']
    datetime_entry = request.form['datetime']
    image_data = request.form['image_data']

    # Convert datetime to MySQL format
    formatted_datetime = datetime.strptime(datetime_entry, "%m/%d/%Y, %I:%M:%S %p").strftime("%Y-%m-%d %H:%M:%S")

    # Decode and save the image
    img_blob = base64.b64decode(image_data.split(',')[1])
    image_path = os.path.join("static/uploads", f"{roll_no}.png")
    with open(image_path, 'wb') as f:
        f.write(img_blob)

    # Insert into MySQL
    cursor = mysql.connection.cursor()
    sql = "INSERT INTO attendance (name, roll_no, department, semester, email, timestamp, image) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (name, roll_no, department, semester, email, formatted_datetime, img_blob))
    mysql.connection.commit()
    cursor.close()

    flash("Attendance submitted successfully!", "success")
    return redirect(url_for('dashboard'))



# dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    cursor = mysql.connection.cursor()
    
    # Get filter values
    semester = request.form.get('semester')
    date_filter = request.form.get('date')

    # Build query
    query = "SELECT roll_no, name, department, semester, image, timestamp FROM attendance WHERE 1=1"
    params = []

    if semester:
        query += " AND semester = %s"
        params.append(semester)

    if date_filter:
        query += " AND DATE(timestamp) = %s"
        params.append(date_filter)

    query += " ORDER BY timestamp DESC"

    cursor.execute(query, tuple(params))
    records = cursor.fetchall()

    # Convert image BLOBs to Base64
    updated_records = []
    for record in records:
        roll_no, name, department, semester, image, timestamp = record
        image_base64 = base64.b64encode(image).decode('utf-8') if image else None

        updated_records.append({
            "roll_no": roll_no,
            "name": name,
            "department": department,
            "semester": semester,
            "image": image_base64,
            "timestamp": timestamp
        })

    return render_template('dashboard.html', records=updated_records)



if __name__ == '__main__':
    app.run(debug=True)

