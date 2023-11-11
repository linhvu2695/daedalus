from flask import current_app
from os import path
import pytesseract
from PIL import Image, ImageDraw

from .. import AppConst

# OCR storage folder
OCR_CONTAINER_PATH = "/icarus/ocr"

def ocr_compute(image: Image) -> (str, str):
    """
    Optical Character Recognition

    Input: image for OCR.
    Output: processed image path and text retrieved from the image.
    """

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

    container_path = current_app.config[AppConst.CONFIG_STORAGE_PATH] + OCR_CONTAINER_PATH
    result_image_path = path.join(container_path, 'ocr_result.jpg')
    image.save(result_image_path)

    return (result_image_path, text_to_render)