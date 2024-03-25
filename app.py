from flask import Flask, render_template, redirect, request, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DATABASE = "C:/Users/22452/OneDrive - Wellington College/13DTS/Maori Dictionary/maori_dictionary"

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "ueuywq9571"


def create_connection(db_file):
    """
    Create a connection with the database
    parameter: name of the database file
    returns: a connection to the file
    """
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def render_home():
    message = request.args.get('message')
    if message is None:
        message = ""

    return render_template('home.html')