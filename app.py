from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import cv2 
import os
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client.image_processing_db
images_collection = db.images

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"The operation is {operation} and filename is {filename}")
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = cv2.imread(img_path)
    
    if img is None:
        flash("Error reading the image file.")
        return None

    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename.split('.')[0]}_gray.jpg"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "cwebp":
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cjpg":
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cpng":
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cblur":
            imgProcessed = cv2.blur(img, (10, 10))
            newFilename = f"static/{filename.split('.')[0]}_blur.jpg"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "cthreshold":
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, imgProcessed = cv2.threshold(gray_img, 120, 255, cv2.THRESH_BINARY)
            newFilename = f"static/{filename.split('.')[0]}_threshold.jpg"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "cresize":
            imgProcessed = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))
            newFilename = f"static/{filename.split('.')[0]}_resized.jpg"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "":
            flash("Invalid operation")
            return None
        case "csmoothing":
            kernel = np.ones((5, 5), np.float32) / 25  # Define the kernel
            imgProcessed = cv2.filter2D(img, -1, kernel)
            newFilename  = f"static/{filename.split('.')[0]}_smoothing.jpg"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
            


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
       
        if 'file' not in request.files:
            flash('No file part')
            return render_template("index.html")
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return render_template("index.html")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_filename = processImage(filename, operation)
            if new_filename:
                # Save metadata to MongoDB
                image_data = {
                    "original_filename": filename,
                    "processed_filename": new_filename,
                    "operation": operation
                }
                images_collection.insert_one(image_data)
                flash(f"Your image has been processed and is available <a href='/{new_filename}' target='_blank'>here</a>")
            else:
                flash("Error processing the image.")
            return render_template("index.html")

    return render_template("index.html")

@app.route("/images")
def list_images():
    images = images_collection.find()
    return render_template("images.html", images=images)

@app.route("/images/<image_id>")
def view_image(image_id):
    image = images_collection.find_one({"_id": ObjectId(image_id)})
    if image:
        return render_template("view_image.html", image=image)
    else:
        flash("Image not found")
        return redirect(url_for("list_images"))

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True, port=5001)


