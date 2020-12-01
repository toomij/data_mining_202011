import os
import time
import datetime as dt
import requests
import bs4
import pymongo
import dotenv
from urllib.parse import urljoin

dotenv.load_dotenv('.env')
dotenv.load_dotenv('.env')
MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}

class MagnitParse:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:83.0) Gecko/20100101 Firefox/83.0'
    }

    def __init__(self, start_url):
        self.start_url = start_url
        client = pymongo.MongoClient(os.getenv('DATA_BASE'))
        self.db = client['gb_parse_11']


    @staticmethod
    def _get(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    raise Exception
                return response
            except Exception:
                time.sleep(0.5)

    def soup(self, url) -> bs4.BeautifulSoup:
        response = self._get(url, headers=self.headers)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self):
        soup = self.soup(self.start_url)
        for product in self.parse(soup):
            self.save(product)

    def parse(self, soup):
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.find_all('a', recursive=False):
            pr_data = self.get_product(product)
            yield pr_data

    def get_product(self, product_soup) -> dict:

        # {
        #     "url": str,
        #     "promo_name": str,
        #     "product_name": str,
        #     "old_price": float,
        #     "new_price": float,
        #     "image_url": str,
        #     "date_from": "DATETIME",
        #     "date_to": "DATETIME",
        # }
        try:
            dt_parser = self.date_parse(product_soup.find('div', attrs={'class': 'card-sale__date'}).text)
        except Exception as e:
            pass

        product_template = {
            'url': lambda soup: urljoin(self.start_url, soup.get('href')),
            'promo_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__header'}).text,
            'product_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__title'}).text,
            'old_price': lambda soup: soup.find('div', attrs={'class': 'label__price_old'}).text,
            'new_price': lambda soup: soup.find('div', attrs={'class': 'label__price_new'}).text,
            'image_url': lambda soup: urljoin(self.start_url, soup.find('img').get('data-src')),
            'date_from': lambda _: next(dt_parser),
            'date_from': lambda _: next(dt_parser),
        }

        result = {}
        for key, value in product_template.items():
            try:
                result[key] = value(product_soup)
            except Exception as e:
                continue
        return result

    @staticmethod
    def date_parse(date_string: str):
        date_list = date_string.replace('с ', '', 1).replace('\n', '').split('до')
        for date in date_list:
            temp_date = date.split()
            yield dt.datetime(year=dt.datetime.now().year, day=int(temp_date[0]), month=MONTHS[temp_date[1][:3]])


    def save(self, product):
        collection = self.db['magnit_11']
        collection.insert_one(product)


if __name__ == '__main__':
    parser = MagnitParse('https://magnit.ru/promo/?geo=moskva')
    parser.run()
