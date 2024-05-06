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


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


@app.route('/')
def render_home():
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category_name, definition, level FROM maori_words m INNER JOIN category c ON " \
            "m.cat_id_fk = c.cat_id"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    con.close()
    print(word_list)
    message = request.args.get('message')
    if message is None:
        message = ""

    return render_template('home.html', logged_in=is_logged_in(), message=message, words=word_list)


@app.route('/dictionary')
def render_dictionary():
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category_name, definition, level FROM maori_words m INNER JOIN category c ON " \
            "m.cat_id_fk = c.cat_id"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    query = "SELECT cat_id, category_name FROM category"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    print(f'word_list = {word_list}')
    return render_template('dictionary.html', words=word_list, categories=category_list, logged_in=is_logged_in())


@app.route('/categories/<cat_id>')
def render_categories(cat_id):  # put application's code here
    title = cat_id
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category_name, definition, level FROM maori_words m " \
            "INNER JOIN category c ON m.cat_id_fk = c.cat_id WHERE cat_id_fk=? "
    cur = con.cursor()
    cur.execute(query, (title, ))
    words_list = cur.fetchall()
    query = "SELECT cat_id, category_name FROM category"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    print(words_list)
    return render_template("categories.html", wor=words_list, categories=category_list, title=title, logged_in=is_logged_in())


@app.route('/login', methods=['POST', 'GET'])
def render_login():
    if is_logged_in():
        return redirect('/')
    print("Logging in")
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        print(email)
        query = """SELECT user_id, fname, password FROM user WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()
        print(user_data)
        # if given email is not in the database this will raise an error
        # would be better to find out how to see if the query return an empty result set
        if user_data is None:
            return redirect("/login?error=Email+invalid+password+incorrect")
        try:

            user_id = user_data[0][0]
            first_name = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+invalid+password+incorrect")



        # check if the password is incorrect for that email address

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        session['email'] = email
        session['user_id'] = user_id
        session['firstname'] = first_name

        print(session)
        return redirect('/')
    return render_template('login.html', logged_in=is_logged_in())


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    if is_logged_in():
        return redirect('/menu/1')
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect("\signup?error=Passwords+do+not+match")

        if len(password) < 8:
            return redirect("\signup?error=Password+must+be+at+least+8+characters")

        hashed_password = bcrypt.generate_password_hash(password)
        con = create_connection(DATABASE)
        query = "INSERT INTO user (fname, lname, email, password) VALUES (?, ?, ?, ?)"
        cur = con.cursor()

        try:
            cur.execute(query, (fname, lname, email, hashed_password))
        except sqlite3.IntegrityError:
            con.close()
            return redirect('\signup?error=Email+is+already+used')

        con.commit()
        con.close()

        return redirect("\login")

    return render_template('signup.html', logged_in=is_logged_in())


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


@app.route('/search', methods=['GET', 'POST'])
def render_search():
    search = request.form['search']
    title = "Search for " + search
    query = "SELECT maori, english, category, definition, level " \
            "FROM maori_words WHERE maori like ? OR english like ? OR category like ? OR definition like ?" \
            "OR level like ?"
    search = "%" + search + "%"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (search, search, search, search, search))
    words_list = cur.fetchall()
    con.close()
    return render_template("home.html", words=words_list, title=title)


@app.route('/admin')
def render_admin():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    con = create_connection(DATABASE)
    query = "SELECT * FROM maori_words"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    con.close()
    return render_template("admin.html", logged_in=is_logged_in(), words=word_list)


@app.route('/add_words', methods=['POST'])
def add_words():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":
        print(request.form)
        maori = request.form.get('maori').title().strip()
        english = request.form.get('english').title().strip()
        category = request.form.get('category').title().strip()
        definition = request.form.get('definition').title().strip()
        level = request.form.get('level').strip()
        print(maori, english, category, definition, level)
        con = create_connection(DATABASE)
        query = "INSERT INTO maori_words (maori, english, category, definition, level) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query, (maori, english, category, definition, level))
        con.commit()
        con.close()
        return redirect('/admin')


@app.route('/delete_words', methods=['POST'])
def render_delete_words():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":
        category = request.form.get('')
        print(category)
        category = category.split(", ")
        cat_id = category[0]
        cat_name = category[1]
        return render_template("delete_confirm.html", id=cat_id, name=cat_name, type="category")
    return redirect("/admin")
