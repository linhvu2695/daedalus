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
ocr_container_path = "/ocr"

@icarus.route("/icarus/ZeroShot")
@login_required
def zeroshot_explore():
    return render_template("icarus/zeroshot.html", user=current_user)

@icarus.route("/icarus/OCR")
@login_required
def ocr_explore():
    return render_template("icarus/ocr.html", user=current_user)

@icarus.route("/icarus/ZeroShot/generate", methods=["POST"])
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
    print(str(data))

    # Create a drawing object to add bounding boxes & text labels to the image
    draw = ImageDraw.Draw(image)
    text_data = {} # text data is structured in 4 levels of block - paragraph - line - word
    text_to_render = [] # block - paragraph

    for i in range(len(data['text'])):
        block_num   = int(data['block_num'][i])
        par_num     = int(data['par_num'][i])
        line_num    = int(data['line_num'][i])
        word_num    = int(data['word_num'][i])
        word        = str(data['text'][i])
        conf        = int(data['conf'][i])
        x, y, w, h = int(data['left'][i]), int(data['top'][i]), int(data['width'][i]), int(data['height'][i])

        draw.rectangle([x, y, x + w, y + h], outline=(0, 255, 0), width=2)

        if conf > 90 and len(word) > 0 and not word.isspace():
            label = f"{word} ({conf})"
            draw.text((x, y - 10), label, fill=(0, 255, 0), font=None, size=16, encoding="utf-8")

            if not (block_num in text_data.keys()):
                text_data[block_num] = {}
            if not (par_num in text_data[block_num].keys()):
                text_data[block_num][par_num] = {}
            if not (line_num in text_data[block_num][par_num].keys()):
                text_data[block_num][par_num][line_num] = ""
            text_data[block_num][par_num][line_num] += (" " + word)

    print(text_data)
    for block in sorted(text_data.keys()):
        for par in sorted(text_data[block].keys()):
            text_to_render.append("")
            for line in sorted(text_data[block][par].keys()):
                text_to_render[-1] += (text_data[block][par][line] + "\n")
    print(text_to_render)

    container_path = current_app.config[AppConst.CONFIG_STORAGE_PATH] + ocr_container_path
    result_image_path = path.join(container_path, 'ocr_result.jpg')
    image.save(result_image_path)
    

    return render_template('icarus/ocr.html', user=current_user, 
                           result_image_path=result_image_path, text_to_render=text_to_render)