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
from werkzeug.utils import secure_filename
import shutil
import json
import math

global unique_vote, vote_percentage
FILENAME = "artes.zip"
unique_vote = True
vote_percentage = 50  # Default: user can vote for 50% of available images
f = open("logs.txt", "a")
load_dotenv()


app = Flask(__name__)
mysql_url = os.getenv("mysql_url")
f.write(f"{mysql_url} \n")
print(mysql_url)
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SERIALIZATION_FORMAT"] = 'json'
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 280}
app.config["SQLALCHEMY_DATABASE_URI"] = mysql_url
app.config["SESSION_REFRESH_EACH_REQUEST"] = False
app.secret_key = os.getenv("secret_key")
app.permanent_session_lifetime = datetime.timedelta(days=1)
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
)

db = SQLAlchemy(app)
app.config["SESSION_SQLALCHEMY"] = db
Session(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    votes: Mapped[list] = mapped_column(JSON)
    created: Mapped[datetime.datetime] = mapped_column(DateTime)

    def __init__(self, *, username: str, votes: list, created: datetime.datetime):
        self.username = username
        self.votes = votes
        self.created = created


with app.app_context():
    db.create_all()


@app.route("/")
def hello_world():
    onlyfiles = [
        f for f in listdir("./static/images") if isfile(join("./static/images", f))
    ]
    count = len(onlyfiles)
    print(datetime.datetime.now(ZoneInfo("America/Sao_Paulo")).second)
    
    # Create vote configuration JSON
    vote_config_json = json.dumps({
        "single_vote": unique_vote,
        "percentage": vote_percentage,
        "total_images": count,
        "max_votes": 1 if unique_vote else math.ceil(count * vote_percentage / 100),
    })
    
    return render_template(
        "index.html", 
        images=onlyfiles, 
        unique_vote=unique_vote, 
        count=count, 
        vote_percentage=vote_percentage,
        vote_config_json=vote_config_json
    )


@app.route("/vote", methods=["POST"])
def vote():
    try:
        json_request = request.json
        username = json_request[0].strip()
        votes = json_request[1]
        
        # Double-check if user already exists (backend safety)
        existing_user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar_one_or_none()
        
        if existing_user:
            return json.dumps({
                "success": False, 
                "error": "User has already voted"
            }), 400, {"ContentType": "application/json"}
        
        ballot = {"Name": username, "Votes": votes}
        f.write(f"Person votes: {ballot}\n")
        
        new_user = User(
            username=username,
            votes=votes,
            created=datetime.datetime.now(ZoneInfo("America/Sao_Paulo")),
        )
        db.session.add(new_user)
        db.session.commit()
        session["voted"] = True
        f.write("The result of insertion : success\n")
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
        
    except Exception as e:
        db.session.rollback()
        f.write(f"Error in vote: {str(e)}\n")
        return json.dumps({
            "success": False, 
            "error": "Database error"
        }), 500, {"ContentType": "application/json"}


@app.route("/count")
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


@app.route("/admin")
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
    
    return render_template("admin.html", count=count_votes, users=users, vote_percentage=vote_percentage, image_count=image_count)


@app.route("/insert", methods=["POST"])
def insert():
  
    # Define allowed image extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff'}
    
    def allowed_file(filename):
        """Check if file has allowed extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def is_zip_file(filename):
        """Check if file is a ZIP file"""
        return filename.lower().endswith('.zip')
    
    # Get uploaded files (can be multiple)
    uploaded_files = request.files.getlist("file")
    
    # Track processed files for feedback
    processed_files = []
    errors = []
    
    for uploaded_file in uploaded_files:
        if uploaded_file.filename == "":
            continue
            
        filename = secure_filename(uploaded_file.filename)
        
        if is_zip_file(filename):
            # Handle ZIP file - extract all images
            try:
                zip_path = os.path.join("temp", filename)
                os.makedirs("temp", exist_ok=True)
                uploaded_file.save(zip_path)
                
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    # Get list of files in ZIP
                    zip_files = zip_ref.namelist()
                    
                    for zip_file in zip_files:
                        # Skip directories and non-image files
                        if not zip_file.endswith('/') and allowed_file(zip_file):
                            # Extract to static/images with secure filename
                            secure_name = secure_filename(os.path.basename(zip_file))
                            if secure_name:  # Make sure filename is not empty
                                zip_ref.extract(zip_file, "temp")
                                temp_file_path = os.path.join("temp", zip_file)
                                final_path = os.path.join("static/images", secure_name)
                                
                                # Move file to final destination
                                os.rename(temp_file_path, final_path)
                                processed_files.append(secure_name)
                
                # Clean up temp ZIP file
                os.remove(zip_path)
                
            except Exception as e:
                errors.append(f"Erro ao processar ZIP {filename}: {str(e)}")
                
        elif allowed_file(filename):
            # Handle individual image file
            try:
                file_path = os.path.join("static/images", filename)
                uploaded_file.save(file_path)
                processed_files.append(filename)
                
            except Exception as e:
                errors.append(f"Erro ao salvar {filename}: {str(e)}")
        else:
            errors.append(f"Arquivo não suportado: {filename}")
    
    # Clean up temp directory if it exists
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    
    # Store results in session for feedback
    if processed_files:
        session['upload_success'] = f"Processados {len(processed_files)} arquivo(s): {', '.join(processed_files[:3])}" + \
                                  ("..." if len(processed_files) > 3 else "")
    if errors:
        session['upload_errors'] = errors
    
    return redirect("/")


@app.route("/delete", methods=["DELETE"])
def delete_votes():
    """
    This function deletes all votes from the database.
    It clears the session and writes the session values to the log file.
    """
    db.session.query(User).delete()
    print(session)
    f.write(f'{session.values}')
    f.write("----")
    session.clear()
    f.write(f'{session.values}')
    print(session)
    db.session.commit()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/change_vote_unique")
def change_vote_unique():
    global unique_vote
    unique_vote = True
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/change_vote_multiple")
def change_vote_multiple():
    global unique_vote
    unique_vote = False
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/set_vote_percentage", methods=["POST"])
def set_vote_percentage():
    """Set the percentage of images a user can vote for in multiple choice mode"""
    global vote_percentage
    try:
        data = request.get_json()
        percentage = data.get('percentage', 50)
        
        # Validate percentage range
        if not isinstance(percentage, (int, float)) or percentage < 1 or percentage > 100:
            return json.dumps({
                "success": False, 
                "error": "Percentage must be between 1 and 100"
            }), 400, {"ContentType": "application/json"}
        
        vote_percentage = int(percentage)
        f.write(f"Vote percentage changed to: {vote_percentage}%\n")
        
        return json.dumps({
            "success": True, 
            "percentage": vote_percentage
        }), 200, {"ContentType": "application/json"}
        
    except Exception as e:
        f.write(f"Error setting vote percentage: {str(e)}\n")
        return json.dumps({
            "success": False, 
            "error": "TODO better error handling",
        }), 500, {"ContentType": "application/json"}


@app.route("/delete_vote", methods=["DELETE"])
def delete_vote():
    json_request = request.json
    print(json_request)
    user = db.get_or_404(User, json_request)
    db.session.delete(user)
    db.session.commit()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/delete_images", methods=["DELETE"])
def delete_images():
    """
    This function deletes all images from the static/images directory.
    It removes all files except the directory itself.
    """
    try:
        images_dir = os.path.join(app.static_folder, 'images')
        
        if not os.path.exists(images_dir):
            return json.dumps({
                "success": False, 
                "error": "Images directory not found"
            }), 404, {"ContentType": "application/json"}
        
        # Get list of files before deletion for logging
        files_before = glob.glob(os.path.join(images_dir, '*'))
        files_count = len([f for f in files_before if os.path.isfile(f)])
        
        # Delete all files in the images directory
        for file_path in files_before:
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    f.write(f"Deleted image: {file_path}\n")
                except Exception as e:
                    f.write(f"Error deleting {file_path}: {str(e)}\n")
        
        # Store success message in session
        session['upload_success'] = f"Todas as {files_count} imagens foram removidas com sucesso!"
        
        f.write(f"Successfully deleted {files_count} images from {images_dir}\n")
        
        return json.dumps({
            "success": True, 
            "deleted_count": files_count
        }), 200, {"ContentType": "application/json"}
        
    except Exception as e:
        error_msg = f"Error deleting images: {str(e)}"
        f.write(f"{error_msg}\n")
        session['upload_errors'] = [error_msg]
        
        return json.dumps({
            "success": False, 
            "error": "TODO better error msg"
        }), 500, {"ContentType": "application/json"}


@app.route("/voted")
def voted():
    flag = session.get("voted", False)
    return jsonify({"voted": flag})


@app.route("/check_user", methods=["POST"])
def check_user():
    """Check if a username has already voted"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        # Check if user exists in database
        existing_user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar_one_or_none()
        
        has_voted = existing_user is not None
        
        return jsonify({
            "username": username,
            "has_voted": has_voted,
            "session_voted": session.get("voted", False)
        })
        
    except Exception as e:
        print("error")
        #return jsonify({"error": str(e)}), 500


@app.route("/votes")
def votes():
    votes = {}
    users = db.session.query(User).all()
    for user in users:
        for vote in user.votes:
            if vote not in votes:
                votes[vote] = set()
            votes[vote].add(user.username)
    print(votes)
    return render_template("votes.html", votes=votes)
