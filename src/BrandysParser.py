import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from dataclasses import field
import csv
import openpyxl





@dataclass
class ClothesAttr1:
    title: str = field(default=str)
    articul: str = field(default=str)
    image_1: str = field(default=str)
    image_2: str = field(default=str)
    describe: str = field(default=str)
    price_old: str = field(default=str)
    price_new: str = field(default=str)
    sex: str = field(default=str)
    sticker: str = field(default=str)
    compound: str = field(default=str)
    size: list[str] = field(default_factory=list)
    colors: tuple[str] = field(default_factory=tuple)


class BrandysParser:

    headers = {
        'authority': 'www.brandys.com.tr',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    params = {
            'ajax': 'true',
        }

    _category_ref = []
    items_ref = {}
    sticker = []

    
    def _get_category(self) -> list[str]:
        print('LAUNCHING.....')
        dataframe = openpyxl.load_workbook("..\\Parser\\options\\BrandysRefCat.xlsx", data_only=True)
        dataframe1 = dataframe.active
        sheet = dataframe1['D2':'D32']
        sticker = dataframe1['B2':'B32']
        for index, item in enumerate(sticker):
            for cell in item:
                self.sticker.append(cell.value)

        for index, item in enumerate(sheet):
            for cell in item:
                self._category_ref.append(cell.value)
        return self._category_ref, self.sticker


    def get_items_from_category(self) -> list[str]:
        
        category, sticker = self._get_category()
        index = 0
        for val in category:
            response = requests.get(val, params=self.params, headers=self.headers).text
            soup = BeautifulSoup (response, 'html.parser')
            numberofpage = soup.find_all('a', attrs={'class':'pagination__item js-pagination-item'})[-1].text.strip() if len(soup.find_all('a', attrs={'class':'pagination__item js-pagination-item'})) > 0 else '1'
            for value in range(1,int(numberofpage)):
                response = requests.get(f'{val}?page={value}', params=self.params, headers=self.headers).text
                soup = BeautifulSoup (response, 'html.parser')
                page = BeautifulSoup(str(soup.find_all('div', attrs={'class':'products__items'})), 'html.parser')
                
                for ref in page.find_all('a', href=True):
                    self.items_ref[f'https://www.brandys.com.tr{ref["href"]}'] = sticker[index]
            index+=1
        return self.items_ref


    def get_items_attributes_and_create_csv_01(self) -> ClothesAttr1:
    
        self.get_items_from_category()
        print('EXTRACTING DATA FROM:')
        for ref, sticker in self.items_ref.items():
            print(ref)
            response = requests.get(ref, params=self.params, headers=self.headers).text
            soup = BeautifulSoup (response, 'html.parser')
            try:
                articul = ''.join(soup.find_all('div', attrs={'class':'row'})[1].text.split()[2:5])
            except IndexError:
                articul = 'NOT_FOUND_ARTICUL'
            try:    
                describe = soup.find(class_='texts__product-name').text.strip()
            except AttributeError:
                describe = 'NOT_FOUND_DESCRIBE'
            try:
                title = ' '.join(soup.find(class_='sub-action__categories').text.split()[2::]) if len(' '.join(soup.find(class_='sub-action__categories').text.split()[2::]).strip()) > 1 else describe
            except AttributeError:
                title = 'NOT_FOUND_TITLE'
            try:  
                color = soup.find(class_='variant-header__text').text.split()[-1]
            except AttributeError:
                color = 'NOT_FOUND_COLOR'
            try:                               
                compound = ' '.join(soup.find_all('div', attrs={'class':'row'})[1].text.split()[6::])
            except  IndexError:
                compound = 'NOT_FOUND_COMPOUND'
            try:                      
                sex = 'Для него' if soup.find_all('a', attrs={'class':'pz-breadcrumb__link'})[2].text.strip() == 'Erkek' or soup.find_all('a', attrs={'class':'pz-breadcrumb__link'})[3].text.strip() == 'Erkek' else 'Для нее'
            except  IndexError:
                compound = 'NOT_FOUND_SEX'
            try:
                image_1 = str(soup.find_all('img', attrs={'data-zoom-id':'zoom_1'})[0]).split()[-1].replace('src="','').replace('"/>','')
            except IndexError:
                image_1 = 'NOT_FOUND_IMAGE1'
            
            try:
                image_2 = str(soup.find_all('img', attrs={'data-zoom-id':'zoom_3'})[0]).split()[-1].replace('src="','').replace('"/>','')
            except IndexError:
                try:
                    image_2 = str(soup.find_all('img', attrs={'data-zoom-id':'zoom_2'})[0]).split()[-1].replace('src="','').replace('"/>','')
                except  IndexError:
                    image_2 = 'NOT_FOUND_IMAGE2'
            
            try:
                size = list(map(lambda x: x.text.replace('\n',' ').strip(), soup.find_all('div', attrs={'class':'options options--size'})[0].find_all('div', attrs={'class':'option js-variant'}))) if list(map(lambda x: x.text.replace('\n',' ').strip(), soup.find_all('div', attrs={'class':'options options--size'})[0].find_all('div', attrs={'class':'option js-variant'}))) != [] else list(map(lambda x: x.text.replace('\n',' ').strip(), soup.find_all('div', attrs={'class':'options options--size'})[0].find_all('div', attrs={'class':'option js-variant selected'})))
                
            except IndexError:
                size = 'NOT_FOUND_SIZE'
            
            try:
                price_old = round(float(soup.find(class_='texts__product-price').text.replace('TL', '').replace('.','').replace(',','.').strip()) * 8.4)
                price_new = price_old
            except ValueError:
                try:
                    price_old = round(float(soup.find(class_='price__old').text.replace('TL', '').replace('.','').replace(',','.').strip()) * 8.4)
                    price_new = round(float(soup.find(class_='price__new').text.replace('TL', '').replace('.','').replace(',','.').strip()) * 8.4)
                except AttributeError:
                    price_old = 'NOT_FOUND_PRICE_OLD'
                    price_new = 'NOT_FOUND_PRICE_NEW'
            
            if size == 'NOT_FOUND_SIZE' or size == []:
                with open('..\\Parser\\BrandysClothes.csv', 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';', escapechar=" ", quoting=csv.QUOTE_NONE, doublequote=True)
                    writer.writerows([[f'{title}',f'{articul}',f'Цвет:{color.strip()}', f'{image_1} {image_2}',f'{describe}', f'{title}', f'{price_old}', f'{price_new}', f'{sex}', f'{sticker}', f'{compound}']])
            elif size != 'NOT_FOUND_SIZE' or size != []:
                for sizes in size:
                    with open('..\\Parser\\BrandysClothes.csv', 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f, delimiter=';', escapechar=" ", quoting=csv.QUOTE_NONE, doublequote=True)
                        writer.writerows([[f'{title}',f'{articul}',f'"Размер:{sizes}',f'Цвет:{color.strip()}"', f'{image_1} {image_2}',f'{describe}', f'{title}', f'{price_old}', f'{price_new}', f'{sex}', f'{sticker}', f'{compound}']])
        print('The work is DONE.')
        return ClothesAttr1(image_1 = image_1, image_2 = image_2, colors = color, articul = articul, size = size, describe = describe, title = title, price_old = price_old, price_new = price_new, sex = sex, sticker = sticker, compound = compound)  
