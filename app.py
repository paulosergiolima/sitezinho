
# A very simple Flask Hello World app for you to get started with...
from os import listdir
import os
from os.path import isfile, join
from bson import BSON
from flask import Flask, after_this_request, json, render_template, request
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


f = open("logs.txt", 'a')

load_dotenv()

#class Base(DeclarativeBase):
 #   pass

app = Flask(__name__)
mysql_url = "mysql+mysqldb://sitezinho:sitezinho@localhost/kinipk$urna"
f.write(f'{mysql_url} \n')
print(mysql_url)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 280}
app.config['SQLALCHEMY_DATABASE_URI'] = mysql_url
db = SQLAlchemy(app)

class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50) ,unique=True, nullable=False)
    votes: Mapped[list] = mapped_column(JSON)

    def __init__(self, *, username: str, votes: list):
        self.username = username
        self.votes = votes


with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():
    onlyfiles = [f for f in listdir("./static/images") if isfile(join("./static/images", f))]
    return render_template('index.html', images = onlyfiles)

@app.route('/vote', methods = ['POST'])
def vote():
    json_request = request.json
    ballot = {"Name": json_request[0], "Votes": request.json[1]}
    f.write(f"Person votes: {ballot}\n")
    new_user = User(username=json_request[0], votes=json_request[1])
    db.session.add(new_user)
    db.session.commit()
    db.session.close()
    f.write("The result of insertion : {x}")
    f.close()
    return "Worked"



