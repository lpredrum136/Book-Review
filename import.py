"""Provided for you in this project is a file called books.csv, 
which is a spreadsheet in CSV format of 5000 different books. 
Each one has an ISBN number, a title, an author, and a publication year. 
In a Python file called import.py separate from your web application, 
write a program that will take the books and import them into your PostgreSQL database. 
You will first need to decide what table(s) to create, what columns those tables should have, 
and how they should relate to one another. Run this program by running python3 import.py 
to import the books into your database, and submit this program with the rest of your project code."""

"""BUt this way is too slow, so I imported directly with pgAdmin4
Right click table name, choose Import/Export
Choose Import switch
Choose file
Tab column -> remove "id" column if csv file does not have an id column
"""

import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine("postgres://nmveeatzgvsvqz:71ac6602574819f555d2c89d38367361795ddf1474c92c763f1ecc67b2951d0c@ec2-23-21-156-171.compute-1.amazonaws.com:5432/d1ta26pb3lelfn")
db = scoped_session(sessionmaker(bind=engine))

# open file
f = open("books.csv")
reader = csv.reader(f)

# export to database
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()