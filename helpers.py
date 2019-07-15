from flask import session, redirect
from functools import wraps
import requests, json

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def GoodreadsReview(isbn):
    """Get review from Goodreads API
    https://www.goodreads.com/api"""

    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "CBCgNmPmOvNmjjf2oy63g", "isbns": isbn})
    return response.json()
