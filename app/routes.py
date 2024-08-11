from flask import Blueprint, request, render_template, redirect, send_file, jsonify
import os
import cv2
from PIL import Image
from .utils import get_pixels_from_inches, resize_and_crop, load_sizes, save_sizes
from . import detector

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
@main.route('/', methods=['GET', 'POST'])
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

@main.route('/settings')
def settings():
    return render_template('setting.html')

@main.route('/add_size', methods=['POST'])
def add_size():
    size_name = request.form['size_name']
    width = float(request.form['width'])
    height = float(request.form['height'])

    sizes = load_sizes()
    if isinstance(sizes, list):
        sizes = {}

    sizes[size_name] = {'width': width, 'height': height}
    save_sizes(sizes)

    return redirect('/settings')
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


