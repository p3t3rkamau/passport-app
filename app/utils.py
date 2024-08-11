import json
import os

def get_pixels_from_inches(inches, dpi=300):
    return int(inches * dpi)

def resize_and_crop(image, target_width, target_height):
    ih, iw = image.shape[:2]
    scale = max(target_width / iw, target_height / ih)
    nw = int(iw * scale)
    nh = int(ih * scale)
    image_resized = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_AREA)
    x_center = nw // 2
    y_center = nh // 2
    crop_x1 = max(0, x_center - target_width // 2)
    crop_y1 = max(0, y_center - target_height // 2)
    crop_x2 = crop_x1 + target_width
    crop_y2 = crop_y1 + target_height
    cropped_image = image_resized[crop_y1:crop_y2, crop_x1:crop_x2]
    return cropped_image

def load_sizes():
    try:
        with open('sizes.json', 'r') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except FileNotFoundError:
        print("File not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}

def save_sizes(sizes):
    with open('sizes.json', 'w') as f:
        json.dump(sizes, f, indent=4)
