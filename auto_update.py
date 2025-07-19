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
      <img src="https://raw.githubusercontent.com/CuteNewWebDeveloper/CuteNew_gallery/refs/heads/main/docs/images/Replace_me_as_real_jpg_file_name" alt="展示图片">
      <div class="caption">Replace_me_as_time · Replace_me_as_location · Replace_me_as_pg_name · 2021</div>
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
            # 遍历到第 n 行
            for i, row in enumerate(reader, 1):
                if i == n:
                    return row
            print(f"未找到第 {n} 行，文件行数不足")
            return None
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
        <label for="gotoPage">跳转到第</label>
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
        for index in range(28 if this_page_num < pages_num - 1 else image_count % 28):
            nth_row_content = get_nth_row_content(this_page_num * 28 + index + 1)
            print(this_page_num, nth_row_content)
            html_template = html_template.replace(f"***replace_me***",
                                                  f'''<a href="pages/Page{nth_row_content[1].replace('.jpg', '')}.html" class="gallery-item">
  <img src="https://raw.githubusercontent.com/CuteNewWebDeveloper/CuteNew_gallery/refs/heads/main/docs/images_preview/{nth_row_content[1]}" alt="图片{nth_row_content[0]}">
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
