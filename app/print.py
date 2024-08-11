from flask import Blueprint, send_file
from PIL import Image
import os
from .utils import get_pixels_from_inches

print_blueprint = Blueprint('print', __name__)

@print_blueprint.route('/print/<filename>/<int:num_copies>')
def print_image(filename, num_copies):
    cropped_img_path = os.path.join('results', filename)
    if not os.path.exists(cropped_img_path):
        return "File not found", 404

    cropped_img = Image.open(cropped_img_path)
    cropped_width, cropped_height = cropped_img.size

    # Define A4 dimensions in pixels (assuming 300 DPI)
    a4_width, a4_height = 2480, 3508
    margin = get_pixels_from_inches(0.2)

    # Create an empty A4 canvas
    a4_canvas = Image.new('RGB', (a4_width, a4_height), (255, 255, 255))

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
    final_image_path = os.path.join('results', f"printable_{filename}")
    a4_canvas.save(final_image_path)

    # Return the printable image as a response
    return send_file(final_image_path, mimetype='image/jpeg')
