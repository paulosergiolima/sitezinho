import datetime
import glob
import io
import os
import shutil
import zipfile
from zoneinfo import ZoneInfo
from flask import Blueprint, json, jsonify, redirect, request, send_file, session, current_app
from werkzeug.utils import secure_filename

from sitezinho.models.database import db
from sitezinho.models.user import User

from sitezinho.services.config_service import get_single_vote_setting, get_vote_percentage_setting, set_config_value
from sitezinho.services.image_service import create_merged_image
from sitezinho.services.user_service import new_user


api = Blueprint('api', __name__)
@api.route("/vote", methods=["POST"])
def vote():
    try:
        json_request = request.json
        username = json_request[0].strip()
        votes = json_request[1]
        print(type(votes))
        
        new_user(username, votes)
        session["voted"] = True
        #f.write("The result of insertion : success\n")
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
        
    except Exception as e:
        print(e)
        db.session.rollback()
        #f.write(f"Error in vote: {str(e)}\n")
        return json.dumps({
            "success": False, 
            "error": "Database error"
        }), 500, {"ContentType": "application/json"}

#Sinto que isso está errado, uma api não deveria fazer redirect(?)
@api.route("/insert", methods=["POST"])
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
        if not uploaded_file.filename:
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
                            # Extract to sitezinho/static/images with secure filename
                            secure_name = secure_filename(os.path.basename(zip_file))
                            if secure_name:  # Make sure filename is not empty
                                zip_ref.extract(zip_file, "temp")
                                temp_file_path = os.path.join("temp", zip_file)
                                final_path = os.path.join("sitezinho/static/images", secure_name)
                                
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
                file_path = os.path.join("sitezinho/static/images", filename)
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
@api.route("/delete", methods=["DELETE"])
def delete_votes():
    """
    This function deletes all votes from the database.
    It clears the session and writes the session values to the log file.
    """
    db.session.query(User).delete()
    print(session)
    #f.write(f'{session.values}')
    #f.write("----")
    session.clear()
    #f.write(f'{session.values}')
    print(session)
    db.session.commit()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@api.route("/change_vote_unique")
def change_vote_unique():
    """Set voting mode to single vote (unique vote)"""
    success = set_config_value("single_vote", "True")
    #f.write("Vote mode changed to: single vote\n")
    return json.dumps({"success": success}), 200, {"ContentType": "application/json"}


@api.route("/change_vote_multiple")
def change_vote_multiple():
    """Set voting mode to multiple vote"""
    success = set_config_value("single_vote", "False")
    #f.write("Vote mode changed to: multiple vote\n")
    return json.dumps({"success": success}), 200, {"ContentType": "application/json"}


@api.route("/get_config", methods=["GET"])
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
        #f.write(f"Error getting config: {str(e)}\n")
        return json.dumps({
            "success": False,
            "error": "Failed to get configuration"
        }), 500, {"ContentType": "application/json"}


@api.route("/set_vote_percentage", methods=["POST"])
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
            #f.write(f"Vote percentage changed to: {percentage_int}%\n")
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
        #f.write(f"Error setting vote percentage: {str(e)}\n")
        return json.dumps({
            "success": False, 
            "error": "Database error occurred",
        }), 500, {"ContentType": "application/json"}


@api.route("/delete_vote", methods=["DELETE"])
def delete_vote():
    json_request = request.json
    print(json_request)
    user = db.get_or_404(User, json_request)
    db.session.delete(user)
    db.session.commit()
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@api.route("/delete_images", methods=["DELETE"])
def delete_images():
    """
    This function deletes all images from the sitezinho/static/images directory.
    It removes all files except the directory itself.
    """
    try:
        if not current_app.static_folder:
            return json.dumps({
                "success": False, 
                "error": "Static folder not configured"
            }), 500, {"ContentType": "application/json"}

        images_dir = os.path.join(current_app.static_folder, 'images')
        
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
                    #f.write(f"Deleted image: {file_path}\n")
                except Exception as e:
                    #f.write(f"Error deleting {file_path}: {str(e)}\n")
                    continue
        
        # Store success message in session
        session['upload_success'] = f"Todas as {files_count} imagens foram removidas com sucesso!"
        
        #f.write(f"Successfully deleted {files_count} images from {images_dir}\n")
        
        return json.dumps({
            "success": True, 
            "deleted_count": files_count
        }), 200, {"ContentType": "application/json"}
        
    except Exception as e:
        error_msg = f"Error deleting images: {str(e)}"
        #f.write(f"{error_msg}\n")
        session['upload_errors'] = [error_msg]
        
        return json.dumps({
            "success": False, 
            "error": "TODO better error msg"
        }), 500, {"ContentType": "application/json"}


@api.route("/voted")
def voted():
    flag = session.get("voted", False)
    return jsonify({"voted": flag})


@api.route("/check_user", methods=["POST"])
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
        return jsonify({"error": str(e)}), 500

@api.route("/merged_image")
def merged_image():
    """
    Generate and return a merged image containing all images from the sitezinho/static/images directory.
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
        images = os.listdir("./sitezinho/static/images")
        #f.write(f"Starting image merge process with {len(images)} files in directory\n")

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
            #f.write(f"Using fixed canvas size: {canvas_width}x{canvas_height}\n")
        else:
            # Use dynamic sizing
            fixed_size = None
            #f.write("Using dynamic canvas size based on image count\n")
        
        # Validate other parameters
        gap = max(0, min(gap, 20))  # Gap between 0 and 20 pixels
        output_format = 'PNG' if output_format == 'png' else 'JPEG'
        
        # Create the merged image
        merged_img = create_merged_image(
            images_dir="./sitezinho/static/images",
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
        #f.write(f"Generated merged image: {filename} ({size_info}, gap={gap}px, format={output_format})\n")
        
        return send_file(
            img_buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        error_msg = f"Error generating merged image: {str(e)}"
        #f.write(f"{error_msg}\n")
        return jsonify({
            "success": False,
            "error": "Failed to generate merged image"
        }), 500