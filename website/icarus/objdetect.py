from flask import current_app
from os import path
import torch
from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image, ImageDraw, ImageFont

from .. import AppConst

# DETR https://arxiv.org/abs/2005.12872 
detr_model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
detr_processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
objdetect_container_path = "/objdetect"
colors = [(50, 205, 50), (255, 215, 0), (64, 224, 208), (250, 128, 14), (255, 218, 185), (135, 206, 250), (186, 85, 211)]

def objdetect_compute(image: Image) -> (str, list):
    """
    Object Detection.

    Input: image for Object Detection.
    Output: processed image path and processed data (including bounding boxes, scores & labels).
    """

    # Process the image with DETR
    inputs = detr_processor(images=image, return_tensors="pt")
    outputs = detr_model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = detr_processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

    # Create a drawing object to add bounding boxes & text labels to the image
    draw = ImageDraw.Draw(image)
    result_data = []

    color_index = 0
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        x0, y0, x1, y1 = box.tolist()
        label_name = detr_model.config.id2label[label.item()]
        color = colors[color_index % len(colors)]
        score = round(score.item(), 2)
        text = f"{label_name} ({score})"

        result_data.append({"text": text, "color": color})
        draw.rectangle([x0, y0, x1, y1], outline=color, width=4)
        draw.text((x0, y0 - 10), text, fill=color, font=None, encoding="utf-8")
        color_index += 1

    container_path = current_app.config[AppConst.CONFIG_STORAGE_PATH] + objdetect_container_path
    result_image_path = path.join(container_path, 'objdetect_result.jpg')
    image.save(result_image_path)

    return (result_image_path, result_data)