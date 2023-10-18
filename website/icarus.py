from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
import base64, io
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from . import db, AppConst

icarus = Blueprint("icarus", __name__)

api_key = "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"

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")

@icarus.route("/icarus")
@login_required
def icarus_explore():
    return render_template("icarus.html", user=current_user)

@icarus.route("/icarus/generate", methods=["POST"])
@login_required
def generate():
    if 'image' not in request.files:
        return render_template('index.html', error='No image provided.')

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

    return render_template('icarus.html', label=label, user=current_user, image=encoded_image, label_props=label_props)