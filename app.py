"""API KEY AND SECRET
key: CBCgNmPmOvNmjjf2oy63g
secret: vub7fNoCfLfEaLNDDX9zL0oq5o2oJIbFucKoE4fcSpg
"""

import os, re, nltk

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from flask_jsglue import JSGlue
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, GoodreadsReview

# Configure application
app = Flask(__name__)
JSGlue(app)

# Check for environment variable
""" if not os.getenv("postgres://nmveeatzgvsvqz:71ac6602574819f555d2c89d38367361795ddf1474c92c763f1ecc67b2951d0c@ec2-23-21-156-171.compute-1.amazonaws.com:5432/d1ta26pb3lelfn"):
    raise RuntimeError("DATABASE_URL is not set") BECAUSE WINDOWS DOES NOT HAVE OS.GETENV
    Could use os.environ.get(theURIabove)
    such as
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API_KEY not set")
    return render_template("index.html", key=os.environ.get("API_KEY"))"""
	
"""If you want to use an environment variable to get your database connection string, do something like the following in your .bash_profile or .bashrc file:

export SQLALCHEMY_DATABASE_URI='postgresql://postgres:password@localhost/database1'

then change your database connection code to the following:

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('SQLALCHEMY_DATABASE_URI')"""

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# pool size and max overflow is to send more requests to sql
engine = create_engine("postgres://nmveeatzgvsvqz:71ac6602574819f555d2c89d38367361795ddf1474c92c763f1ecc67b2951d0c@ec2-23-21-156-171.compute-1.amazonaws.com:5432/d1ta26pb3lelfn", pool_size=10, max_overflow=20)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get info
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            # If not, return login page
            message = f"Username {username} or password is not correct. Please try again"
            return render_template("login.html", message=message)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        # Get info
        username = request.form.get("username")
        password = request.form.get("password")
        # confirmation = request.form.get("confirmation") No need because just for confirmation, already check validation in register.html
        passwordHash = generate_password_hash(password)
        # Validate info
            # Already validate in register.html
        # Check if username exists:
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
        if len(rows) == 0:
            # If not exist yet, add to db
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", {"username": username, "hash": passwordHash})
            db.commit()
            return redirect('/')
        else:
            # If exists, return register page
            message = f"Username {username} is not available. Please try again."
            return render_template("register.html", message=message)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/search")
@login_required
def search():
    """Search for book"""
    """ if request.method == 'GET':
        return redirect("/") """
    q = request.args.get("q")  
    qTokens = nltk.word_tokenize(q) # Extract all the word
    queryInput = '%'.join(qTokens) + '%' # Join them with * in between and at the end. For example, "ac ri" will become ac*ri*
    rows = db.execute("SELECT * FROM books WHERE UPPER(title) LIKE UPPER(:q) OR UPPER(isbn) LIKE UPPER(:q) OR UPPER(author) LIKE UPPER(:q)", {"q": queryInput}).fetchall()
    return jsonify([dict(row) for row in rows])
    # return render_template("searchResults.html", rows=rows)

@app.route("/fullSearch", methods=['GET', 'POST'])
@login_required
def fullSearch():
    """When user click on Search to see all results"""
    if request.method == 'GET':
        return redirect("/")
    q = request.form.get("q")  
    qTokens = nltk.word_tokenize(q) # Extract all the word
    queryInput = '%'.join(qTokens) + '%' # Join them with * in between and at the end. For example, "ac ri" will become ac*ri*
    rows = db.execute("SELECT * FROM books WHERE UPPER(title) LIKE UPPER(:q) OR UPPER(isbn) LIKE UPPER(:q) OR UPPER(author) LIKE UPPER(:q)", {"q": queryInput}).fetchall()
    return render_template("searchResults.html", q=q, rows=rows)
    # return jsonify([dict(row) for row in rows])

@app.route("/book/<string:isbn>")
@login_required
def bookInfo(isbn):
    # Get the book and the reviews
    rows = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall() # get the book
    reviews = db.execute("SELECT username, rating, review FROM review WHERE isbn = :isbn", {"isbn": isbn}).fetchall() # get the reviews
    message = ''
    review_by_username = ''
    rating_by_username = 0

    # Get the Goodreads review data
    goodread_data = GoodreadsReview(isbn)
    goodread_rating = goodread_data['books'][0]['average_rating']
    goodread_rating_count = goodread_data['books'][0]['work_ratings_count']

    # Check if user has already reviewed
    for review in reviews:
        if session['username'] == review['username']:
            message = 'You have already reviewed this book'
            review_by_username = review['review']
            rating_by_username = review['rating']
            break
    
    # Finally, render the suitable template
    if message != '':
        return render_template("book.html", row=rows[0], reviews=reviews, successReview=message, user=session['username'], rating_by_username=rating_by_username, review_by_username=review_by_username, gr_rating=goodread_rating, gr_rating_count=goodread_rating_count)
    else:
        return render_template("book.html", row=rows[0], reviews=reviews, gr_rating=goodread_rating, gr_rating_count=goodread_rating_count)

@app.route("/review/<string:isbn>", methods=['GET', 'POST'])
@login_required
def review(isbn):
    if request.method == 'GET':
        return redirect(f"/book/{isbn}")
    db.execute("INSERT INTO review (isbn, rating, review, username) VALUES (:isbn, :rating, :review, :username)", {"isbn": isbn, "rating": request.form.get("user-rating"), "review": request.form.get("review"), "username": session['username']})
    db.commit()
    return redirect(f"/book/{isbn}")

@app.route("/api/<string:isbn>", methods=['GET'])
@login_required
def api(isbn):
    # Fetch basic info from local db
    rows = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    
    if len(rows) == 0:
        return jsonify({"error": "Book not found"}), 404

    # Fetch review info from Goodreads API
    goodread_data = GoodreadsReview(isbn)
    goodread_rating = goodread_data['books'][0]['average_rating']
    goodread_rating_count = goodread_data['books'][0]['work_ratings_count']

    # Construct JSON response
    json_data = {
        "title": rows[0]['title'],
        "author": rows[0]['author'],
        "year": rows[0]['year'],
        "isbn": rows[0]['isbn'],
        "review_count": goodread_rating_count,
        "average_score": goodread_rating
    }

    # Response
    return jsonify(json_data)