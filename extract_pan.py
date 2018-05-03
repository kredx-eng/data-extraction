#CODE TO EXTRACT PAN NUMBER, NAME, FATHER'S NAME AND BIRTHDATE FROM PAN CARD

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
import datetime

# Set path to google credentials file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-application-credentials.json"

#Path of Image of cheque
imge = ("pancard.jpg")
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
    serialized = json.loads(MessageToJson(response))

    items = serialized["textAnnotations"]
    #check whther PAN is of new format or old format
    for item in items:
        if item["description"] == "Name" or item["description"] == "Father's Name" or item["description"] == "Date of Birth":
            option = 1
        else:
            option = 2
    #New format extract data
    if option == 1:
        index = 0
        for item in items:
            index = index + 1
            if item["description"] == "Permanent Account Number card":
                pnum =  items[index]["description"]
            if item["description"] == "Name":
                name = items[index]["description"]
            if item["description"] == "Father's Name":
                f_name = items[index]["description"]
            if item["description"] == "Date of Birth":
                bday = items[index]["description"]

    #Old format extract data
    if option == 2:
        index = 0

        #Extract PAN Number
        for item in items:
            index = index + 1
            if item["description"] == "Permanent":
                if items[index]["description"] == "Account":
                    if items[index + 1]["description"] == "Number":
                        pnum = items[index + 2]["description"]
        #Extract name
        index = 0
        for item in items:
            index = index + 1
            if item['description'] == "INDIA":
                i1 = items[index]["boundingPoly"]
                i2 = i1["vertices"][0]
                i3 = i2['y']
                y_name = i3
                break

        count = 0
        count1 = 0
        name = []
        for item in items:
            i1 = item["boundingPoly"]
            i2 = i1["vertices"][0]
            i3 = i2['y']
            count = count + 1
            if(i3 >= y_name-5 and i3 <= y_name+5):
                name.append(item["description"])
                count1 = count1 + 1
                word = items[count]["description"]
                if re.match(r'[\w-]*$', word):
                    choice = 1
                else:
                    choice = 0
        name = ' '.join(name)
        count2 = index + count1 + 1

        if (choice == 0):
             bday = items[count2]["description"]
        else:
            i1 = items[count2]["boundingPoly"]
            i2 = i1["vertices"][0]
            i3 = i2['y']
            y_fname = i3

        count3 = 0
        fname = []
        #Extract father's name
        for item in items:
            i1 = item["boundingPoly"]
            i2 = i1["vertices"][0]
            i3 = i2['y']
            if (i3 >= y_fname - 5 and i3 <= y_fname + 5):
                fname.append(item["description"])
                count3 = count3 + 1

        f_name = ' '.join(fname)
        #Extract birthdate
        for item in items:
            if re.match(r'[\d+/\d+/\d+]', item["description"]):
                bday = item["description"]

    #Store data as JSON
    data = ({
        'Name': name,
        'Birth Date': bday,
        'Father\'s Name': f_name,
        'PAN Number': pnum
    })

    # Writing in JSON file
    with open('pan_data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)


detect_text(file_name)



