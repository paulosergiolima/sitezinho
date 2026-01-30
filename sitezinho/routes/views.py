import datetime
import math
from os import listdir
from os.path import isfile,join
from zoneinfo import ZoneInfo
from flask import Blueprint, json, render_template, session

from sitezinho.models.user import User
from sitezinho.services.config_service import get_single_vote_setting, get_vote_percentage_setting
from sitezinho.models.database import db

views = Blueprint('views', __name__,template_folder='templates')

@views.route('/')
def hello_world():
    onlyfiles = [
        f for f in listdir("./static/images") if isfile(join("./static/images", f))
    ]
    count = len(onlyfiles)
    print(datetime.datetime.now(ZoneInfo("America/Sao_Paulo")).second)
    
    # Get current settings from database
    single_vote = get_single_vote_setting()
    vote_percentage = get_vote_percentage_setting()
    
    # Create vote configuration JSON
    vote_config_json = json.dumps({
        "single_vote": single_vote,
        "percentage": vote_percentage,
        "total_images": count,
        "max_votes": 1 if single_vote else math.ceil(count * vote_percentage / 100),
    })
    
    return render_template(
        "index.html", 
        images=onlyfiles, 
        unique_vote=single_vote, 
        count=count, 
        vote_percentage=vote_percentage,
        vote_config_json=vote_config_json
    )

@views.route("/count")
def count():
    # Dictionary to store vote count and voters for each image
    votes_data = {}
    
    # Get all users who voted
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    
    # Process each user's votes
    for user in users:
        for voted_image in user.votes:
            if voted_image not in votes_data:
                votes_data[voted_image] = {
                    'count': 0,
                    'voters': []
                }
            votes_data[voted_image]['count'] += 1
            votes_data[voted_image]['voters'].append(user.username)
    
    # Sort by vote count (descending)
    votes_data = {
        k: v for k, v in sorted(votes_data.items(), key=lambda item: item[1]['count'], reverse=True)
    }
    
    return render_template("count.html", images=votes_data)

@views.route("/admin")
def admin():
    count_votes = db.session.query(User).count()
    users = db.session.execute(db.select(User)).scalars().all()
    
    # Clear upload messages after displaying them
    upload_success = session.pop('upload_success', None)
    upload_errors = session.pop('upload_errors', None)
    
    # Get image count for admin
    onlyfiles = [
        f for f in listdir("./static/images") if isfile(join("./static/images", f))
    ]
    image_count = len(onlyfiles)
    
    # Get current settings from database
    vote_percentage = get_vote_percentage_setting()
    
    return render_template("admin.html", count=count_votes, users=users, vote_percentage=vote_percentage, image_count=image_count)

@views.route("/votes")
def votes():
    votes = {}
    users = db.session.query(User).all()
    for user in users:
        for vote in user.votes:
            if vote not in votes:
                votes[vote] = set()
            votes[vote].add(user.username)
    
    # Sort by vote count (descending) - images with most votes first
    votes_sorted = dict(sorted(votes.items(), key=lambda item: len(item[1]), reverse=True))
    
    print(f"Votes sorted by count: {[(img, len(voters)) for img, voters in votes_sorted.items()]}")
    return render_template("votes.html", votes=votes_sorted)