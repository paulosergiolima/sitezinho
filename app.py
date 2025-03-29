
# It's okay man
import datetime
from os import listdir
import os
from os.path import isfile, join
from flask import Flask, json, redirect, render_template, request
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
import zipfile
import glob
from zoneinfo import ZoneInfo

global unique_vote
unique_vote = True
f = open("logs.txt", 'a')
load_dotenv()

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
    created: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now())

    def __init__(self, *, username: str, votes: list):
        self.username = username
        self.votes = votes


with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():
    onlyfiles = [f for f in listdir("./static/images") if isfile(join("./static/images", f))]
    count = len(onlyfiles)
    print(datetime.datetime.now(ZoneInfo("America/Sao_Paulo")).second)
    return render_template('index.html', images = onlyfiles, unique_vote=unique_vote, count=count)

@app.route('/vote', methods = ['POST'])
def vote():
    json_request = request.json
    ballot = {"Name": json_request[0], "Votes": request.json[1]}
    f.write(f"Person votes: {ballot}\n")
    new_user = User(username=json_request[0], votes=json_request[1])
    db.session.add(new_user)
    db.session.commit()
    f.write("The result of insertion : {x}")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
@app.route('/count')
def count():
    secret_votes = []
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    for user_id, user in enumerate(users):
        secret_votes.append(user.votes)
    secret_votes = [
        x 
        for xs in secret_votes
        for x in xs
    ]
    votes = {i:secret_votes.count(i) for i in secret_votes}
    votes = {k: v for k, v in sorted(votes.items(), key=lambda item: item[1], reverse=True)}
    for key, value in votes.items():
        print(key, value)
    return render_template('count.html', images = votes)

@app.route('/admin')
def admin():
    count_votes = db.session.query(User).count()
    users = db.session.execute(db.select(User)).scalars().all()
    return render_template('admin.html', count=count_votes, users=users)
@app.route('/insert', methods = ['POST'])
def insert():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)

    #it's a zip file
    files = glob.glob('static/images/*')
    for f in files:
        os.remove(f)
    with zipfile.ZipFile(uploaded_file.filename, "a") as zip_ref:
        zip_ref.extractall("static/images")
    return redirect('/')
@app.route('/delete', methods = ['DELETE'])
def delete_votes():
    db.session.query(User).delete()
    db.session.commit()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/change_vote_unique')
def change_vote_unique():
    global unique_vote
    unique_vote = True
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/change_vote_multiple')
def change_vote_multiple():
    global unique_vote
    unique_vote = False
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
