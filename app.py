
# A very simple Flask Hello World app for you to get started with...
from os import listdir
import os
from os.path import isfile, join
from bson import BSON
from flask import Flask, after_this_request, render_template, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello_world():
    onlyfiles = [f for f in listdir("./static/images") if isfile(join("./static/images", f))]
    return render_template('index.html', images = onlyfiles)

@app.route('/vote', methods = ['POST'])
def vote():
    f = open("logs.txt", "a")
    uri = f'mongodb://sitezinho:sitezinho@urna-shard-00-00.yj774.mongodb.net:27017,urna-shard-00-01.yj774.mongodb.net:27017,urna-shard-00-02.yj774.mongodb.net:27017/?replicaSet=atlas-y8c7zw-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=urna'
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        mydb = client["urna"]
        votes = mydb["votes"]
        json_request = request.json
        ballot = {"Name": json_request[0], "Votes": request.json[1]}
        f.write(f"Person votes: {ballot}")
        print(ballot)
        x = votes.insert_one(ballot)
        f.write("The result of insertion : {x}")
        print(x)
    except Exception as e:
        f.write(f"Error: {e}")
        print(e)
    client.close()
    f.close()
    return "Worked"

    

