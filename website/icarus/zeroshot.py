from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image

from ..tools import image_tools

# CLIP https://arxiv.org/abs/2103.00020 
# Zeroshot models
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")

def zeroshot_compute(image: Image, labels: list[str]) -> (str, dict, str):
    """
    Zeroshot classification

    Input: image and the labels we want to classify.
    Output: the predicted label, the probability distribution, and the encoded image.
    """
    encoded_image = image_tools.encode_image_to_base64(image)
    
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

    return (label, label_props, encoded_image)