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


def resize_image(image_path):
    # Ensure the file exists
    if not os.path.isfile(image_path):
        print(f"File {image_path} does not exist.")
        return

    try:
        # Open the image
        with Image.open(image_path) as img:
            # Get image dimensions
            width, height = img.size
            max_dimension = max(width, height)

            # Check if resizing is needed
            if max_dimension > 1920:
                # Calculate the scaling factor
                scale = 1920 / max_dimension
                new_width = int(width * scale)
                new_height = int(height * scale)

                # Resize the image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Convert to RGB if necessary (for PNG or other formats with transparency)
                if resized_img.mode in ('RGBA', 'P'):
                    resized_img = resized_img.convert('RGB')

                # Define output path in the same directory
                output_filename = f"{os.path.basename(image_path)}"
                if image_path.lower().endswith(('.png', '.bmp', '.tiff')):
                    output_filename = output_filename.rsplit('.', 1)[0] + '.jpg'
                output_path = os.path.join(os.path.dirname(image_path), output_filename)

                # Save the resized image with quality 95
                resized_img.save(output_path, 'JPEG', quality=95)
                print(f"Resized and saved: {output_path}")
            else:
                print(f"No resizing needed for: {image_path}")

    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")


# Load a font that supports Chinese (use fallback if not available)
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

    parts = name.split()
    if len(parts) < 3:
        print(f"[Warning] {filename} does not split cleanly into at least 3 parts.")
        time_of_photo = parts[0] if len(parts) > 0 else ""
        location = parts[1].upper() if len(parts) > 1 else ""
        name = ""
    else:
        time_of_photo = parts[0]
        location = parts[1].upper()
        name = ' '.join(parts[2:])

    year = time_of_photo.split('.')[0] if '.' in time_of_photo else time_of_photo

    # Extract year from time_of_photo (before the dot)
    year = time_of_photo.split('.')[0] if '.' in time_of_photo else time_of_photo


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


def process_new_file(file_path):
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)

    if ext.lower() != '.jpg':
        print(f"[Invalid] {filename} is not a JPG image. Deleting...")
        os.remove(file_path)
        return

    parts = name.split(" ")
    
    if len(parts) < 3:
        print(f"[Warning] {filename} does not split cleanly into 3 parts.")
        part1, part2, part3 = (parts + [""] * 3)[:3]
    else:
        part1 = parts[0]
        part2 = parts[1]
        part3 = ' '.join(parts[2:])

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
    crop_bottom_bar(file_path)
    with Image.open(file_path) as img:
        # Calculate new dimensions to maintain aspect ratio
        width, height = img.size
        new_width = 380
        new_height = int((new_width / width) * height)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized_img.save(preview_path, 'JPEG', quality=55)
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
      <img src="../images/Replace_me_as_real_jpg_file_name" alt="展示图片">
      <div class="caption">Replace_me_as_time · Replace_me_as_location · Replace_me_as_pg_name</div>
    </div>
  </main>
  <br/><br/>
</body>
</html>
"""
    html_template = html_template.replace('Replace_me_as_real_jpg_file_name', file_random_name)
    html_template = html_template.replace("Replace_me_as_time", part1)
    html_template = html_template.replace("Replace_me_as_location", part2)
    html_template = html_template.replace("Replace_me_as_pg_name", part3)
    with open(os.path.join("./docs/pages", f"Page{file_random_name.replace('.jpg', '')}.html"), 'w',
              encoding='utf-8') as f:
        f.write(html_template)
    print(f"[Success] write page:{file_random_name.replace('.jpg', ''), '.html'}")

    print(f"[Success] {filename} finish and is being removed.")
    os.remove(file_path)
    return

    # TODO:  后续逻辑可以继续写在这里


def count_image_log_rows():
    try:
        with open('./docs/images/image_log.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            # 跳过表头
            next(reader, None)
            # 计数非表头行
            row_count = sum(1 for row in reader)
            return row_count
    except FileNotFoundError:
        print("文件 './docs/images/image_log.csv' 未找到")
        return 0
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return 0


def get_nth_row_content(n):
    try:
        with open('./docs/images/image_log.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            # 跳过表头
            next(reader, None)
            # 将所有行读入列表
            rows = list(reader)
            # 计算总行数
            total_rows = len(rows)
            # 检查 n 是否有效
            if n <= 0 or n > total_rows:
                print(f"无效的行号 {n}，文件有效行数为 {total_rows}")
                return None
            # 返回倒数第 n 行
            return rows[total_rows - n]
    except FileNotFoundError:
        print("文件 './docs/images/image_log.csv' 未找到")
        return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None


def main():
    if not os.path.exists(input_dir):
        print(f"{input_dir} does not exist.")
        return

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        resize_image(input_path)
        add_text_bar_to_image(input_path)

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
    # 完成并生index.html
    image_count = count_image_log_rows()
    pages_num = math.ceil(image_count / 28)
    for this_page_num in range(pages_num):
        html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CuteNew Gallery</title>
  <link rel="icon" type="image/x-icon" href="favicon.ico">

  <style>
    body {
      margin: 0;
      font-family: sans-serif;
      background-color: #f5f5f5;
    }
    header {
      background-color: #122344;
      color: white;
      text-align: center;
      padding: 1em;
      font-size: 1.5em;
    }
    .gallery {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 16px;
      padding: 16px;
    }
    .gallery-item {
      background-color: white;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      transition: transform 0.2s ease;
    }
    .gallery-item:hover {
      transform: scale(1.03);
    }
    .gallery-item img {
      width: 100%;
      height: auto;
      display: block;
    }
    .caption {
      padding: 8px;
      text-align: center;
      font-size: 0.9em;
      color: #333;
    }
    .caption.tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  padding: 8px;
}

.tag {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.8em;
  font-weight: 500;
  border-radius: 999px;
  color: white;
  background-color: #888;
  transition: background-color 0.3s ease;
}

/* 循环色系 */
.tag1 { background-color: #007bff; }  /* 蓝 */
.tag2 { background-color: #28a745; }  /* 绿 */
.tag3 { background-color: #ffc107; color: black; }  /* 黄 */
.tag4 { background-color: #dc3545; }  /* 红 */

/* 深色模式微调（可选） */
@media (prefers-color-scheme: dark) {
  .tag3 { background-color: #ffca2c; color: black; }
}

  .pagination a {
    margin: 0 6px;
    text-decoration: none;
    color: #0077cc;
    font-weight: bold;
  }
  .pagination a:hover {
    text-decoration: underline;
  }


      .goto-container {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 16px;
  }

  .goto-container input[type="number"] {
    width: 60px;
    padding: 4px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 6px;
    text-align: center;
    outline: none;
    transition: border-color 0.2s;
  }

  .goto-container input[type="number"]:focus {
    border-color: #0077cc;
  }

  .goto-container button {
    background-color: #0077cc;
    color: white;
    border: none;
    padding: 6px 14px;
    font-size: 14px;
    border-radius: 6px;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    transition: background-color 0.3s, transform 0.1s;
  }

  .goto-container button:hover {
    background-color: #005fa3;
  }

  .goto-container button:active {
    transform: scale(0.97);
  }

  </style>
</head>
<body>
  <header>
    <img src="logo.png" alt="CuteNew Logo" style="height: 1.2em; vertical-align: middle;">  欢迎来到
CuteNew
    Gallery
  </header>
  <main class="gallery">











***replace_me***


      </main>





<div class="pagination" style="text-align: center; margin: 40px 0;">
  <script>
    const currentPage = **replace_me_as_Current_pages********; // 当前页码
    const totalPages = **replace_me_as_totalPages********; // 总页数
    const range = 2; // 当前页前后展示的页数范围
    let html = '';

    // 首页 + 上一页
    if (currentPage > 1) {
      html += `<a href="${currentPage === 2 ? 'index.html' : 'page' + (currentPage - 1) + '.html'}">« 上一页</a> `;
      html += `<a href="index.html">首页</a> `;
    }

    // 前置页码
    for (let i = Math.max(1, currentPage - range); i < currentPage; i++) {
      html += `<a href="${i === 1 ? 'index.html' : 'page' + i + '.html'}">${i}</a> `;
    }

    // 当前页高亮
    html += `<span style="margin: 0 8px; font-weight: bold; color: gray;">${currentPage}</span>`;

    // 后置页码
    for (let i = currentPage + 1; i <= Math.min(totalPages, currentPage + range); i++) {
      html += `<a href="page${i}.html">${i}</a> `;
    }

    // 下一页 + 尾页
    if (currentPage < totalPages) {
      html += `<a href="page${currentPage + 1}.html">下一页 »</a> `;
      html += `<a href="page${totalPages}.html">尾页</a>`;
    }

    // 跳转输入框
    html += `
      <br/><br/>
      <div class="goto-container">
        <label for="gotoPage">共**replace_me_as_totalPages********页，跳转到第</label>
        <input id="gotoPage" type="number" min="1" max="${totalPages}" value="${currentPage}">
        <span>页</span>
        <button onclick="gotoPage()">跳转</button>
      </div>
    `;

    // 写入到页面中
    document.write(html);

    // 跳转函数
    function gotoPage() {
      const page = parseInt(document.getElementById('gotoPage').value);
      if (isNaN(page) || page < 1 || page > totalPages) {
        alert('请输入有效的页码！');
        return;
      }
      location.href = page === 1 ? 'index.html' : `page${page}.html`;
    }
  </script>
</div>


  

  
</body>
</html>
"""
        print(this_page_num,pages_num,image_count)
        for index in range(28 if this_page_num < pages_num - 1 else image_count % 28):
            nth_row_content = get_nth_row_content(this_page_num * 28 + index + 1)
            print(this_page_num, nth_row_content)
            print('replace',nth_row_content)
            html_template = html_template.replace(f"***replace_me***",
                                                  f'''<a href="pages/Page{nth_row_content[1].replace('.jpg', '')}.html" class="gallery-item">
  <img src="images_preview/{nth_row_content[1]}" alt="图片{nth_row_content[0]}">
  <div class="caption tags">
  <span class="tag tag1">{nth_row_content[2]}</span>
  <span class="tag tag2">{nth_row_content[3]}</span>
  <span class="tag tag3">{nth_row_content[4]}</span>
</div>

</a>

***replace_me***''')
        html_template = html_template.replace('***replace_me***', '')
        html_template = html_template.replace('**replace_me_as_Current_pages********', str(this_page_num + 1))
        html_template = html_template.replace('**replace_me_as_totalPages********', str(pages_num))
        with open('./docs/index.html' if this_page_num == 0 else f'./docs/page{this_page_num + 1}.html', 'w',
                  encoding='utf-8') as f:
            f.write(html_template)


if __name__ == "__main__":
    main()





import os
from PIL import Image

def crop_to_16_10(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        target_ratio = 16 / 10
        current_ratio = width / height

        if abs(current_ratio - target_ratio) < 0.01:
            print(f"Skipping {image_path}: Already at 16:10 ratio")
            return

        if current_ratio > target_ratio:
            # Image is too wide: crop width
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            img_cropped = img.crop((left, 0, left + new_width, height))
        else:
            # Image is too tall: crop height
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            img_cropped = img.crop((0, top, width, top + new_height))

        # Save cropped image, overwriting original
        img_cropped.save(image_path, quality=95)
        print(f"Cropped {image_path} to 16:10")

def main1():
    target_dir = os.getenv('TARGET_DIR', './docs/images_preview')
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp')

    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(supported_formats):
                file_path = os.path.join(root, file)
                try:
                    crop_to_16_10(file_path)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    main1()
