
import os
import re
import smtplib
import requests
from bs4 import BeautifulSoup
from email.header import Header
from email.mime.text import MIMEText

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

url = open('url.txt', 'r').read()

page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')

class_name = 'hidden-small lay-overflow-hidden word-break--word mt-0'
class_price = 'final-price'

frm = 'scraper51@yahoo.com'  # sender's e-mail
password = os.environ.get('EMAIL_PASSWORD')
to = os.environ.get('EMAIL_ADDRESS')  # receiver's e-mail


def get_name():
    name = soup.find('h1', class_=class_name).get_text()
    return name


def get_price():
    price = soup.find('b', class_=class_price).get_text().strip()  # -> 1 999Kč
    price = price.replace(' ', '')  # -> 2999Kč
    price = int(price[:-2])  # 2999
    return price


def get_latest_price(name, price):
    filename = re.sub(r'\W+', '', name)  # strip everything but alphanumeric characters

    with open(f'prices/{filename}.txt', 'w+') as f:
        content = f.read()

        if content == '':
            return price

        return int(content)


def save_latest_price(name, price):
    filename = re.sub(r'\W+', '', name)

    with open(f'prices/{filename}.txt', 'w') as f:
        f.truncate(0)  # erase file
        f.write(str(price))


def create_message(price, latest_price):
    if latest_price < price:
        difference = price - latest_price
        description = f'Price raised by {difference}Kč'

    elif latest_price > price:
        difference = latest_price - price
        description = f'Price dropped by {difference}Kč'

    else:
        description = 'Price didn\'t change'

    message = description + '\n\n' + url
    return message


def send_mail(subject, message):
    smtp_host = 'smtp.mail.yahoo.com'

    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = frm
    msg['To'] = to

    s = smtplib.SMTP(smtp_host, 587)

    try:
        s.starttls()
        s.login(frm, password)
        s.sendmail(msg['From'], to, msg.as_string())
        print('Mail sent successfully!')
    except:
        print('Mail not sent.')

    s.quit()


name = get_name()
price = get_price()
latest_price = get_latest_price(name, price)

print(create_message(price, latest_price))
send_mail(subject=name, message=create_message(price, latest_price))
save_latest_price(name, price)
