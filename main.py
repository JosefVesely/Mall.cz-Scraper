#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests, schedule, smtplib, os
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from bs4 import BeautifulSoup

__author__ = 'Josef Veselý | u/3majorr'

URL = 'https://www.mall.cz/herni-klavesnice/razer-ornata-chroma-us-rz03-02040100-r3m1-994895?gclid=Cj0KCQjw2K3rBRDiARIsAOFSW_5QVawskB9HCsG6Ivq4znXp6KNKJxP-2B-DhJcB9LcrHjc4BLQIzY4aAuAvEALw_wcB'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
_class = 'pro-price variant-BC con-emphasize font-primary--bold mr-5'

frm = 'scraper51@yahoo.com' # sender's mail
to = os.environ.get('EMAIL') # receiver's mail
password = os.environ.get('PASSWORD')

class File:
    def read(self):
        with open('price.txt', 'r+') as f: # opens the text file
            latest_price = f.read()
            return f, latest_price

    def change(self):
        with open('price.txt', 'r+') as f:
            f.seek(0)
            f.truncate(0) # erases the text file content
            f.write(price[:4]) # writes the current price into the file

file = File()
f, latest_price = file.read()


def get_price():
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('b', class_=_class).get_text().strip().replace(' ', '')
    int_price = int(price[:4])
    return price, int_price
price, int_price = get_price()

def create_message():
    if int(latest_price) < int_price:
        difference = int_price - int(latest_price)
        description = f'Price raised by {difference}Kč!'
    elif int(latest_price) > int_price:
        difference = int(latest_price) - int_price
        description = f'Price dropped by {difference}Kč!'
    else:
        description = 'Price didn\'t changed!'

    subject = f'Razer Ornata Chroma - {int_price}Kč'
    message = f'{description}\n\nhttps://bit.ly/2M0tptf'
    return subject, message
subject, message = create_message()

def send_mail():
    smtp_host = 'smtp.mail.yahoo.com'

    create_message() # creates the message content

    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = frm
    msg['To'] = to

    s = smtplib.SMTP(smtp_host, 587)

    try:
        s.starttls()
        s.login(frm, password)
        s.sendmail(msg['From'], to, msg.as_string())
    finally:
        s.quit()

    print('Mail sent!')
    print(msg)

file.read()
send_mail()
file.change()
