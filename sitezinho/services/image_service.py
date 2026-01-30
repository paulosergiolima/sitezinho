from os.path import isfile, join
from os import listdir
from PIL import Image, ImageDraw, ImageFont
import math


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
        #f.write(f"Found {len(image_files)} images to merge\n")
        
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
        
        #f.write(f"Using grid layout: {grid_cols}x{grid_rows} for {num_images} images\n")
        
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
            
            #f.write(f"Dynamic canvas size: {canvas_width}x{canvas_height} with standard image size: {image_size}x{image_size}\n")
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
            
            #f.write(f"Fixed canvas size: {canvas_width}x{canvas_height}, calculated image size: {image_size}x{image_size}\n")
        
        #f.write(f"Gap between images: {gap_between_images}px, Outer margin: {outer_margin}px\n")
        
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
                    
                    #f.write(f"Placed image {idx+1}/{num_images}: {image_file} at exact position ({paste_x}, {paste_y})\n")
                    
            except Exception as e:
                # Log error for individual image but continue processing others
                #f.write(f"Error processing image {image_file}: {str(e)}\n")
                continue
        
        return merged_image
        
    except Exception as e:
        #f.write(f"Error creating merged image: {str(e)}\n")
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