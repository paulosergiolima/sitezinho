import datetime
from zoneinfo import ZoneInfo
from flask import json

from sitezinho.models.user import User, Vote
from sitezinho.models.database import db


def new_user(username: str, votes: list):
    date = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))
    print(votes)
    print(username, votes)
    
    existing_user = db.session.execute(
                db.select(User).where(User.username == username)
            ).scalar_one_or_none()
            
    if existing_user:
        return json.dumps({
            "success": False, 
            "error": "User has already voted"
        }), 400, {"ContentType": "application/json"}
    
    ballot = {"Name": username, "Votes": votes}
    #f.write(f"Person votes: {ballot}\n")
    
    new_user = User(
        username=username, # type: ignore
        created=datetime.datetime.now(ZoneInfo("America/Sao_Paulo")), # type: ignore
    )
    vote_instances: list[Vote] = [Vote(image_name=image_name,created=date,user=new_user) for image_name in votes] # pyright: ignore[reportCallIssue]
    db.session.add(new_user)
    db.session.add_all(vote_instances)
    db.session.commit()

def delete_votes():
    db.session.query(Vote).delete()
    db.session.query(User).delete()
    db.session.commit()