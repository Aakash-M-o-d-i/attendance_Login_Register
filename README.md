# CTUAP LAB Attendance System – Documentation

📌 **Overview**

The CTUAP LAB Attendance System is a Flask-based web application that allows students to submit their attendance by capturing a live webcam photo, along with their details. Admins can view, filter, and delete attendance records from the dashboard.

⚙️ **Technologies Used**

| Purpose              | Technology                 |
| -------------------- | -------------------------- |
| Backend Framework    | Flask (Python)             |
| Front End Styling    | HTML, CSS                  |
| Database             | MySQL                      |
| Camera Integration   | JavaScript (WebRTC)        |
| Authentication       | Flask Sessions             |
| Password Security    | Werkzeug Hashing           |

🧪 **Features**

✅ **Student Panel**

- Submit attendance with:
  - Full name
  - Enrollment number (8-digit validation)
  - Department & Semester
  - Email
  - Date & Time (auto-filled)
  - Captured webcam image

🔐 **Admin Panel**

- Register/Login functionality
- View all attendance records
- Filter by:
  - Semester
  - Date
- Pagination (10 records per page)
- Delete individual records
- Logout functionality

🛠️ **Setup Instructions**

1. 🐍 **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. 📦 Install Dependencies
    - Install the required Python packages using pip:
    ```bash
   pip install flask flask-mysqldb werkzeug
   ```
   Example *requirements.txt*:
            - Flask
            - Flask-MySQLdb
            - Werkzeug

3. 🛢️ MySQL Configuration

Make sure MySQL is installed and running.
Create the database and tables:

    ```bash
        CREATE DATABASE attendancedb;

        USE attendancedb;

        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100),
            email VARCHAR(100),
            password VARCHAR(200)
        );

        CREATE TABLE attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            roll_no VARCHAR(8),
            department VARCHAR(100),
            semester VARCHAR(10),
            email VARCHAR(100),
            timestamp DATETIME,
            image LONGBLOB
        );
#    <!-- ``` -->

4. ⚙️ Update Flask MySQL Configuration (app.py)
    ```bash
    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = "1111"  # Replace with your password
    app.config["MYSQL_DB"] = "attendancedb"
    app.config["SECRET_KEY"] = "1254AHG"
    ```
# ▶️ How to Run

1. Run the Flask App
    ```bash
        python app.py
    ```
2. Open in Browser
    Visit 
    ```bash 
    http://127.0.0.1:5000/ 
    ```

# 🛡️ Security Considerations

### 1. Passwords are hashed using werkzeug.security.
### 2. Session management is handled using Flask's built-in session support.
### 3.    actions like delete require confirmation prompts.

# 💡 Future Improvements

### 1. Export records to CSV/PDF
### 2. Face recognition for better 
### verification
### 3. Admin roles and privileges
### 4. Email confirmations on attendance