from PIL import Image
from flask import Flask, request, render_template, send_from_directory, send_file, make_response
from mtcnn import MTCNN
import cv2
import numpy as np
import os

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
        crop_size = request.form['crop_size']

        if crop_size == '2x2':
            final_width = get_pixels_from_inches(2)
            final_height = get_pixels_from_inches(2)
        elif crop_size == '0.8x0.8':
            final_width = get_pixels_from_inches(0.8)
            final_height = get_pixels_from_inches(0.8)
        elif crop_size == 'custom':
            custom_width = float(request.form.get('custom_width', 2))
            custom_height = float(request.form.get('custom_height', 2))
            final_width = get_pixels_from_inches(custom_width)
            final_height = get_pixels_from_inches(custom_height)
        else:
            return "Invalid crop size selected", 400

        # Resize the cropped image to the desired final dimensions
        resized_img = cv2.resize(cropped_img, (final_width, final_height))

        # Save the resized image
        resized_img_path = os.path.join(RESULT_FOLDER, f"resized_{image.filename}")
        cv2.imwrite(resized_img_path, resized_img)

        return render_template('result.html', filename=f"resized_{image.filename}")

    return render_template('upload.html')


from PIL import Image
import os

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
        if x_offset + cropped_width + margin > a4_width:
            x_offset = margin
            y_offset += row_height + margin
            row_height = cropped_height

        a4_canvas.paste(cropped_img, (x_offset, y_offset))
        x_offset += cropped_width + margin
        row_height = max(row_height, cropped_height)

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

    if crop_size == '2x2':
        final_width = get_pixels_from_inches(2)
        final_height = get_pixels_from_inches(2)
    elif crop_size == '0.8x0.8':
        final_width = get_pixels_from_inches(0.8)
        final_height = get_pixels_from_inches(0.8)
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
