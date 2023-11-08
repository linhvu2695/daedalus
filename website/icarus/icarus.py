from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from os import path

import torch
from PIL import Image, ImageDraw

from .. import db, AppConst
from .zeroshot import zeroshot_compute
from .ocr import ocr_compute
from .objdetect import objdetect_compute
from .diffusion import diffusion_compute
from .captioning import captioning_compute

icarus = Blueprint("icarus", __name__)

# Main page

@icarus.route("/icarus/ZeroShot")
@login_required
def zeroshot_explore():
    return render_template("icarus/zeroshot/zeroshot.html", user=current_user)

@icarus.route("/icarus/OCR")
@login_required
def ocr_explore():
    return render_template("icarus/ocr/ocr.html", user=current_user)

@icarus.route("/icarus/ObjDetect")
@login_required
def objdetect_explore():
    return render_template("icarus/objdetect/objdetect.html", user=current_user)

@icarus.route("/icarus/Diffusion")
@login_required
def diffusion_explore():
    return render_template("icarus/diffusion/diffusion.html", user=current_user)

@icarus.route("/icarus/Captioning")
@login_required
def captioning_explore():
    return render_template("icarus/captioning/captioning.html", user=current_user)

# AJAX generation

@icarus.route("/icarus/ZeroShot/generate", methods=["POST"])
@login_required
def zeroshot_generate():
    image = Image.open(request.files['image']).convert("RGB")
    labels = [label.strip() for label in request.form['text'].split(',')]
    
    label, label_props, encoded_image = zeroshot_compute(image, labels)

    return render_template('icarus/zeroshot/zeroshot_gen.html', label=label, user=current_user, image=encoded_image, label_props=label_props)

@icarus.route("/icarus/OCR/generate", methods=["POST"])
@login_required
def ocr_generate():
    image = Image.open(request.files['image']).convert("RGB")

    result_image_path, text_to_render = ocr_compute(image)

    return render_template('icarus/ocr/ocr_gen.html', user=current_user, 
                           result_image_path=result_image_path, text_to_render=text_to_render)

@icarus.route("/icarus/ObjDetect/generate", methods=["POST"])
@login_required
def objdetect_generate():
    image = Image.open(request.files['image']).convert("RGB")

    result_image_path, result_data = objdetect_compute(image)

    return render_template('icarus/objdetect/objdetect_gen.html', user=current_user, 
                           result_image_path=result_image_path, result_data=result_data)

@icarus.route("/icarus/Diffusion/generate", methods=["POST"])
@login_required
def diffusion_generate():
    image_desc = request.form['text']

    result_image_path = diffusion_compute(image_desc)

    return render_template('icarus/diffusion/diffusion_gen.html', user=current_user, 
                           result_image_path=result_image_path)

@icarus.route("/icarus/Captioning/generate", methods=["POST"])
@login_required
def captioning_generate():
    image = Image.open(request.files['image']).convert("RGB")

    result_caption = captioning_compute(image)

    print(result_caption)
    return render_template('icarus/captioning/captioning_gen.html', user=current_user, 
                           text_to_render=result_caption)