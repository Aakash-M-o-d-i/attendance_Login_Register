from flask import render_template
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index(name=None):
    return render_template('index.html', person=name)

#Login
@app.route('/login')
def login(name=None):
    return render_template('login.html', person=name)
#Register
@app.route('/register')
def register():
    return render_template('register.html')