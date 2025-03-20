
# A very simple Flask Hello World app for you to get started with...
from os import listdir
import os
from os.path import isfile, join
from bson import BSON
from flask import Flask, after_this_request, render_template, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = load_dotenv("mysql_url")
db = SQLAlchemy(app)

class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)

@app.route('/')
def hello_world():
    onlyfiles = [f for f in listdir("./static/images") if isfile(join("./static/images", f))]
    return render_template('index.html', images = onlyfiles)

@app.route('/vote', methods = ['POST'])
def vote():
    f = open("logs.txt", 'a')
    json_request = request.json
    ballot = {"Name": json_request[0], "Votes": request.json[1]}
    f.write(f"Person votes: {ballot}")
    print(ballot)
    f.write("The result of insertion : {x}")
    f.close()
    return "Worked"



