print('hello world')

import os
import hashlib

input_dir = "CuteNew_gallery/docs/input_material"
existing_dir = "CuteNew_gallery/docs/images"

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
    print(f"Processing new file: {file_path}")
    # 将来这里可以放入图片重命名、压缩等操作
    pass

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
