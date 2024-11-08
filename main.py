import time
import requests
import selectorlib
import smtplib, ssl
import os
import sqlite3

url = 'http://programmer100.pythonanywhere.com/tours/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
database_path = 'data.db'


# Headers are used for specific web server that don't like script programs, so these helps here showing the program as browser

class Event:
    def scrape(self, url):
        """Scrape the page source from the url"""
        response = requests.get(url, headers=HEADERS)
        source = response.text
        return source

    def extract(self, source):
        extractor = selectorlib.Extractor.from_yaml_file('extract.yaml')
        value = extractor.extract(source)['tours']
        return value


class Email:
    def send(self, raw_message):
        host = 'smtp.gmail.com'
        port = 465
        username = 'jeevasathappan2000@gmail.com'
        password = 'ypxn naqt nwau ghhx'
        receiver = 'jeevasathappan2000@gmail.com'
        context = ssl.create_default_context()
        message = f"""\
Subject: New Event on board
    
{raw_message}
    """
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(username, password)
            server.sendmail(username, receiver, message)
        print('Mail sent')


class Database:
    def __init__(self,database_path):
        self.connection = sqlite3.connect(database_path)
    def read(self, extracted):
        row = extracted.split(',')
        row = [r.strip() for r in row]
        band, city, date = row
        cursor = self.connection.cursor()
        cursor.execute('select * from events where band=? and city=? and date=?',
                       (band, city, date))
        rows = cursor.fetchall()
        print(rows)
        return rows


    def store(self, extracted):
        row = extracted.split(',')
        row = [r.strip() for r in row]
        cursor = self.connection.cursor()
        cursor.execute('insert into events values (?,?,?)', row)
        self.connection.commit()


if __name__ == '__main__':
    while True:
        event = Event()
        scraped = event.scrape(url)
        extracted = event.extract(scraped)
        print(extracted)

        if extracted != 'No upcoming tours':
            db = Database(database_path)
            rows = db.read(extracted)
            if not rows:
                db.store(extracted)
                email = Email()
                email.send(extracted)
        time.sleep(2)
