
# It's okay man
import datetime
from os import listdir
import os
from os.path import isfile, join
from flask import Flask, json, jsonify, redirect, render_template, request, session
from flask_session import Session
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
import zipfile
import glob
from zoneinfo import ZoneInfo

global unique_vote
FILENAME = "artes.zip"
unique_vote = True
f = open("logs.txt", 'a')
load_dotenv()



app = Flask(__name__)
mysql_url = os.getenv("mysql_url")
f.write(f'{mysql_url} \n')
print(mysql_url)
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 280}
app.config['SQLALCHEMY_DATABASE_URI'] = mysql_url
app.config['SESSION_REFRESH_EACH_REQUEST'] = False
app.secret_key = os.getenv("secret_key")
app.permanent_session_lifetime = datetime.timedelta(days=1)
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
)

db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db
Session(app)
class User(db.Model):
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50) ,unique=True, nullable=False)
    votes: Mapped[list] = mapped_column(JSON) 
    created: Mapped[datetime.datetime] = mapped_column(DateTime)

    def __init__(self, *, username: str, votes: list, created: datetime.datetime):
        self.username = username
        self.votes = votes
        self.created = created


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
    new_user = User(username=json_request[0], votes=json_request[1], created=datetime.datetime.now(ZoneInfo("America/Sao_Paulo")))
    db.session.add(new_user)
    db.session.commit()
    session.permanent = True
    session["voted"] = True
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
        uploaded_file.save(FILENAME)

    #it's a zip file
    files = glob.glob('static/images/*')
    for f in files:
        os.remove(f)
    with zipfile.ZipFile(FILENAME, "a") as zip_ref:
        zip_ref.extractall("static/images")
    session.clear()
    return redirect('/')
@app.route('/delete', methods = ['DELETE'])
def delete_votes():
    db.session.query(User).delete()
    session.clear()
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

@app.route('/delete_vote', methods = ['DELETE'])
def delete_vote():
    json_request = request.json
    print(json_request)
    user = db.get_or_404(User, json_request)
    print(user)
    db.session.delete(user)
    db.session.commit()
    print(user)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
@app.route('/voted')
def voted():
    flag = session.get("voted", False)
    return jsonify({'voted': flag})
@app.route('/votes')
def votes():
    votes = {}
    users = db.session.query(User).all()
    for user in users:
        for vote in user.votes:
            if vote not in votes:
                votes[vote] = set()
            votes[vote].add(user.username)
    print(votes)
    return render_template('votes.html', votes=votes)
