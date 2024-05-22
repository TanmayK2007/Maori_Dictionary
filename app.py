from flask import Flask, render_template, redirect, request, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime
# importing everything needed from external libraries

# database file path
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
        # checks if the "email" key is not in session, as everyone who has logged in will have an email
        print("not logged in")  # prints "not logged in" if not logged in
        return False
    else:
        print("logged in")  # prints "logged in" if logged in
        return True


def is_teacher():
    if session.get("type") is None:
        # checks if "type" is in session, this is what I use in user table to check for users who are teachers
        print("Not Teacher")  # prints "Not Teacher"
        return False
    else:
        print("Is Teacher")  # prints "Is Teacher"
        return True


@app.route('/')
def render_home():  # render the home page with the list of maori words and some of its details
    con = create_connection(DATABASE)  # create a connection to the database
    query = "SELECT maori, english, category_name, definition, level, date_added, word_id FROM maori_words m" \
            " INNER JOIN category c ON m.cat_id_fk = c.cat_id"
    # query for specific columns to be selected from maori_words table also using inner join to use the foreign key
    # in maori_words to use data from category table
    cur = con.cursor()
    cur.execute(query)  # executes the query
    word_list = cur.fetchall()  # fetches all the results from the executed query
    con.close()  # closes the database connection
    print(word_list)  # prints the list of words
    return render_template('home.html', logged_in=is_logged_in(), words=word_list, teacher=is_teacher())
    # return the rendered template home.html


@app.route('/open_word_details/<word_id>')
def render_open_word_details(word_id):  # render the details page for a specific maori word
    con = create_connection(DATABASE)  # create a connection to the database
    query = "SELECT maori, english, category_name, definition, level, date_added, fname, lname, cat_id, images," \
            " word_id FROM maori_words m INNER JOIN category c ON m.cat_id_fk = c.cat_id INNER JOIN user u " \
            "ON m.user_id_fk = u.user_id WHERE word_id = ?"
    # query for specific columns to be selected from maori_words table, also using inner join to use the foreign keys
    # in maori_words to use data from user table and category table
    cur = con.cursor()  # creates a cursor
    cur.execute(query, (word_id,))  # executes the query, along with word_id
    words_list = cur.fetchall()  # fetches all the results from the executed query into words_list
    con.close()  # closes the database connection
    print(words_list)  # prints the list of words
    return render_template('open_word_details.html', logged_in=is_logged_in(), teacher=is_teacher(), words=words_list)
    # return the rendered template open_word_details.html


@app.route('/dictionary')
def render_dictionary():  # render the dictionary page with all maori words and categories
    con = create_connection(DATABASE)  # create a connection to the database
    query = "SELECT maori, english, word_id FROM maori_words"
    # query for specific columns to be selected from maori_words table
    cur = con.cursor()  # creates a cursor
    cur.execute(query)  # executes the query
    word_list = cur.fetchall()  # fetches all the results from the executed query into word_list
    query = "SELECT cat_id, category_name FROM category"
    # query for specific columns to be selected from category table, I've used another query for this instead of using
    # inner join because I was getting an error and Mr. Stevenson said this is how it is supposed to be done, it is fine
    cur = con.cursor()  # creates a cursor
    cur.execute(query)  # executes the query
    category_list = cur.fetchall()  # fetches all the results from the executed query
    con.close()  # closes the database connection
    return render_template('dictionary.html', words=word_list, categories=category_list,
                           logged_in=is_logged_in(), teacher=is_teacher())
    # return the rendered template dictionary.html


@app.route('/categories/<cat_id>')
def render_categories(cat_id):  # renders the categories page for a specific category ID
    title = cat_id  # making title = cat_id to simplify things
    con = create_connection(DATABASE)  # create a connection to the database
    query = "SELECT maori, english, word_id FROM maori_words m " \
            "INNER JOIN category c ON m.cat_id_fk = c.cat_id WHERE cat_id_fk=? "
    # query for specific columns to be selected from maori_words table, inner joining category table as well
    cur = con.cursor()  # creates a cursor
    cur.execute(query, (title,))  # executes the query
    words_list = cur.fetchall()  # fetches all the results from the executed query into word_list
    query = "SELECT cat_id, category_name FROM category"
    # query for specific columns to be selected from category table
    cur = con.cursor()  # creates a cursor
    cur.execute(query)  # executes the query
    category_list = cur.fetchall()  # fetches all the results from the executed query into category_list
    con.close()  # closes the database connection
    print(words_list)  # prints the list of words
    return render_template("categories.html", words=words_list, categories=category_list,
                           title=title, logged_in=is_logged_in(), teacher=is_teacher())
    # return the rendered template categories.html


@app.route('/login', methods=['POST', 'GET'])
def render_login():  # render the login page and handle login submissions
    if is_logged_in():  # checks if the user is already logged in
        return redirect('/')  # if the user is already logged in, redirects to the home page
    print("Logging in")  # prints "logging in"
    if request.method == "POST":  # checks if the request method is post
        email = request.form['email'].strip().lower()
        # get email from form and strips extra whitespaces and turns it into lowercase
        password = request.form['password'].strip()  # gets password from form and strips extra whitespaces
        print(email)  # print the email
        query = "SELECT user_id, fname, password, type FROM user WHERE email = ?"
        # query for specific columns to be selected from user table
        con = create_connection(DATABASE)  # create a connection to the database
        cur = con.cursor()  # creates a cursor
        cur.execute(query, (email,))  # executes the query
        user_data = cur.fetchall()  # fetches all the results from the executed query into category_list
        con.close()  # close the database connection
        print(user_data)  # prints the data of users
        # if given email is not in the database this will raise an error
        # would be better to find out how to see if the query return an empty result set
        if user_data is None:  # checks if user_data is empty
            return redirect("/login?error=Email+invalid+password+incorrect")
            # if it is empty or password/email is incorrect, redirects to login page with an error message
        try:
            user_id = user_data[0][0]  # get user_id from user_data
            first_name = user_data[0][1]  # get first_name from user_data
            db_password = user_data[0][2]  # get db_password from user_data
            user_type = user_data[0][3]  # get user_type from user_data
        except IndexError:
            return redirect("/login?error=Email+invalid+password+incorrect")
        # check if the password is incorrect for that email address
        if not bcrypt.check_password_hash(db_password, password):
            # check if the provided password matches the stored hashed password
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")
            # redirect with an error message if provided password does not match the stored hashed password
        # stores user details in the session
        session['email'] = email
        session['user_id'] = user_id
        session['firstname'] = first_name
        session['type'] = user_type

        print(session)  # print session details
        return redirect('/')  # redirect to home page if login is successful
    return render_template('login.html', logged_in=is_logged_in(), teacher=is_teacher())
    # return the rendered template login.html


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():  # render the signup page and handle new users signing up
    if is_logged_in():  # checks if the user is already logged in
        return redirect('/')  # if the user is already logged in, redirects to the home page
    if request.method == 'POST':  # checks if the request method is post
        print(request.form)  # prints for data
        fname = request.form.get('fname').title().strip()
        # get first name, strip any extra whitespaces and then capitalize the first letter
        lname = request.form.get('lname').title().strip()
        # get last name, strip any extra whitespaces and then capitalize the first letter
        email = request.form.get('email').lower().strip()
        # get email, strip any extra whitespaces and then convert it to lowercase
        password = request.form.get('password')  # get password
        password2 = request.form.get('password2')  # get password2 for confirmation that both match
        teacher = request.form.get('teacher')  # get teacher status

        if password != password2:  # check if both passwords match
            return redirect("/signup?error=Passwords+do+not+match")
            # if both passwords don't match send an error message telling the user that the passwords don't match

        if len(password) <= 8:  # check if the length of the password is at least 8 characters long
            return redirect("/signup?error=Password+must+be+at+least+8+characters")
        # if the length of the password is less than 8 then it will send the user an error message to change it

        hashed_password = bcrypt.generate_password_hash(password)  # hash the password provided for added security
        con = create_connection(DATABASE)  # creates a connection to the database
        query = "INSERT INTO user (fname, lname, email, password, type) VALUES (?, ?, ?, ?, ?)"
        # query to insert the data provided to the form into user table into the specified columns
        cur = con.cursor()  # creates a cursor object

        try:
            cur.execute(query, (fname, lname, email, hashed_password, teacher))  # execute the query with form data
        except sqlite3.IntegrityError:  # handle case where email is already used
            con.close()  # close the database connection
            return redirect('/signup?error=Email+is+already+used')
        # if email is already in use redirects with an error message

        con.commit()  # commit everything that occurred in the cursor
        con.close()  # close the database connection

        return redirect("/login")  # redirects to the login page if signup is successful

    return render_template('signup.html', logged_in=is_logged_in(), teacher=is_teacher())
    # return the rendered template signup.html


@app.route('/logout')
def logout():  # log out the user by clearing the session
    print(list(session.keys()))  # print the session keys
    [session.pop(key) for key in list(session.keys())]  # remove the session keys
    print(list(session.keys()))  # print session keys after removing them
    return redirect('/?message=See+you+next+time!')  # redirect to home page with a wholesome message


@app.route('/search', methods=['GET', 'POST'])
def render_search():  # render the search results based on user query
    search = request.form['search']  # get search from form
    title = "Search for " + search  # set the title for the search results page
    query = "SELECT maori, english, category_name, definition, level, date_added, word_id, cat_id_fk " \
            "FROM maori_words m INNER JOIN category c ON m.cat_id_fk = c.cat_id " \
            "WHERE maori like ? OR english like ? OR category_name like ? OR definition like ? OR level like ? "
    # query for specific columns to be selected from maori_words table, also using inner join to use the foreign keys
    # to join the category table too
    search = "%" + search + "%"
    con = create_connection(DATABASE)  # create a connection to the database
    cur = con.cursor()  # create a cursor object
    cur.execute(query, (search, search, search, search, search))  # execute the query with search terms
    words_list = cur.fetchall()  # fetches all the results from the executed query into words_list
    con.close()  # close the database connection
    return render_template("home.html", words=words_list, title=title, teacher=is_teacher(), logged_in=is_logged_in())
    # return the rendered template home.html


@app.route('/admin')
def render_admin():  # render the admin page if the user is a teacher, with teacher-only features
    if not is_logged_in():  # checks if the user is not logged in
        return redirect('/?message=Need+to+be+logged+in.')
    # redirects to home page with a message telling the user to be logged in first to access admin
    if not is_teacher():  # checks if the user is a teacher
        return redirect('/?message=Need+to+be+teacher.')
    # redirects to home page with a message telling the user to be a teacher first to access admin
    con = create_connection(DATABASE)  # creates a connection to the database
    query = "SELECT * FROM maori_words"  # query for all the columns to be selected from the table maori_words
    cur = con.cursor()  # create a cursor object
    cur.execute(query)  # execute the query
    word_list = cur.fetchall()  # fetches all the results from the executed query into word_list
    con.close()  # close the connection to the database
    con = create_connection(DATABASE)  # create a connection to the database
    query = "SELECT * FROM category"  # query for all the columns to be selected category table
    cur = con.cursor()  # create a cursor object
    cur.execute(query)  # execute the query
    category_list = cur.fetchall()  # fetches all the results from the executed query into category_list
    con.close()  # close the connection to the database
    print(category_list)  # print the category list
    return render_template("admin.html", logged_in=is_logged_in(), categories=category_list, words=word_list,
                           teacher=is_teacher())
    # returns the rendered template admin.html


@app.route('/add_words', methods=['POST'])
def add_words():  # function to add new words into the dictionary
    if not is_logged_in():  # checks if the user is not logged in
        return redirect('/?message=Need+to+be+logged+in.')
    # redirects to home page with a message telling the user to be logged in first to access admin
    if not is_teacher():  # checks if the user is a teacher
        return redirect('/?message=Need+to+be+teacher.')
    # redirects to home page with a message telling the user to be a teacher first to access admin
    if request.method == "POST":  # checks if the request method is post
        print(request.form)  # prints the form
        maori = request.form.get('maori').capitalize().strip()
        # get maori, strip any extra whitespaces and capitalize the first letter
        english = request.form.get('english').capitalize().strip()
        # get english, strip any extra whitespaces and capitalize the first letter
        category = request.form.get('category').capitalize().strip()
        # get category, strip any extra whitespaces and capitalize the first letter
        definition = request.form.get('definition').capitalize().strip()
        # get definition, strip any extra whitespaces and capitalize the first letter
        level = request.form.get('level')  # get level
        date_added = datetime.today().strftime('%d-%m-%Y')  # get current date in specific DD/MM/YYYY format
        word_added_by = session.get('user_id')  # get user_id from session
        images = 'noimage'  # set default image value
        print(maori, english, category, definition, level, date_added)  # print word details
        con = create_connection(DATABASE)  # create a connection to the database
        query = "INSERT INTO maori_words (maori, english, cat_id_fk, definition, level," \
                " date_added, user_id_fk, images) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        # query to insert the details into specific columns in maori_words table
        cur = con.cursor()  # create a cursor object
        cur.execute(query, (maori, english, category, definition, level, date_added, word_added_by, images))
        # execute the query with all the word details
        con.commit()  # commit everything that occurred in the cursor
        con.close()  # close the database connection
    return redirect('/admin')  # redirect to admin page


@app.route('/add_category', methods=['POST'])
def add_category():  # function to add new categories into the dictionary
    if not is_logged_in():  # checks if the user is not logged in
        return redirect('/?message=Need+to+be+logged+in.')
    # redirects to home page with a message telling the user to be logged in first to access admin
    if not is_teacher():  # checks if the user is a teacher
        return redirect('/?message=Need+to+be+teacher.')
    # redirects to home page with a message telling the user to be a teacher first to access admin
    if request.method == "POST":  # checks if the request method is post
        print(request.form)  # prints the form
        cat_name = request.form.get('category_name').capitalize().strip()
        # get cat_name, strip any extra whitespaces and capitalize the first letter
        print(cat_name)  # print cat_name
        con = create_connection(DATABASE)  # create a connection to the database
        query = "INSERT INTO category ('category_name') VALUES (?)"
        # query to add the new category into the column category_name of the category table
        cur = con.cursor()  # create a cursor
        cur.execute(query, (cat_name,))  # execute the query with cat_name
        con.commit()  # commit everything that occurred in the cursor
        con.close()  # close the database connection
        return redirect('/admin')  # redirect to admin page


@app.route('/delete_word', methods=['POST'])
def render_delete_words():  # render the delete words page for deleting words
    if not is_logged_in():  # checks if the user is not logged in
        return redirect('/?message=Need+to+be+logged+in.')
    # redirects to home page with a message telling the user to be logged in first to access admin
    if not is_teacher():  # checks if the user is a teacher
        return redirect('/?message=Need+to+be+teacher.')
    # redirects to home page with a message telling the user to be a teacher first to access admin
    if request.method == "POST":  # checks if the request method is post
        words = request.form.get('word_id')  # get word_id from form
        words = words.split(", ")  # split word_id and name
        words_id = words[0]  # get word_id
        words_name = words[1]  # get word name
        return render_template("delete_confirm.html", id=words_id, name=words_name, type="word",
                               logged_in=is_logged_in(), teacher=is_teacher())
        # return the rendered template delete_confirm.html
    return redirect("/admin")  # redirect to admin page


@app.route('/delete_word_confirm/<word_id>')
def delete_word_confirm(word_id):  # confirm to, and delete the specified word
    print("Deleting word with ID:", word_id)  # print word_id for the word being deleted
    if not is_logged_in():  # checks if the user is not logged in
        return redirect('/?message=Need+to+be+logged+in.')
    # redirects to home page with a message telling the user to be logged in first to access admin
    if not is_teacher():  # checks if the user is a teacher
        return redirect('/?message=Need+to+be+teacher.')
    # redirects to home page with a message telling the user to be a teacher first to access admin
    con = create_connection(DATABASE)  # create a connection to the database
    query = 'DELETE FROM maori_words WHERE word_id = ?'  # query to delete the specified word from maori_words table
    cur = con.cursor()  # create a cursor
    cur.execute(query, (word_id,))  # execute the query and the word_id
    con.commit()  # commit everything that occurred in the cursor
    con.close()  # close the connection to the database
    return redirect('/admin')  # redirect to admin page


@app.route('/delete_category', methods=['POST'])
def render_delete_category():  # render the delete confirmation page for categories
    if not is_logged_in():  # checks if the user is not logged in
        return redirect('/?message=Need+to+be+logged+in.')
    # redirects to home page with a message telling the user to be logged in first to access admin
    if not is_teacher():  # checks if the user is a teacher
        return redirect('/?message=Need+to+be+teacher.')
    # redirects to home page with a message telling the user to be a teacher first to access admin
    if request.method == "POST":  # checks if the request method is post
        category = request.form.get('cat_id')  # get cat_id from form
        print(category)  # print word_id
        category = category.split(", ")  # split cat_id and category_name
        cat_id = category[0]  # get cat_id
        category_name = category[1]  # get category_name
        return render_template("delete_category_confirm.html", id=cat_id, name=category_name, type="category")
        # return the rendered template delete_category_confirm.html
    return redirect("/admin")  # redirect to admin page


@app.route('/delete_category_confirm/<cat_id>')
def delete_category_confirm(cat_id):  # confirm and delete the specified category
    if not is_logged_in():  # checks if the user is not logged in
        return redirect('/?message=Need+to+be+logged+in.')
    # redirects to home page with a message telling the user to be logged in first to access admin
    if not is_teacher():  # checks if the user is a teacher
        return redirect('/?message=Need+to+be+teacher.')
    # redirects to home page with a message telling the user to be a teacher first to access admin
    con = create_connection(DATABASE)  # create a connection to the database
    query = "DELETE FROM category WHERE cat_id = ?"  # query to delete the specified category from category table
    cur = con.cursor()  # create a cursor
    cur.execute(query, (cat_id,))  # execute the query and the word_id
    con.commit()  # commit everything that occurred in the cursor
    con.close()  # close the connection to the database
    return redirect("/admin")  # redirect to admin page
