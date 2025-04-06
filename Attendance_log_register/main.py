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
app.config["MYSQL_PASSWORD"] = "1111"
app.config["MYSQL_DB"] = "attendancedb"
app.config["SECRET_KEY"] = "1254AHG"

# MySQL connection
mysql = MySQL(app)

# Define Upload Folder
UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not email or not password:
            flash("All fields are required!", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username or Email already exists!", "error")
            return render_template("register.html")

        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash("Registration successful!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))

        flash("Invalid credentials!", "error")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))


# Submit attendance
@app.route('/submit', methods=['POST'])
def submit():
    required_fields = ['name', 'enrollment_number', 'department', 'semester', 'email', 'datetime', 'image_data']
    if not all(field in request.form for field in required_fields):
        flash("All fields are required!", "danger")
        return redirect(url_for('index'))

    roll_no = request.form['enrollment_number']
    if not roll_no.isdigit() or len(roll_no) != 8:
        flash("Enrollment number must be exactly 8 digits.", "danger")
        return redirect(url_for('index'))

    name = request.form['name']
    department = request.form['department']
    semester = request.form['semester']
    email = request.form['email']
    datetime_entry = request.form['datetime']
    image_data = request.form['image_data']

    try:
        formatted_datetime = datetime.strptime(datetime_entry, "%m/%d/%Y, %I:%M:%S %p").strftime("%Y-%m-%d %H:%M:%S")
        img_blob = base64.b64decode(image_data.split(',')[1])

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO attendance (name, roll_no, department, semester, email, timestamp, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, roll_no, department, semester, email, formatted_datetime, img_blob))
        mysql.connection.commit()
        cursor.close()

        flash("Attendance submitted successfully!", "success")
    except Exception as e:
        flash(f"Error occurred while submitting: {str(e)}", "danger")

    return redirect(url_for('index'))



# Dashboard with filters, pagination
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    semester = request.form.get('semester') if request.method == 'POST' else request.args.get('semester')
    date_filter = request.form.get('date') if request.method == 'POST' else request.args.get('date')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    cursor = mysql.connection.cursor()

    # Build dynamic query
    base_query = "FROM attendance WHERE 1=1"
    params = []

    if semester:
        base_query += " AND semester = %s"
        params.append(semester)

    if date_filter:
        base_query += " AND DATE(timestamp) = %s"
        params.append(date_filter)

    # Get filtered data with pagination
    query = f"SELECT roll_no, name, department, semester, image, timestamp {base_query} ORDER BY timestamp DESC LIMIT %s OFFSET %s"
    params_with_limit = params + [per_page, offset]
    cursor.execute(query, tuple(params_with_limit))
    records = cursor.fetchall()

    # Get total count for pagination
    cursor.execute(f"SELECT COUNT(*) {base_query}", tuple(params))
    total_records = cursor.fetchone()[0]
    total_pages = (total_records + per_page - 1) // per_page

    # Format records
    updated_records = []
    for rec in records:
        image_base64 = base64.b64encode(rec[4]).decode('utf-8') if rec[4] else None
        updated_records.append({
            'roll_no': rec[0],
            'name': rec[1],
            'department': rec[2],
            'semester': rec[3],
            'image': image_base64,
            'timestamp': rec[5]
        })

    cursor.close()

    # Pass everything to the template
    return render_template('dashboard.html',
                           records=updated_records,
                           pagination={
                               'page': page,
                               'pages': total_pages
                           },
                           semester=semester,
                           date=date_filter)



# Delete a record
@app.route('/delete/<roll_no>/<timestamp>', methods=['POST'])
def delete_attendance(roll_no, timestamp):
    if 'user_id' not in session:
        flash("Unauthorized action!", "error")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM attendance WHERE roll_no = %s AND timestamp = %s", (roll_no, timestamp))
    mysql.connection.commit()
    cursor.close()

    flash("Attendance record deleted.", "success")
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
