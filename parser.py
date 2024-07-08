from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import time
import random
import json
import requests
import re



class Parser:
    def __init__(self, url: str) -> None:
        self.url = url
        self.id = 0
    
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

    def get_market(self) -> None:
        access_token = "vk1.a.dz0piXUODPKvtSX110vxx9hUIgnFLbJBEvSfzRyjJVsYQwMp6R3ni8gYJPFTugZMOKh_ieRpdzkS3SHCixuCKaXBsDkcUiqjbDkDZGm9Zi0EGet6yKM377a5vssewo7CMGnpUmWuziz1m3VSuYC3kztTkf5LVMCIkgvxjMnZCLsXUBVttvOadvwJvSSowNUlHLmbtFikGDczJ8_RWqF1EA"
        api_version = "5.199"


        # Извлечение owner_id из URL
        match = re.search(r"market-(\d+)", self.url)

        owner_id = match.group(1)

        # Добавление заголовка Authorization
        headers = {
            "Authorization": "Bearer " + access_token
        }
        server_url = f"https://api.vk.com/method/market.get?owner_id=-{owner_id}&v={api_version}"

        # Выполнение запроса
        self.response = requests.get(server_url, headers=headers).json()


    def get_links(self) -> None:
        """
        получаем ссылки на объявления. не все объявления подгружаются сразу, поэтому
        для начала нужно прокрутить вниз до конца
        """
        self.create_driver()
        # Открытие сайта Avito
        self.driver.get(self.url)


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
        for idx, link in enumerate(self.urls):
            print(self.get_data('https://vk.com' + link))

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
        data['category'] = self.get_category()

        return data

    def replace_size(self, url):
        # Парсим URL
        parsed_url = urlparse(url)
        
        # Разбираем параметры запроса
        query_params = parse_qs(parsed_url.query)
        
        # Меняем значение параметра 'cs' на '510x510'
        query_params['cs'] = '510x510'
        
        # Кодируем параметры обратно в строку запроса
        new_query = urlencode(query_params, doseq=True)
        
        # Собираем новый URL
        new_url = urlunparse(parsed_url._replace(query=new_query))
        
        return new_url

    def get_images(self) -> list:
        pattern = r'["\'](.*?)["\']'
        photo_blocks = self.driver.find_elements(By.CLASS_NAME, 'ItemGallery__thumb')
        images = [re.findall(pattern, photo_block.get_attribute('style'))[0] for photo_block in photo_blocks]
        return list(map(self.replace_size, images))


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
        category = self.response['response']['items'][self.id]['category']['name']
        return category

 


if __name__ == "__main__":
    url = "https://vk.com/market-186208863"
    pars = Parser(url)        
    pars.get_market()
    pars.get_links()
    pars.get_all_data()