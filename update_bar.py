
import math
import os
import hashlib
import csv
import uuid
from datetime import datetime
import os
import csv
import uuid
from datetime import datetime
from PIL import Image
import shutil
import math
from PIL import Image, ImageDraw, ImageFont

input_dir = "./docs/input_material"
existing_dir = "./docs/images"

def load_font(size=12):
    possible_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # GitHub Actions Ubuntu
        "/usr/share/fonts/truetype/arphic/ukai.ttc",               # 另一种 Ubuntu 中文字体
        "/System/Library/Fonts/STHeiti Light.ttc",                # macOS
        "C:/Windows/Fonts/simhei.ttf",                            # Windows SimHei 黑体
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    print("[Warning] No Chinese font found, using default.")
    return ImageFont.load_default()


def find_image_log_by_name(name, csv_path='./docs/images/image_log.csv'):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            image_filename = row.get('image_name', '')
            if image_filename[:-4] == name:
                return row  # 返回整行，作为字典
    return None  # 未找到则返回 None

def add_text_bar_to_image(image_path):
    if not os.path.isfile(image_path):
        print(f"Skipped (not a file): {image_path}")
        return  # 或者 return None

    # Extract filename from path and process it
    filename = os.path.basename(image_path)

    # Remove extension case-insensitively
    name, ext = os.path.splitext(filename)
    if ext.lower() != '.jpg':
        print(f"[Warning] Unexpected file extension: {ext}")
        return
    result = find_image_log_by_name(name)
    year =   result['time'].split()[0]  
    location = result['location']
    name = result['photographer_name']

  


    # Open the image
    img = Image.open(image_path)
    width, height = img.size

    # Create a new image with extra height for the black bar
    new_height = height + 17
    new_img = Image.new('RGB', (width, new_height), (0, 0, 0))  # Black background
    new_img.paste(img, (0, 0))  # Paste original image at the top

    # Create a draw object
    draw = ImageDraw.Draw(new_img)

    # Load a font (use default if arial.ttf is not available)
    try:
        
        font = load_font(12)

    except IOError:
        font = ImageFont.load_default()

    # Calculate text widths to avoid overlap
    left_text = f' © {year} {name}, All Rights Reserved.'
    right_text = f'[{time_of_photo}, {location}] CuteNew Gallery Images'
    left_text_bbox = draw.textbbox((0, 0), left_text, font=font)
    right_text_bbox = draw.textbbox((0, 0), right_text, font=font)
    left_text_width = left_text_bbox[2] - left_text_bbox[0]
    right_text_width = right_text_bbox[2] - right_text_bbox[0]

    # Define central region for parallelograms (50% of image width, avoiding text)
    margin = 20  # Extra padding to ensure no overlap with text
    central_width = width // 2
    start_x = max((width - central_width) // 2, left_text_width + margin + 10)
    end_x = min(width - (right_text_width + margin + 10), start_x + central_width)

    # Draw parallelogram pattern in the central region
    parallelogram_width = 20
    parallelogram_height = 10
    tilt = 5  # Horizontal offset for tilt effect
    spacing = 30  # Space between parallelograms
    y_top = height + 3  # Center parallelograms vertically in bar
    for x in range(start_x, end_x, spacing):
        points = [
            (x, y_top),
            (x + parallelogram_width, y_top),
            (x + parallelogram_width + tilt, y_top + parallelogram_height),
            (x + tilt, y_top + parallelogram_height)
        ]
        draw.polygon(points, fill=(255, 255, 255))  # White parallelograms

    # Calculate text positions
    # Adjust vertical alignment based on actual text height
    left_text_height = left_text_bbox[3] - left_text_bbox[1]
    text_y = height + (17 - left_text_height) // 2  # Center text vertically in 17px bar


    # Draw left-aligned text
    draw.text((10, text_y), left_text, fill=(255, 255, 255), font=font)

    # Draw right-aligned text
    draw.text((width - right_text_width - 10, text_y), right_text, fill=(255, 255, 255), font=font)

    # Save the new image
    output_path = os.path.join(os.path.dirname(image_path), f"{filename}")
    new_img.save(output_path, quality=100)

    return name, output_path


def crop_bottom_bar(image_path):
    # Open the image
    if not os.path.isfile(image_path):
        return
    img = Image.open(image_path)
    width, height = img.size

    # Check if image height is at least 17 pixels to crop
    if height < 17:
        raise ValueError("Image height is too small to crop 17 pixels.")

    # Crop the bottom 17 pixels
    cropped_img = img.crop((0, 0, width, height - 17))

    # Save the cropped image
    filename = os.path.basename(image_path)
    output_path = os.path.join(os.path.dirname(image_path), f"{filename}")
    cropped_img.save(output_path, quality=100)

    return output_path



image_dir = './docs/images'

for filename in os.listdir(image_dir):
    if not filename.lower().endswith('.jpg'):
        print(f"Skipped: {filename}")
        continue
    path = os.path.join(image_dir, filename)
    print(f"Processing: {path}")
    crop_bottom_bar(path)
    add_text_bar_to_image(path)
