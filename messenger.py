#!/usr/bin/python3

import time
import os
import json
import urllib
import re

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import pyotp
import fbchat
fbchat._util.USER_AGENTS    = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"]
fbchat._state.FB_DTSG_REGEX = re.compile(r'"name":"fb_dtsg","value":"(.*?)"')

from dotenv import load_dotenv
load_dotenv()

FB_EMAIL = os.getenv('FB_EMAIL')
FB_PASSWORD = os.getenv('FB_PASSWORD')
FB_OTP = os.getenv('FB_OTP')

RAINDROP_TOKEN = os.getenv('RAINDROP_TOKEN')

option = Options()

option.add_argument("--disable-infobars")
option.add_argument("--disable-extensions")

# Pass the argument 1 to allow and 2 to block
option.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 1 
})

driver = webdriver.Chrome(chrome_options=option)
driver.get('https://www.facebook.com')

email_elem = driver.find_element_by_id('email')
email_elem.send_keys(FB_EMAIL)

email_elem = driver.find_element_by_id('pass')
email_elem.send_keys(FB_PASSWORD)
email_elem.send_keys(Keys.ENTER)

# get OTP
otp_elem = driver.find_element_by_id('approvals_code')
totp = pyotp.TOTP(FB_OTP)
otp_elem.send_keys(totp.now())
otp_elem.send_keys(Keys.ENTER)

# save browser prompt
driver.find_element_by_xpath("//input[@value='dont_save']").click()
driver.find_element_by_id('checkpointSubmitButton').click()

# pinned post link
# i'm assuming we'll also have separate links for each group but can also be one post for all
driver.get('https://www.facebook.com/groups/csesoc/permalink/10157037534857191/')

to_add = []

# dirty hack to get page to load
time.sleep(5)

# load _all_ comments
# for "view more comments" before comments
while True:
    try:
        more_comments_elem = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[5]/div/div/div[2]/div[2]/div/div[2]/span/span[contains(text(), 'comments')]")
        more_comments_elem.click()
        # again, wait for comments to load. 
        time.sleep(5)
    except NoSuchElementException:
        break

# for "view more comments" after comments
while True:
    try:
        more_comments_elem = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[5]/div/div/div[2]/div[3]/div/div[2]/span/span[contains(text(), 'comments')]")
        more_comments_elem.click()
        # again, wait for comments to load. 
        time.sleep(5)
    except NoSuchElementException:
        break

# get top level comments
i = 1
while True:
    try:
        comment_elem = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[5]/div/div/div[2]/ul/li[{}]/div[1]/div/div[2]/div/div[1]/div/div[1]/div'.format(i))
        
        comment_text_elem = comment_elem.find_elements_by_xpath('.//div/div/span/div')

        if len(comment_text_elem) is 1:
            # grab comment text
            comment_text = comment_text_elem[0].text
            # potentially do some text parsing if you want, especially if you also need to parse the course or something
        
            commenter_elem = comment_elem.find_element_by_xpath('.//div/span/div/a')
            # get id of commenter
            commenter_profile_id = re.findall(r'user\/(.*)\/', commenter_elem.get_property("href"))[0]
            commenter_name = commenter_elem.text
            print(commenter_name)

            # add more fields if required (courses etc)
            to_add.append({
                'id': commenter_profile_id,
                'name': commenter_name
                # 'course': ?
            })
    except NoSuchElementException:
        break    
    i = i + 1


driver.close()

# log in to fbchat
# client = fbchat.Client(FB_EMAIL, FB_PASSWORD)

for u in to_add:
    # assuming different files per course
    with open('course.txt', 'a+') as f:
        f.seek(0)
        existing_users = f.read()
        if u['id'] not in existing_users:
            f.write(u['name'] + ', ' + u['id'] + '\n')
            # source course chat id from somewhere
            # client.addUsersToGroup([u['id']], course_chat_id)

# client.logout()
