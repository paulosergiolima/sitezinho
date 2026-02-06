import math
from flask import Blueprint, json, render_template, session
from sqlalchemy import func

from sitezinho.models.user import User, Vote
from sitezinho.services.config_service import get_single_vote_setting, get_vote_percentage_setting
from sitezinho.models.database import db
from sitezinho.services.image_service import get_image_files

views = Blueprint('views', __name__,template_folder='templates')


@views.route('/')
def hello_world() -> str:
    onlyfiles: list[str] = get_image_files()
    print(f"this is inside views.py {onlyfiles}")
    count: int = len(onlyfiles)

    # Get current settings from database
    single_vote: bool = get_single_vote_setting()
    vote_percentage: int = get_vote_percentage_setting()

    # Create vote configuration JSON
    vote_config_json: str = json.dumps({
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
def count() -> str:
    # Dictionary to store vote count and voters for each image
    votes_data: dict[str, dict[str,list[str]]] = {}
    vote_counts = (
        db.session.query(
            Vote.image_name,
            func.count(Vote.id).label('vote_count'),
            func.group_concat(User.username).label('voters')
        )
        .join(User, Vote.user_id == User.id)
        .group_by(Vote.image_name)
        .order_by(func.count(Vote.id).desc())
        .all()
    )
    for image_name, vote_count, voters in vote_counts:
        votes_data[image_name] = {
            'count': vote_count,
            'voters': voters.split(',') if voters else []
        }
    

    return render_template("count.html", images=votes_data)


@views.route("/admin")
def admin():
    count_votes = db.session.query(User).count()
    users = db.session.execute(db.select(User)).scalars().all()

    # Clear upload messages after displaying them
    _upload_success = session.pop('upload_success', None)
    _upload_errors = session.pop('upload_errors', None)

    # Get image count for admin
    onlyfiles: list[str] = get_image_files()
    image_count: int = len(onlyfiles)

    # Get current settings from database
    vote_percentage: int = get_vote_percentage_setting()

    return render_template("admin.html", count=count_votes, users=users, vote_percentage=vote_percentage, image_count=image_count)


@views.route("/votes")
def votes():
    
    vote_counts = (
        db.session.query(
            Vote.image_name,
            func.group_concat(User.username).label('voters')
        )
        .join(User, Vote.user_id == User.id)
        .group_by(Vote.image_name)
        .order_by(func.count(Vote.id).desc())
        .all()
    )
    votes_data = {}
    for image_name, voters in vote_counts:
            votes_data[image_name] = set(voters.split(',')) if voters else set()

    print(f"Votes sorted by count: {[(img, len(voters)) for img, voters in votes_data.items()]}")
    return render_template("votes.html", votes=votes_data)
