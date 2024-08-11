
# Image Cropper Tool

This project is a powerful image cropping tool built using Flask. It allows users to upload an image, select predefined crop sizes, zoom in/out, and crop the image based on the selected area. The cropped image can be saved, printed, and downloaded.

## Table of Contents

-   [Features](#features)
-   [Installation](#installation)
-   [Usage](#usage)
-   [How It Works](#how-it-works)
-   [API Endpoints](#api-endpoints)
-   [File Structure](#file-structure)
-   [Technologies Used](#technologies-used)
-   [License](#license)

## Features

-   Upload and crop images with predefined or custom sizes.
-   Zoom in/out and move the cropping area with buttons.
-   Automatically detect faces and crop the image based on face detection.
-   Option to manually crop images if face detection fails.
-   Save, download, and print the cropped images.
-   Manage crop sizes with a settings page.
-   Delete all uploaded and result files with a single click.

## Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**
    
   
    
    
    
    `git clone https://github.com/yourusername/image-cropper-tool.git
    cd image-cropper-tool` 
    
2.  **Create a virtual environment and install dependencies:**
    
   
    
  
    
    ``python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt`` 
    
3.  **Run the Flask application:**
    

    
    
    `flask run` 
    
    The application will start at `http://127.0.0.1:5000`.
    

## Usage

1.  **Upload an Image:**
    
    -   Go to the homepage and upload an image.
2.  **Select Crop Size:**
    
    -   Choose a predefined size or select "Custom" to enter your own dimensions.
3.  **Zoom and Move:**
    
    -   Use the Zoom In/Out buttons to adjust the view and drag the crop box to the desired position.
4.  **Crop the Image:**
    
    -   Click "Crop" to crop the image based on your selections.
5.  **Download or Print:**
    
    -   Download the cropped image or print multiple copies on an A4-sized canvas.

## How It Works

-   **Face Detection:**
    -   The tool uses MTCNN (Multi-task Cascaded Convolutional Networks) to detect faces in the uploaded image. If a face is detected, the crop area is adjusted to include the face and some surrounding context.
-   **Custom Crop Sizes:**
    -   Users can add custom crop sizes via the settings page, which are saved in a `sizes.json` file.
-   **Zooming and Cropping:**
    -   The tool allows users to zoom in and out and move the crop box to get the desired crop. The crop box is resized and positioned according to the selected crop size.

## API Endpoints

-   **`POST /api/crop`**: Crop an image based on the provided crop size and return the cropped image.
-   **`GET /api/sizes`**: Get the list of available crop sizes.
-   **`POST /add_size`**: Add a new crop size.
-   **`POST /delete_all_folders`**: Delete all files in the upload and result folders.









## Technologies Used

-   **Python & Flask:** Backend development.
-   **HTML/CSS/JavaScript:** Frontend development.
-   **OpenCV & MTCNN:** Image processing and face detection.
-   **Pillow:** Image handling and manipulation.

## License

This project is licensed under the MIT License.