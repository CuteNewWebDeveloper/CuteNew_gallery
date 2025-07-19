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


input_dir = "./docs/input_material"
existing_dir = "./docs/images"

def compute_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_existing_md5_map(directory):
    md5_map = {}
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            md5 = compute_md5(full_path)
            md5_map[md5] = full_path
    return md5_map


def process_new_file(file_path):
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)

    if ext.lower() != '.jpg':
        print(f"[Invalid] {filename} is not a JPG image. Deleting...")
        os.remove(file_path)
        return

    parts = name.split(" ")

    if len(parts) != 3:
        print(f"[Warning] {filename} does not split cleanly into 3 parts.")
        part1, part2, part3 = (parts + [""] * 3)[:3]  # 补齐不足3项
    else:
        part1, part2, part3 = parts

    print(f"[Valid] Processing JPG image: {filename}")
    print(f"  → Part1: {part1}, Part2: {part2}, Part3: {part3}")

    # Generate a random filename using UUID
    file_random_name = f"{uuid.uuid4()}.jpg"

    # Define CSV file path
    csv_path = "./docs/images/image_log.csv"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # Determine the next image_id
    image_id = 1
    if os.path.exists(csv_path):
        with open(csv_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            try:
                # Skip header and find the last image_id
                next(reader)  # Skip header
                last_row = None
                for last_row in reader:
                    pass
                if last_row and last_row[0].isdigit():
                    image_id = int(last_row[0]) + 1
            except StopIteration:
                pass

    # Append new row to CSV
    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header if file is empty
        if os.path.getsize(csv_path) == 0 if os.path.exists(csv_path) else True:
            writer.writerow(['image_id', 'image_name', 'time', 'location', 'photographer_name', 'note'])
        # Write new row with empty note
        writer.writerow([image_id, file_random_name, part1, part2, part3, ''])

    print(f"[Success] Added {file_random_name} to CSV with image_id {image_id}")

    # Define paths for copying
    gallery_path = os.path.join(".", "docs", "images", file_random_name)
    preview_path = os.path.join(".", "docs", "images_preview", file_random_name)

    # Ensure destination directories exist
    os.makedirs(os.path.dirname(gallery_path), exist_ok=True)
    os.makedirs(os.path.dirname(preview_path), exist_ok=True)

    # Copy original image to gallery
    shutil.copy(file_path, gallery_path)
    print(f"[Success] Copied {filename} to {gallery_path}")

    # Resize and copy image to preview
    with Image.open(file_path) as img:
        # Calculate new dimensions to maintain aspect ratio
        width, height = img.size
        new_width = 520
        new_height = int((new_width / width) * height)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized_img.save(preview_path, 'JPEG')
        print(f"[Success] Resized and copied {filename} to {preview_path} (width: {new_width}px)")
    
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>图片展示 - CuteNew Gallery</title>
  <link rel="icon" type="image/x-icon" href="../favicon.ico">

  <style>
    body {
      margin: 0;
      font-family: sans-serif;
      background-color: #000;
      color: white;
    }

    header {
      background-color: #122344;
      color: white;
      text-align: center;
      padding: 1em;
      font-size: 1.5em;
    }

    header img {
      height: 1.2em;
      vertical-align: middle;
      margin-right: 0.5em;
    }

    .container {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 2vh;
      box-sizing: border-box;
    }

    .image-wrapper {
      max-width: 90%;
      max-height: 80vh;
      background-color: #000;
      padding: 1em;
      box-shadow: 0 0 10px rgba(255,255,255,0.1);
    }

    .image-wrapper img {
      width: 100%;
      height: auto;
      display: block;
      margin: 0 auto;
      border-radius: 8px;
    }

    .caption {
      text-align: center;
      margin-top: 1em;
      font-size: 1em;
      color: #ccc;
    }
  </style>
</head>
<body>
  <header>
    <img src="../logo.png" alt="CuteNew Logo"> 图片展示 - CuteNew Gallery
  </header>
  <main class="container">
    <div class="image-wrapper">
      <img src="https://raw.githubusercontent.com/CuteNewWebDeveloper/CuteNew_gallery/refs/heads/main/docs/images/Replace_me_as_real_jpg_file_name" alt="展示图片">
      <div class="caption">Replace_me_as_time · Replace_me_as_location · Replace_me_as_pg_name · 2021</div>
    </div>
  </main>
  <br/><br/>
</body>
</html>
"""
    html_template = html_template.replace('Replace_me_as_real_jpg_file_name',file_random_name)
    html_template = html_template.replace("Replace_me_as_time",part1)
    html_template = html_template.replace("Replace_me_as_location", part2)
    html_template = html_template.replace("Replace_me_as_pg_name", part3)
    with open(os.path.join("./docs/pages", f"Page{file_random_name.replace('.jpg','')}.html"),'w',encoding='utf-8') as f:
        f.write(html_template)
    print(f"[Success] write page:{file_random_name.replace('.jpg',''),'.html'}")

    print(f"[Success] {filename} finish and is being removed.")
    os.remove(file_path)
    return
    
    # TODO:  后续逻辑可以继续写在这里


def main():
    if not os.path.exists(input_dir):
        print(f"{input_dir} does not exist.")
        return

    existing_md5s = get_existing_md5_map(existing_dir)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        if not os.path.isfile(input_path):
            continue

        md5 = compute_md5(input_path)

        if md5 in existing_md5s:
            print(f"[Duplicate] {filename} matches existing file. Deleting...")
            os.remove(input_path)
        else:
            process_new_file(input_path)

if __name__ == "__main__":
    main()
