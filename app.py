from flask import Flask, request, render_template, send_from_directory, send_file, make_response, jsonify, redirect
from mtcnn import MTCNN
import cv2
import numpy as np
import os
from PIL import Image
import json


app = Flask(__name__)

# Initialize the MTCNN face detector
detector = MTCNN()

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

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

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No image file provided", 400

        image = request.files['image']
        img_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(img_path)

        # Read the image using OpenCV
        img = cv2.imread(img_path)

        # Detect faces
        detections = detector.detect_faces(img)
        if len(detections) == 0:
            return "No face detected", 400

        # Get the bounding box for the first detected face
        bounding_box = detections[0]['box']
        x, y, width, height = bounding_box

        # Increase the top margin to avoid cutting off the head
        # Calculate the margin to include some chest area and space above the head
        chest_extension = int(height * 0.4)  # Increased chest area (was 0.5)
        margin = int(0.4 * width)  # Increased left and right margin (was 0.2)
        top_margin = int(0.8 * height)  # Increased space above the head (was 0.3)

        # Calculate crop coordinates
        crop_x1 = max(x - margin, 0)
        crop_y1 = max(y - top_margin, 0)  # Move the top boundary up
        crop_x2 = min(x + width + margin, img.shape[1])
        crop_y2 = min(y + height + chest_extension, img.shape[0])

        # Crop the image
        cropped_img = img[crop_y1:crop_y2, crop_x1:crop_x2]

        # Get the selected crop size
        crop_size = request.form['crop_size']
        sizes = load_sizes()

        if crop_size in sizes:
            size = sizes[crop_size]
            final_width = get_pixels_from_inches(size['width'])
            final_height = get_pixels_from_inches(size['height'])
        elif crop_size == 'custom':
            custom_width = float(request.form.get('custom_width', 2))
            custom_height = float(request.form.get('custom_height', 2))
            final_width = get_pixels_from_inches(custom_width)
            final_height = get_pixels_from_inches(custom_height)
        else:
            return "Invalid crop size selected", 400

        resized_img = resize_and_crop(cropped_img, final_width, final_height)

        # Save the resized image
        resized_img_path = os.path.join(RESULT_FOLDER, f"resized_{image.filename}")
        cv2.imwrite(resized_img_path, resized_img)

        return render_template('result.html', filename=f"resized_{image.filename}")

    return render_template('upload.html')

@app.route('/print/<filename>/<int:num_copies>')
def print_image(filename, num_copies):
    cropped_img_path = os.path.join(RESULT_FOLDER, filename)
    if not os.path.exists(cropped_img_path):
        return "File not found", 404

    # Load the cropped image
    cropped_img = Image.open(cropped_img_path)
    cropped_width, cropped_height = cropped_img.size

    # Define A4 dimensions in pixels (assuming 300 DPI)
    a4_width, a4_height = 2480, 3508

    # Define margins
    margin = get_pixels_from_inches(0.2)

    # Create an empty A4 canvas
    a4_canvas = Image.new('RGB', (a4_width, a4_height), (255, 255, 255))

    # Place images onto the canvas
    x_offset = margin
    y_offset = margin
    row_height = 0

    for i in range(num_copies):
        # Add a 1px border to the image
        bordered_img = Image.new('RGB', (cropped_width + 2, cropped_height + 2), (0, 0, 0))
        bordered_img.paste(cropped_img, (1, 1))

        if x_offset + bordered_img.width + margin > a4_width:
            x_offset = margin
            y_offset += row_height + margin
            row_height = bordered_img.height

        a4_canvas.paste(bordered_img, (x_offset, y_offset))
        x_offset += bordered_img.width + margin
        row_height = max(row_height, bordered_img.height)

    # Save the final image
    final_image_path = os.path.join(RESULT_FOLDER, f"printable_{filename}")
    a4_canvas.save(final_image_path)

    # Open the print dialog directly
    with open(final_image_path, 'rb') as file:
        response = make_response(file.read())
        response.headers.set('Content-Type', 'application/octet-stream')
        response.headers.set('Content-Disposition', 'attachment', filename=f"printable_{filename}")
        return response

@app.route('/api/crop', methods=['POST'])
def api_crop_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files['image']
    img_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(img_path)

    # Read the image using OpenCV
    img = cv2.imread(img_path)

    # Detect faces
    detections = detector.detect_faces(img)
    if len(detections) == 0:
        return jsonify({"error": "No face detected"}), 400

    # Get the bounding box for the first detected face
    bounding_box = detections[0]['box']
    x, y, width, height = bounding_box

    # Calculate the margin to include some chest area and space above the head
    chest_extension = int(height * 0.5)
    margin = int(0.2 * width)  # Margin around the face
    top_margin = int(0.3 * height)  # Additional space above the head

    # Calculate crop coordinates
    crop_x1 = max(x - margin, 0)
    crop_y1 = max(y - top_margin, 0)  # Move the top boundary up
    crop_x2 = min(x + width + margin, img.shape[1])
    crop_y2 = min(y + height + chest_extension, img.shape[0])

    # Crop the image
    cropped_img = img[crop_y1:crop_y2, crop_x1:crop_x2]

    # Get the selected crop size
    crop_size = request.form.get('crop_size', '2x2')

    # Load sizes from JSON
    sizes_path = './sizes.json'
    if not os.path.exists(sizes_path):
        return jsonify({"error": "Sizes file not found"}), 404

    with open(sizes_path, 'r') as file:
        sizes = json.load(file)

    size_data = sizes.get(crop_size)
    if size_data:
        final_width = get_pixels_from_inches(size_data['width'])
        final_height = get_pixels_from_inches(size_data['height'])
    elif crop_size == 'custom':
        custom_width = float(request.form.get('custom_width', 2))
        custom_height = float(request.form.get('custom_height', 2))
        final_width = get_pixels_from_inches(custom_width)
        final_height = get_pixels_from_inches(custom_height)
    else:
        return jsonify({"error": "Invalid crop size selected"}), 400

    # Resize the cropped image to the desired final dimensions
    resized_img = cv2.resize(cropped_img, (final_width, final_height))

    # Save the resized image
    resized_img_path = os.path.join(RESULT_FOLDER, f"resized_{image.filename}")
    cv2.imwrite(resized_img_path, resized_img)

    # Create the printable image
    num_copies = request.form.get('num_copies', 4)  # Default to 4 copies
    num_copies = int(num_copies)

    # Load the cropped image
    cropped_img = Image.open(resized_img_path)
    cropped_width, cropped_height = cropped_img.size

    # Define A4 dimensions in pixels (assuming 300 DPI)
    a4_width, a4_height = 2480, 3508

    # Define margins
    margin = get_pixels_from_inches(0.2)

    # Create an empty A4 canvas
    a4_canvas = Image.new('RGB', (a4_width, a4_height), (255, 255, 255))

    # Place images onto the canvas
    x_offset = margin
    y_offset = margin
    row_height = 0

    for i in range(num_copies):
        if x_offset + cropped_width + margin > a4_width:
            x_offset = margin
            y_offset += row_height + margin
            row_height = cropped_height

        a4_canvas.paste(cropped_img, (x_offset, y_offset))
        x_offset += cropped_width + margin
        row_height = max(row_height, cropped_height)

    # Save the final printable image
    final_image_path = os.path.join(RESULT_FOLDER, f"printable_{image.filename}")
    a4_canvas.save(final_image_path)

    # Return the printable image as a response
    return send_file(final_image_path, mimetype='image/jpeg')

@app.route('/settings')
def settings():
    return render_template('setting.html')

# Load sizes from a JSON file
def load_sizes():
    try:
        with open('sizes.json', 'r') as f:
            content = f.read().strip()
            if not content:
                return {}  # Return an empty dictionary if file is empty
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



# Save sizes to a JSON file
def save_sizes(sizes):
    with open('sizes.json', 'w') as f:
        json.dump(sizes, f, indent=4)


@app.route('/add_size', methods=['POST'])
def add_size():
    size_name = request.form['size_name']
    width = float(request.form['width'])
    height = float(request.form['height'])

    sizes = load_sizes()
    if isinstance(sizes, list):
        sizes = {}  # Ensure sizes is a dictionary

    sizes[size_name] = {'width': width, 'height': height}
    save_sizes(sizes)

    return redirect('/settings')

@app.route('/api/sizes', methods=['GET'])
def get_sizes():
    sizes_path = './sizes.json'
    if not os.path.exists(sizes_path):
        return jsonify({"error": "Sizes file not found"}), 404

    with open(sizes_path, 'r') as file:
        sizes = json.load(file)

    # Ensure sizes is a dictionary
    if isinstance(sizes, list):
        return jsonify({"error": "Invalid data format"}), 500

    # Convert JSON to a format suitable for the frontend
    formatted_sizes = [{"label": f"{v['width']}x{v['height']} inches", "value": k} for k, v in sizes.items()]

    return jsonify(formatted_sizes)


@app.route('/delete_all_folders', methods=['POST'])
def delete_all_folders():
    # Delete all files in RESULT_FOLDER
    for filename in os.listdir(RESULT_FOLDER):
        file_path = os.path.join(RESULT_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            return f"An error occurred while deleting files in results: {str(e)}", 500

    # Delete all files in UPLOAD_FOLDER
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            return f"An error occurred while deleting files in uploads: {str(e)}", 500

    return "All files in upload and result folders deleted successfully", 200




@app.route('/download/<filename>')
def download_file(filename):
    cropped_img_path = os.path.join(RESULT_FOLDER, filename)
    if not os.path.exists(cropped_img_path):
        return "File not found", 404
    return send_from_directory(RESULT_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True)
