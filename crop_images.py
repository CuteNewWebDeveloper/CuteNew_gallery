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

def main():
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
    main()
