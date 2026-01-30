import datetime
from zoneinfo import ZoneInfo
from flask import json

from sitezinho.models.user import User
from sitezinho.models.database import db


def new_user(username: str, votes):
    print(type(votes))
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
        username=username,
        votes=votes,
        created=datetime.datetime.now(ZoneInfo("America/Sao_Paulo")),
    )
    db.session.add(new_user)
    db.session.commit()