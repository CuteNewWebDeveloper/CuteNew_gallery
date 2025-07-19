import os
import hashlib

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

    # 后续逻辑可以继续写在这里


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
