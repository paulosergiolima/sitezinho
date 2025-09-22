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
import math
from PIL import Image, ImageDraw, ImageFont
import io
from flask import send_file

FILENAME = "artes.zip"
f = open("logs.txt", "a")
load_dotenv()


mysql_url = os.getenv("mysql_url")
if not mysql_url:
    raise RuntimeError("mysql_url environment variable not set. Check your .env file.")


app = Flask(__name__)

mysql_url = os.getenv("mysql_url")
f.write(f"{mysql_url} \n")
print(mysql_url)
# Ensure images directory exists inside the container to avoid FileNotFoundError
os.makedirs("./static/images", exist_ok=True)
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


class AppConfig(db.Model):
    """Model to store application configuration settings"""
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    config_value: Mapped[str] = mapped_column(String(255), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime)
    updated: Mapped[datetime.datetime] = mapped_column(DateTime)

    def __init__(self, *, config_key: str, config_value: str):
        self.config_key = config_key
        self.config_value = config_value
        self.created = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))
        self.updated = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))


def get_config_value(key: str, default_value: str = None) -> str:
    """Get configuration value from database"""
    config = db.session.execute(
        db.select(AppConfig).where(AppConfig.config_key == key)
    ).scalar_one_or_none()
    
    if config:
        return config.config_value
    return default_value


def set_config_value(key: str, value: str) -> bool:
    """Set configuration value in database"""
    try:
        config = db.session.execute(
            db.select(AppConfig).where(AppConfig.config_key == key)
        ).scalar_one_or_none()
        
        if config:
            # Update existing config
            config.config_value = value
            config.updated = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))
        else:
            # Create new config
            config = AppConfig(config_key=key, config_value=value)
            db.session.add(config)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        f.write(f"Error setting config {key}: {str(e)}\n")
        return False


def get_single_vote_setting() -> bool:
    """Get single vote setting from database"""
    value = get_config_value("single_vote", "True")
    return value.lower() == "true"


def get_vote_percentage_setting() -> int:
    """Get vote percentage setting from database"""
    value = get_config_value("vote_percentage", "50")
    try:
        return int(value)
    except ValueError:
        return 50


def initialize_default_configs():
    """Initialize default configuration values if they don't exist"""
    # Set default single_vote if not exists
    if not get_config_value("single_vote"):
        set_config_value("single_vote", "True")
    
    # Set default vote_percentage if not exists  
    if not get_config_value("vote_percentage"):
        set_config_value("vote_percentage", "50")


def create_merged_image(images_dir="./static/images", fixed_size=None, background_color=(240, 240, 240), gap_between_images=2):
    """
    Create a single image with fixed dimensions by combining all images from the specified directory.
    The function automatically calculates the best grid layout and image sizes to fit the fixed canvas.
    All images will have exactly the same size and be positioned with minimal gaps.
    
    Args:
        images_dir (str): Directory containing the images to merge
        fixed_size (tuple): Fixed canvas size (width, height) - default 1600x1600
        background_color (tuple): RGB background color for the merged image
        gap_between_images (int): Gap in pixels between images (0 = coladas, 2 = default small gap)
    
    Returns:
        PIL.Image: The merged image object with fixed dimensions and uniform image sizes
    """
    try:
        # Get all image files from the directory
        image_files = [
            f for f in listdir(images_dir) 
            if isfile(join(images_dir, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff'))
        ]
        
        # Log the number of images found
        f.write(f"Found {len(image_files)} images to merge\n")
        
        # Canvas will be created after determining size (fixed or dynamic)
        
        if not image_files:
            # Create a "No images" placeholder with default size
            placeholder_size = fixed_size if fixed_size else (800, 400)
            placeholder = Image.new('RGB', placeholder_size, background_color)
            draw = ImageDraw.Draw(placeholder)
            try:
                font = ImageFont.load_default()
                draw.text((placeholder_size[0]//2, placeholder_size[1]//2), "No images found", 
                         font=font, fill=(128, 128, 128), anchor="mm")
            except:
                draw.text((placeholder_size[0]//2 - 50, placeholder_size[1]//2), "No images found", fill=(128, 128, 128))
            return placeholder
        
        # Calculate optimal grid layout based on number of images
        num_images = len(image_files)
        
        # Calculate grid dimensions with minimum 6 columns
        grid_cols = max(6, math.ceil(math.sqrt(num_images)))
        grid_rows = math.ceil(num_images / grid_cols)
        
        # Adjust if we have too many empty slots, but keep minimum 6 columns
        while grid_cols * (grid_rows - 1) >= num_images and grid_rows > 1 and grid_cols > 6:
            grid_rows -= 1
        
        f.write(f"Using grid layout: {grid_cols}x{grid_rows} for {num_images} images\n")
        
        # If no fixed_size provided, calculate dynamic size based on grid
        if fixed_size is None:
            # Standard image size for good quality
            standard_image_size = 200
            outer_margin = 10
            
            # Calculate total canvas size needed
            canvas_width = (standard_image_size * grid_cols) + (gap_between_images * (grid_cols - 1)) + (outer_margin * 2)
            canvas_height = (standard_image_size * grid_rows) + (gap_between_images * (grid_rows - 1)) + (outer_margin * 2)
            
            # Create new canvas with dynamic size
            merged_image = Image.new('RGB', (canvas_width, canvas_height), background_color)
            image_size = standard_image_size
            
            f.write(f"Dynamic canvas size: {canvas_width}x{canvas_height} with standard image size: {image_size}x{image_size}\n")
        else:
            # Use provided fixed size
            canvas_width, canvas_height = fixed_size
            merged_image = Image.new('RGB', fixed_size, background_color)
            
            # Calculate spacing and image size to fit the fixed canvas
            outer_margin = 10
            
            # Calculate available space for images
            available_width = canvas_width - (outer_margin * 2)
            available_height = canvas_height - (outer_margin * 2)
            
            # Calculate space needed for gaps
            total_gap_width = gap_between_images * (grid_cols - 1)
            total_gap_height = gap_between_images * (grid_rows - 1)
            
            # Calculate exact image size to fill the available space
            image_width = (available_width - total_gap_width) // grid_cols
            image_height = (available_height - total_gap_height) // grid_rows
            
            # Make images square using the smaller dimension to ensure they fit
            image_size = min(image_width, image_height)
            
            f.write(f"Fixed canvas size: {canvas_width}x{canvas_height}, calculated image size: {image_size}x{image_size}\n")
        
        f.write(f"Gap between images: {gap_between_images}px, Outer margin: {outer_margin}px\n")
        
        # Process each image and place it in the grid
        for idx, image_file in enumerate(image_files):
            try:
                # Calculate grid position
                row = idx // grid_cols
                col = idx % grid_cols
                
                # Calculate exact position for this image (no centering, exact placement)
                paste_x = outer_margin + (col * (image_size + gap_between_images))
                paste_y = outer_margin + (row * (image_size + gap_between_images))
                
                # Open and crop the image to exact square size
                img_path = join(images_dir, image_file)
                with Image.open(img_path) as img:
                    # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Get original dimensions
                    orig_width, orig_height = img.size
                    
                    # Calculate crop area to make it square (center crop)
                    if orig_width > orig_height:
                        # Landscape: crop from left and right
                        crop_size = orig_height
                        left = (orig_width - crop_size) // 2
                        top = 0
                        right = left + crop_size
                        bottom = crop_size
                    else:
                        # Portrait or square: crop from top and bottom
                        crop_size = orig_width
                        left = 0
                        top = (orig_height - crop_size) // 2
                        right = crop_size
                        bottom = top + crop_size
                    
                    # Crop to square
                    img_cropped = img.crop((left, top, right, bottom))
                    
                    # Resize the cropped square to exact target size
                    img_final = img_cropped.resize((image_size, image_size), Image.Resampling.LANCZOS)
                    
                    # Paste the image at exact position
                    merged_image.paste(img_final, (paste_x, paste_y))
                    
                    f.write(f"Placed image {idx+1}/{num_images}: {image_file} at exact position ({paste_x}, {paste_y})\n")
                    
            except Exception as e:
                # Log error for individual image but continue processing others
                f.write(f"Error processing image {image_file}: {str(e)}\n")
                continue
        
        return merged_image
        
    except Exception as e:
        f.write(f"Error creating merged image: {str(e)}\n")
        # Return a simple error image with fixed size
        error_image = Image.new('RGB', fixed_size, (255, 100, 100))
        draw = ImageDraw.Draw(error_image)
        try:
            font = ImageFont.load_default()
            draw.text((fixed_size[0]//2, fixed_size[1]//2), "Error creating image", 
                     font=font, fill=(255, 255, 255), anchor="mm")
        except:
            draw.text((fixed_size[0]//2 - 80, fixed_size[1]//2), "Error creating image", fill=(255, 255, 255))
        return error_image


with app.app_context():
    db.create_all()
    # Initialize default configurations
    initialize_default_configs()


@app.route("/")
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
    
    # Get current settings from database
    vote_percentage = get_vote_percentage_setting()
    
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
    """Set voting mode to single vote (unique vote)"""
    success = set_config_value("single_vote", "True")
    f.write("Vote mode changed to: single vote\n")
    return json.dumps({"success": success}), 200, {"ContentType": "application/json"}


@app.route("/change_vote_multiple")
def change_vote_multiple():
    """Set voting mode to multiple vote"""
    success = set_config_value("single_vote", "False")
    f.write("Vote mode changed to: multiple vote\n")
    return json.dumps({"success": success}), 200, {"ContentType": "application/json"}


@app.route("/get_config", methods=["GET"])
def get_config():
    """Get current application configuration"""
    try:
        single_vote = get_single_vote_setting()
        vote_percentage = get_vote_percentage_setting()
        
        return json.dumps({
            "success": True,
            "config": {
                "single_vote": single_vote,
                "vote_percentage": vote_percentage
            }
        }), 200, {"ContentType": "application/json"}
        
    except Exception as e:
        f.write(f"Error getting config: {str(e)}\n")
        return json.dumps({
            "success": False,
            "error": "Failed to get configuration"
        }), 500, {"ContentType": "application/json"}


@app.route("/set_vote_percentage", methods=["POST"])
def set_vote_percentage():
    """Set the percentage of images a user can vote for in multiple choice mode"""
    try:
        data = request.get_json()
        percentage = data.get('percentage', 50)
        
        # Validate percentage range
        if not isinstance(percentage, (int, float)) or percentage < 1 or percentage > 100:
            return json.dumps({
                "success": False, 
                "error": "Percentage must be between 1 and 100"
            }), 400, {"ContentType": "application/json"}
        
        percentage_int = int(percentage)
        
        # Save to database
        success = set_config_value("vote_percentage", str(percentage_int))
        
        if success:
            f.write(f"Vote percentage changed to: {percentage_int}%\n")
            return json.dumps({
                "success": True, 
                "percentage": percentage_int
            }), 200, {"ContentType": "application/json"}
        else:
            return json.dumps({
                "success": False, 
                "error": "Failed to save configuration"
            }), 500, {"ContentType": "application/json"}
        
    except Exception as e:
        f.write(f"Error setting vote percentage: {str(e)}\n")
        return json.dumps({
            "success": False, 
            "error": "Database error occurred",
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
    
    # Sort by vote count (descending) - images with most votes first
    votes_sorted = dict(sorted(votes.items(), key=lambda item: len(item[1]), reverse=True))
    
    print(f"Votes sorted by count: {[(img, len(voters)) for img, voters in votes_sorted.items()]}")
    return render_template("votes.html", votes=votes_sorted)


def _get_votes_data_sorted() -> dict:
    """Build votes dict sorted by vote count (descending). Keys are image filenames.
    Structure: { image_name: { 'count': int, 'voters': [usernames...] } }
    """
    votes_data: dict[str, dict] = {}
    users = db.session.query(User).all()
    for user in users:
        for voted_image in user.votes:
            if voted_image not in votes_data:
                votes_data[voted_image] = {
                    'count': 0,
                    'voters': []
                }
            votes_data[voted_image]['count'] += 1
            votes_data[voted_image]['voters'].append(user.username)
    votes_data = {
        k: v for k, v in sorted(votes_data.items(), key=lambda item: item[1]['count'], reverse=True)
    }
    return votes_data


def _draw_text_wrapped(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int, start_xy: tuple[int, int], line_spacing: int = 4, fill=(50, 50, 50)) -> int:
    """Draw multi-line wrapped text within max_width. Returns bottom y after drawing."""
    x, y = start_xy
    words = text.split()
    line = ""
    for word in words:
        test_line = word if line == "" else f"{line} {word}"
        w, _ = draw.textbbox((0, 0), test_line, font=font)[2:4]
        if w <= max_width:
            line = test_line
        else:
            draw.text((x, y), line, font=font, fill=fill)
            y += font.size + line_spacing
            line = word
    if line:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_spacing
    return y


def _generate_results_image() -> Image.Image:
    """Generate a composite PNG showing images with vote counts and voters list, similar to /count page."""
    votes_data = _get_votes_data_sorted()

    # Layout settings
    canvas_width = 1600
    margin = 24
    gutter = 16
    thumb_size = 180
    column_gap = 24
    text_area_width = canvas_width - (margin * 2) - thumb_size - column_gap

    # Fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Pre-compute height
    y = margin
    draw_dummy = ImageDraw.Draw(Image.new('RGB', (canvas_width, 10)))
    section_spacer = 18
    total_height = y
    for image_name, info in votes_data.items():
        # Title + count line height
        title_line = f"{image_name}  —  votos: {info['count']}"
        _, _, _, h_title = draw_dummy.textbbox((0, 0), title_line, font=title_font)
        # Voters text height (wrapped)
        voters_text = ", ".join(sorted(info['voters'])) if info['voters'] else ""
        # Roughly estimate wrapped height: assume ~8px per char width in default -> compute lines by measuring
        tmp_img = Image.new('RGB', (text_area_width, 10))
        tmp_draw = ImageDraw.Draw(tmp_img)
        h_y = _draw_text_wrapped(tmp_draw, voters_text, small_font, text_area_width, (0, 0), line_spacing=4)
        block_height = max(thumb_size, h_title + 8 + h_y)  # Ensure space for thumbnail
        total_height += block_height + section_spacer
    total_height += margin

    # Create canvas
    canvas_height = max(total_height, margin * 2 + thumb_size)
    img = Image.new('RGB', (canvas_width, canvas_height), (250, 250, 250))
    draw = ImageDraw.Draw(img)

    # Header
    header_text = f"Resultados — {datetime.datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M')}"
    draw.text((margin, y), header_text, font=title_font, fill=(20, 20, 20))
    y += title_font.size + 12

    # Sections
    for image_name, info in votes_data.items():
        # Thumb
        thumb_box = (margin, y, margin + thumb_size, y + thumb_size)
        thumb_path = os.path.join("static", "images", image_name)
        try:
            with Image.open(thumb_path) as im:
                if im.mode != 'RGB':
                    im = im.convert('RGB')
                # Center-crop square
                w, h = im.size
                side = min(w, h)
                left = (w - side) // 2
                top = (h - side) // 2
                im = im.crop((left, top, left + side, top + side))
                im = im.resize((thumb_size, thumb_size), Image.Resampling.LANCZOS)
                img.paste(im, (thumb_box[0], thumb_box[1]))
        except Exception as e:
            # Draw placeholder if image not found
            draw.rectangle(thumb_box, fill=(220, 220, 220), outline=(180, 180, 180))
            draw.text((thumb_box[0] + 8, thumb_box[1] + 8), "No image", font=small_font, fill=(80, 80, 80))

        # Text area
        text_x = margin + thumb_size + column_gap
        text_y = y
        title_line = f"{image_name}  —  votos: {info['count']}"
        draw.text((text_x, text_y), title_line, font=title_font, fill=(30, 30, 30))
        text_y += title_font.size + 8
        voters_text = ", ".join(sorted(info['voters'])) if info['voters'] else ""
        text_y = _draw_text_wrapped(draw, voters_text, small_font, text_area_width, (text_x, text_y), line_spacing=4, fill=(50, 50, 50))

        # Advance y for next section
        y += max(thumb_size, (text_y - (y))) + section_spacer

    return img


@app.route("/export_results_image", methods=["GET"])
def export_results_image():
    """Export vote results as a nicely formatted PNG image with thumbnails and voters list."""
    try:
        out_img = _generate_results_image()
        buf = io.BytesIO()
        out_img.save(buf, format='PNG')
        buf.seek(0)
        timestamp = datetime.datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y%m%d_%H%M%S")
        filename = f"vote_results_{timestamp}.png"
        return send_file(buf, mimetype='image/png', as_attachment=True, download_name=filename)
    except Exception as e:
        f.write(f"Error exporting results image: {str(e)}\n")
        return jsonify({"success": False, "error": "Failed to export results"}), 500

@app.route("/merged_image")
def merged_image():
    """
    Generate and return a merged image containing all images from the static/images directory.
    All images are cropped to squares and have exactly the same size with uniform spacing.
    Layout uses minimum 6 columns and automatically adjusts canvas size unless specified.
    
    Query parameters:
        - width (int): Canvas width in pixels (optional, enables fixed size mode, range: 400-3000)
        - height (int): Canvas height in pixels (optional, enables fixed size mode, range: 400-3000)
        - gap (int): Gap between images in pixels (default: 2, range: 0-20, 0=coladas)
        - format (str): Output format - 'png' or 'jpeg' (default: 'png')
        
    Modes:
        - Dynamic size (default): Optimal canvas size based on image count, min 6 columns
        - Fixed size: Specify both width and height to force specific canvas dimensions
    """
    try:
        # List and count images for logging
        images = os.listdir("./static/images")
        f.write(f"Starting image merge process with {len(images)} files in directory\n")

        # Get query parameters with defaults
        canvas_width = request.args.get('width', type=int)  # None by default for dynamic sizing
        canvas_height = request.args.get('height', type=int)  # None by default for dynamic sizing
        gap = request.args.get('gap', 2, type=int)  # Gap between images
        output_format = request.args.get('format', 'png').lower()
        
        # Determine if using fixed or dynamic size
        if canvas_width and canvas_height:
            # Validate fixed size parameters
            canvas_width = max(400, min(canvas_width, 3000))  # Limit between 400 and 3000 pixels
            canvas_height = max(400, min(canvas_height, 3000))  # Limit between 400 and 3000 pixels
            fixed_size = (canvas_width, canvas_height)
            f.write(f"Using fixed canvas size: {canvas_width}x{canvas_height}\n")
        else:
            # Use dynamic sizing
            fixed_size = None
            f.write("Using dynamic canvas size based on image count\n")
        
        # Validate other parameters
        gap = max(0, min(gap, 20))  # Gap between 0 and 20 pixels
        output_format = 'PNG' if output_format == 'png' else 'JPEG'
        
        # Create the merged image
        merged_img = create_merged_image(
            images_dir="./static/images",
            fixed_size=fixed_size,
            background_color=(240, 240, 240),  # Light gray background
            gap_between_images=gap
        )
        
        # Save image to memory buffer
        img_buffer = io.BytesIO()
        merged_img.save(img_buffer, format=output_format, quality=95)
        img_buffer.seek(0)
        
        # Determine file extension and mimetype
        file_extension = 'png' if output_format == 'PNG' else 'jpg'
        mimetype = 'image/png' if output_format == 'PNG' else 'image/jpeg'
        
        # Generate filename with current timestamp
        timestamp = datetime.datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y%m%d_%H%M%S")
        
        if fixed_size:
            filename = f"merged_images_{canvas_width}x{canvas_height}_{timestamp}.{file_extension}"
            size_info = f"canvas={canvas_width}x{canvas_height}"
        else:
            actual_size = merged_img.size
            filename = f"merged_images_dynamic_{actual_size[0]}x{actual_size[1]}_{timestamp}.{file_extension}"
            size_info = f"dynamic_size={actual_size[0]}x{actual_size[1]}"
        
        # Log the operation
        f.write(f"Generated merged image: {filename} ({size_info}, gap={gap}px, format={output_format})\n")
        
        return send_file(
            img_buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        error_msg = f"Error generating merged image: {str(e)}"
        f.write(f"{error_msg}\n")
        return jsonify({
            "success": False,
            "error": "Failed to generate merged image"
        }), 500



