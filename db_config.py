# import mysql.connector
import MySQLdb


def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",  # my MySQL username
        password="1111",  # my MySQL password
        database="attendancedb"
    )