#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import smtplib
import requests
import colorama
from bs4 import BeautifulSoup
from termcolor import colored
from email.header import Header
from pyshorteners import Shortener
from email.mime.text import MIMEText


__author__ = 'Josef Veselý'


colorama.init()  # necessary to print colored text

headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

class_name = 'lay-overflow-hidden word-break--word mt-5'
class_price = 'pro-price variant-BC con-emphasize font-primary--bold mr-5'


frm = 'scraper51@yahoo.com'  # sender's mail
to = os.environ.get('EMAIL_ADDRESS')  # receiver's mail
password = os.environ.get('EMAIL_PASSWORD')


with open('url.txt', 'r') as f:
      url = f.read()

# check if URL starts with "http"
if 'http' not in url:
      url = f'http://{url}'


def scrape():
      page = requests.get(url, headers=headers)
      soup = BeautifulSoup(page.content, 'html.parser')

      try:
            name = soup.find('h1', class_=class_name).get_text()
      except AttributeError:
            input('URL address in file "url.txt" isn\'t leading to any MALL.CZ product. ')

            sys.exit()


      price = soup.find('b', class_=class_price).get_text().strip()  # -> 2 999Kč
      price = price.replace(' ', '')  # -> 2999Kč
      price = int(price[:-2])  # -> 2999 - as an int

      return name, price

name, price = scrape()


class File:
      def read(self):
            with open(f'prices/{name}.txt', 'w+') as f:
                  content = f.read()
                  if content == '':
                        f.write(f'{price}')
                        content = price

                  latest_price = int(content)
                  return latest_price


      def change(self):
            with open(f'prices/{name}.txt', 'r+') as f:
                  f.seek(0)
                  f.truncate(0)  # erases the text file content
                  f.write(f'{price}')  # writes the current price into the file

file = File()
latest_price = file.read()


def create_message():
      if latest_price < price:
          difference = price - latest_price
          description = f'Price raised by {difference}Kč!'
      elif latest_price > price:
          difference = latest_price - price
          description = f'Price dropped by {difference}Kč!'
      else:
          description = 'Price didn\'t change!'

      # shorts URL with TinyUrl
      shortener = Shortener('Tinyurl')
      short_url = shortener.short(url)  # shorts the URL -> www.tinyurl.com/link

      subject = f'{name}'
      content = f'{description} - {price}Kč\n\n{short_url}'
      return subject, content, short_url

subject, content, short_url = create_message()


def send_mail():
      smtp_host = 'smtp.mail.yahoo.com'

      create_message()

      msg = MIMEText(content, 'plain', 'utf-8')
      msg['Subject'] = Header(subject, 'utf-8')
      msg['From'] = frm
      msg['To'] = to

      s = smtplib.SMTP(smtp_host, 587)

      try:
            s.starttls()
            s.login(frm, password)
            s.sendmail(msg['From'], to, msg.as_string())
            print(colored('\n<--- Mail sent successfully! --->', 'green', attrs=['concealed']))
      except:
            print(colored('\n<--- Mail not sent :( Check send_mail function for more info. --->', 'red'))
      finally:
            s.quit()


def print_header(header):
      return colored(f'\n  {header}  ', 'blue', 'on_white')


def info():
      # prints some useful informations
      print(print_header('PRICE'))
      print(f'Latest price: {latest_price}Kč')
      print(f'Current price: {price}Kč')

      print(print_header('MESSAGE'))
      print(subject)
      print(content)


file.read()
info()
send_mail()
file.change()

input()
