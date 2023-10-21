from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
import base64, io
from os import path
import torch
from transformers import CLIPProcessor, CLIPModel
import pytesseract
from PIL import Image, ImageDraw
from . import db, AppConst

icarus = Blueprint("icarus", __name__)

# CLIP https://arxiv.org/abs/2103.00020 
# Zeroshot models
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")

@icarus.route("/icarus/ZeroShotClassification")
@login_required
def zeroshot_explore():
    return render_template("icarus/zeroshot.html", user=current_user)

@icarus.route("/icarus/OCR")
@login_required
def ocr_explore():
    return render_template("icarus/ocr.html", user=current_user)

@icarus.route("/icarus/ZeroShotClassification/generate", methods=["POST"])
@login_required
def zeroshot_generate():
    if 'image' not in request.files:
        return render_template('icarus/zeroshot.html', error='No image provided.')

    # Get the uploaded image
    image = Image.open(request.files['image']).convert("RGB")
    labels = [label.strip() for label in request.form['labels'].split(',')]

    # Get the image encoded in base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    # Process the image with CLIP
    inputs = processor(text=labels, images=image, return_tensors="pt", padding=True)
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image # this is the image-text similarity score
    probs = logits_per_image.softmax(dim=1) # softmax to get the label probabilities

    # Get the probabilities of each label
    label_props = {label: prob for label, prob in zip(labels, [tensor.item() for tensor in probs[0]])}
    print(f"Probs: {label_props}")

    label_id = torch.argmax(probs)
    label = labels[label_id] # the label with the highest probability is our prediction

    return render_template('icarus/zeroshot.html', label=label, user=current_user, image=encoded_image, label_props=label_props)

@icarus.route("/icarus/OCR/generate", methods=["POST"])
@login_required
def ocr_generate():
    if 'image' not in request.files:
        return render_template('icarus/ocr.html', error='No image provided.')
    
    # Get the uploaded image
    image = Image.open(request.files['image']).convert("RGB")

    # Perform OCR on the uploaded image
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    print(data)

    # Create a drawing object to add bounding boxes to the image
    draw = ImageDraw.Draw(image)

    for i in range(len(data['text'])):
        word = data['text'][i]
        conf = int(data['conf'][i])
        x, y, w, h = int(data['left'][i]), int(data['top'][i]), int(data['width'][i]), int(data['height'][i])

        # Draw a rectangle around each word
        draw.rectangle([x, y, x + w, y + h], outline="green", width=2)

    container_path = current_app.config[AppConst.CONFIG_STORAGE_PATH]
    image.save(path.join(container_path, 'test_ocr.jpg'))
    

    return render_template('icarus/ocr.html', user=current_user)