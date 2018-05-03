#CODE TO EXTRACT NAME, ADDRESS, GENDER, BIRTH YEAR AND AADHAR NUMBER FROM AADHAR CARD

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

#Name of file of aadhar card to extract data from
filename = "aadhar.png"

def preprocess(path):
    ext = os.path.splitext(filename)[1]
    base = os.path.splitext(filename)[0]

    # Load source / input image as grayscale, also works on color images...
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

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

    # Save preprocessed image
    cv2.imwrite(base + '_pre' + ext, img)

    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        base + '_pre' + ext)

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

def get_text(path):
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.text_detection(image=image)
    print response
    serialized = json.loads(MessageToJson(response))

    items = serialized["textAnnotations"]
    block_items = serialized["fullTextAnnotation"]

    print items


    with open('aadhaar_data.json', 'w') as outfile:
        json.dump(block_items, outfile, indent=4)

    #print block_items

    count = 0
    flag = 0
    for item in items:
        count = count + 1

        if items[0]["description"] == "INDIA" or items[1]["description"] == "India" or items[2]["description"] == "India":
            c = count
            flag = 1

        #Extract birth year
        if re.search('(Year|Birth|irth|YoB|YOB:|DOB:|DOB)$', item["description"]):
            birthyear =  items[count+1]["description"]

            #Extract gender
            if re.search('(Female|female|FEMALE|emale)$', items[count+2]["description"]):
                gen = "Female"
                anum = items[count+4]["description"] + " " + items[count+5]["description"] + " " + items[count+6]["description"]
            if re.search('(Male|male|ale)$', items[count+2]["description"]):
                gen = "Male"
                anum = items[count+4]["description"] + " " + items[count+5]["description"] + " " + items[count+6]["description"]
            if re.search('(Female|female|FEMALE|emale)$', items[count+3]["description"]):
                gen = "Female"
                anum = items[count+4]["description"] + " " + items[count+5]["description"] + " " + items[count+6]["description"]
            else:
                gen = "Male"
                anum =  items[count+4]["description"] + " " + items[count+5]["description"] + " " + items[count+6]["description"]

    #extract name
    if flag == 1:
        name = items[c]["description"] + " " + items[c+1]["description"]

    else:
         name = items[1]["description"] + " " + items[2]["description"]

    #Extract address
    ind = 0
    for item in items:
        ind = ind + 1
        if item["description"] == "Address":
            i1 = item["boundingPoly"]
            i2 = i1["vertices"][0]
            i3 = i2['x']
            break

    add = []
    for i in items:
        i1 = items[ind]["boundingPoly"]
        i2 = i1["vertices"][0]
        xcoord = i2['x']
        if (xcoord >= i3 - 5):
            add.append(items[ind]["description"])
        if re.match(r'(\d{6})', items[ind]["description"]):
            break
        ind = ind + 1

    addr = ' '.join(add)

    data = ({
        'Name': name,
        'Birth Year': birthyear,
        'Gender': gen,
        'Aadhaar Card Number': anum,
        'Address': addr
    })

    # Writing in JSON file
    with open('aadhaar_data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

preprocess(filename)
get_text(filename)




