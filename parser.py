from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
import json
import re



class Parser:
    def __init__(self, url: str) -> None:
        self.url = url
    
    def create_driver(self):
        # Настройка драйвера Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Запуск в фоновом режиме, без отображения окна браузера
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def scroll_page(self):
        SCROLL_PAUSE_TIME = 2

        # Получение высоты страницы
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Прокрутка до низа страницы
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Ожидание загрузки новой части страницы
            time.sleep(SCROLL_PAUSE_TIME)

            # Получение новой высоты страницы и сравнение с последней
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height


    def get_links(self) -> None:
        """
        получаем ссылки на объявления. не все объявления подгружаются сразу, поэтому
        для начала нужно прокрутить вниз до конца
        """
        self.create_driver()
        # Открытие сайта Avito
        self.driver.get(url)

        # прокрутить вниз
        self.scroll_page()

        # получаем код страницы
        html_code = self.driver.page_source

        soup = BeautifulSoup(html_code, 'html.parser')
        
        # Извлечение всех ссылок с заданным классом внутри div
        links = soup.select('.market_row_name a')

        # Извлечение href из каждой ссылки
        self.urls = [link.get('href') for link in links]

    def get_all_data(self):
        """
        Проходиться по всем ссылкам и передает случайное значение для time.sleep().
        """
        for idx, link in enumerate(self.urls[self.id:]):
            print(self.get_data('https://vk.com' + link))
            self.data['id'] = self.id + idx
            self.set_context()

            # после того как прошлись по всем ссылкам окно браузера закрыватся

    def get_data(self, url) -> dict:
        self.driver.get(url)
        time.sleep(2)
        
        data = {
            'photos': [],
            'title': '',
            'price': '',
            'description': '',
            'category': '',
        }

        data['photos'] = self.get_images()
        data['price'] = self.get_price()
        data['description'] = self.get_desc()
        data['title'] = self.get_title()
        # data['category'] = self.get_category()

        return data

    def get_images(self) -> list:
        pattern = r'["\'](.*?)["\']'
        photo_blocks = self.driver.find_elements(By.CLASS_NAME, 'ItemGallery__thumb')
        return [re.findall(pattern, photo_block.get_attribute('style'))[0] for photo_block in photo_blocks]


    def get_price(self) -> str:
        price = self.driver.find_element(By.CSS_SELECTOR, ".ItemPrice-module__actual--lyqkb span")
        return price.text

    def get_title(self) -> str:
        title = self.driver.find_element(By.CLASS_NAME, "ItemName")
        return title.text

    def get_desc(self) -> str:
        desc = self.driver.find_element(By.CLASS_NAME, "ItemDescription")
        return desc.text

    def get_category(self) -> str:
        category = self.driver.find_element(By.CSS_SELECTOR, ".ItemCardLayout__right h5 a")
        return category.text

    def get_context(self):
        # Открытие и чтение JSON файла
        with open('context.json', 'r') as file:
            self.data = json.load(file)

        if self.data['url'] == self.url:
            self.id = self.data['id']

        else:
            self.id = 0
            self.data['url'] = self.url

    def set_context(self):
        with open('context.json', 'w') as file:
            json.dump(self.data, file, indent=4)
 


if __name__ == "__main__":
    url = "https://vk.com/market-213936507?screen=group"
    pars = Parser(url)        
    pars.get_context()
    pars.get_links()
    pars.get_all_data()