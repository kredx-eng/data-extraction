from selenium import webdriver
from bs4 import BeautifulSoup
import base64
import io
from PIL import Image
import pytesseract
import requests
from time import sleep
import re
import json

#Setting path of phantomjs in computer
driver = webdriver.PhantomJS("/usr/local/bin/phantomjs")
driver.set_window_size(1920,1080)

try:
    driver.get('http://112.133.194.253/reprintletter/membercard.aspx')
except Exception,e:
    driver.save_screenshot('screenshot.png')

#Reading and extracting captcha
html = driver.page_source
soup = BeautifulSoup(html)
img = soup.find("img", {"id": "imgCaptcha"})["src"]
img = base64.b64decode(img.split("base64,")[1])
img = Image.open(io.BytesIO(img))
text = pytesseract.image_to_string(img).replace("\n", "").replace("\t", "").replace(" ", "")

#Finding values of hidden elements in form
vie = soup.find("input", {"name" : "__VIEWSTATE"}, type="hidden")["value"]
valid = soup.find("input", {"name" : "__EVENTVALIDATION"}, type="hidden")["value"]

#Filling the login form and submitting
def logins():
    mrn = driver.find_element_by_css_selector('#txtMRN')
    mrn.send_keys('137819')
    day = driver.find_element_by_css_selector('#txtDay')
    day.send_keys('21')
    month = driver.find_element_by_css_selector('#txtMonth')
    month.send_keys('08')
    year = driver.find_element_by_css_selector('#txtYear')
    year.send_keys('1987')
    year = driver.find_element_by_css_selector('#txtCap')
    year.send_keys(text)

    targ = driver.find_element_by_name("__EVENTTARGET")
    driver.execute_script('arguments[0].value = arguments[1]', targ, '')
    arg = driver.find_element_by_name("__EVENTARGUMENT")
    driver.execute_script('arguments[0].value = arguments[1]', arg, '')
    val = driver.find_element_by_name("__EVENTVALIDATION")
    driver.execute_script('arguments[0].value = arguments[1]', val, valid )
    stat = driver.find_element_by_name("__VIEWSTATE")
    driver.execute_script('arguments[0].value = arguments[1]', stat, vie)

    login = driver.find_element_by_css_selector('#btnSubmit')
    login.click()

logins()

#Fetchiing the new page html source
new_html = driver.page_source
soup = BeautifulSoup(new_html)

#finding the columns that need to data to be extracted from
table = soup.find_all("table")[0]
table_body = table.findAll('td')

table1 = soup.find_all("table")[1]
table1_body = table1.findAll('td')

#extracting data according as per requirement
t1 = re.split(r'Sex:' , table_body[1].text)
t7 = re.split(r':', t1[0])
t8 = re.split(r':', table_body[6].text)
t9 = re.split(r':', table_body[8].text)
t10 = re.split(r':', table_body[11].text)
t11 = re.split(r':',table_body[13].text)
t12 = re.split(r':', table_body[15].text)
t14 = re.split(r':', table_body[20].text)
t5 = re.split(r':' , table1_body[10].text)
t2 = re.split(r'Mobile No.:' , table1_body[11].text)
t3 = re.split(r'Email :' , t2[1])
t5 = re.split(r':' , table1_body[12].text)
t4 = re.split(r'Mobile No.:' , table1_body[13].text)
t6 = re.split(r'Holding COP', table1_body[1].text)

str1 = t7[1].replace(u"\u00A0", " ")
str2 = t1[1].replace(u"\u00A0", " ")
str3 = t8[1].replace(u"\u00A0", " ")
str4 = table_body[18].text.replace(u"\u00A0", " ")
str5 = t3[0].replace(u"\n", "")
str6 = t3[1].replace(u"\n", "")
str7  = t4[1].replace(u"\n", "")

data = ({
    'MRN': str1,
    'Sex': str2,
    'NAME': str3,
    'DOB': t9[1],
    'QUALIFICATION': t10[1],
    'ENROLLMENT DATE' : t11[1],
    'A/F' : t12[1],
    'COP DATE' : str4,
    'FATHER\'S NAME' : t14[1],
    'Holding COP' : t6[1],
    'Prof addr' : t5[1],
    'Mobile No.' : str5,
    'Email' : str6,
    'Res addr' : t5[1],
    'Res Mobile No.' : str7
})

#Writing in JSON file
with open('data.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)




































