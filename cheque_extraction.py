import json
import io
import os
import cv2
import numpy as np
import base64
from IPython import embed
import re
from google.protobuf.json_format import MessageToJson
from google.cloud import vision
from google.cloud.vision import types

# Set path to google credentials file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-application-credentials.json"

#Path of Image of cheque
imge = ("ch.jpg")
ext = os.path.splitext(imge)[1]
base = os.path.splitext(imge)[0]

# Load source / input image as grayscale, also works on color images...
img = cv2.imread(imge, cv2.IMREAD_GRAYSCALE)

height, width = img.shape[:2]
max_height = 1000
max_width = 1000

# only shrink if img is bigger than required
if max_height < height or max_width < width:
    # get scaling factor
    scaling_factor = max_height / float(height)
    if max_width / float(width) < scaling_factor:
        scaling_factor = max_width / float(width)
    # resize image
    img = cv2.resize(img, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

kernel = np.zeros((9, 9), np.float32)
kernel[4, 4] = 2.0  # Identity, times two!

# Create a box filter:
boxFilter = np.ones((9, 9), np.float32) / 81.0

# Subtract the two:
kernel = kernel - boxFilter

img = cv2.filter2D(img, -1, kernel)

#Save preprocessed image
cv2.imwrite(base + '_pre' + ext, img)

# The name of the image file to annotate
file_name = os.path.join(
    os.path.dirname(__file__),
    base + '_pre' + ext)

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.text_detection(image=image)
    #labels = response.text_annotations
    serialized = json.loads(MessageToJson(response))
    #print serialized
    # embed()

    items = serialized["textAnnotations"]

    def getletter(variable, letternumber):
        return str(variable)[letternumber - 1]

    # Read IFSC Code
    iter_items = iter(items)
    next(iter_items)
    index = 0
    for item in items:
        index = index + 1
        # if len(item["description"]) >= 3:
        #     #print item["description"]
        #     if "IFS" or "FSC" in item["description"]:
        #         nine_words = index + 9 if index + 9 <= len(items) else len(items)
        #         for next_item in items[index:nine_words]:
        #             word = next_item["description"]
        #             if len(word) == 11:
        #                 got = getletter(word, 5)
        #                 if got == '0':
        #                     print "IFSC Code: " + word

        if re.match(r'^[A-Z]{4}[0-9]{7}$', item["description"]):
            print "IFSC Code: " + item["description"]
    # Read Account Number
    index = 0
    for item in items:
        index = index + 1
        if item["description"] == "No.":
            print "Account Number: " + items[index]["description"]
        if item["description"] == "NO.":
            print "Account Number: " + items[index]["description"]
        if item["description"] == "NO":
            print "Account Number: " + items[index]["description"]
        if item["description"] == "No":
            print "Account Number: " + items[index]["description"]


detect_text(file_name)



