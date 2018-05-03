import PyPDF2
import re
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
import json
from IPython import embed

#Set root directory name where the documents are present
rootdir = 'emtex payments'
files = None
root = None

for root, dirs, files in os.walk(rootdir):
    files = files
    root = root
    break
print files

ext = ['pdf']
data = []
for file in files:

    current_file = {}

    #Setting path of file with root dir
    file_name = "{}/{}".format(root, file)
    print "\n\n\n",file_name

    # creating a pdf file object
    pdfFileObj = open(file_name, 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pageObj = pdfReader.getPage(0)
    #Get plain text from PDF as a string
    text = pageObj.extractText()

    #Removing uneccessary punctuations and blanks to make extraction easier
    sanitized_text =  " ".join(text.split(":"))
    sanitized_text =  " ".join(sanitized_text.split("_"))
    text =  " ".join(sanitized_text.split())

    #Split text by spaces
    words = text.split(" ")
    index = 0

    #Extracting the required data (logic may vary from this point onward)
    total_amount = ""
    invoice_no_1 = ""
    invoice_no_2 = ""
    date_1 = ""
    date_2 = ""
    ref = ""

    print words
    for word in words:
        if word == ".":
            if words.index("."):
                i = words.index(".")
                del words[i]

    for word in words:
        index = index + 1
        if word == "vide":
            ref = words[index+2]
        if word == "videUTR":
            ref = words[index+1]
        if word =="Rs":
            word = words[index]
            word_r = re.split("\(", word)
            total_amount = word_r[0]
        if word == "Security/Retention":
            invoice_no_1 = words[index]
            print invoice_no_1
            date_1 = words[index+1]
            print date_1
        if word == "Ref/Remarks":
            if '007' in words[index]:
                invoice_no_2 = words[index]
                print invoice_no_2
                date_2 = words[index + 1]
                print date_2
            if 'SBW' in  words[index]:
                invoice_no_2 = words[index]
                print invoice_no_2
                date_2 = words[index + 1]
                print date_2
            if '007' in  words[index+1]:
                invoice_no_2 = words[index+1]
                print invoice_no_2
                date_2 = words[index + 2]
                print date_2
            if 'SBW' in  words[index+1]:
                invoice_no_2 = words[index+1]
                print invoice_no_2
                date_2 = words[index + 2]
                print date_2
            if '007' in  words[index+2]:
                invoice_no_2 = words[index+2]
                print invoice_no_2
                date_2 = words[index + 3]
                print date_2
            if 'SBW' in  words[index+2]:
                invoice_no_2 = words[index+2]
                print invoice_no_2
                date_2 = words[index + 3]
                print date_2

    #Add data to JSON
    current_file = {
        "File Name": file,
        "Ref No": ref,
        'Total Amount': total_amount,
        'Invoice Number_1': invoice_no_1,
        'Invoice Number_2': invoice_no_2,
        'Date_2': date_2,
        'Date_1' : date_1
    }

    data.append(current_file)

# Writing in JSON file
with open('emtex_payments.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
               