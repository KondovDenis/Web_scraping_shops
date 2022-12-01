import re
import requests
from bs4 import BeautifulSoup
from typing import List
from dataclasses import dataclass
from dataclasses import field
import json
import csv
import openpyxl





@dataclass
class ClothesAttr1:
    title: str = field(default=str)
    articul: str = field(default=str)
    img: str = field(default=str)
    describe: str = field(default=str)
    price: str = field(default=str)
    sex: str = field(default=str)
    sticker: str = field(default=str)
    compound: str = field(default=str)
    size: tuple[str] = field(default_factory=tuple)
    colors: tuple[str] = field(default_factory=tuple)




class TommyHilfigerParser:

    headers = {
            'authority': 'widget.fitanalytics.com',
            'accept': 'application/json',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://www.zara.com',
            'referer': 'https://www.zara.com/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }

    params = {
            'ajax': 'true',
        }

    _category_ref = []
    items_ref = {}
    sticker = []

    
    def _get_category(self) -> list[str]:
        print('LAUNCHING.....')
        dataframe = openpyxl.load_workbook("..\\options\\TommyRefCat.xlsx", data_only=True)
        dataframe1 = dataframe.active
        sheet = dataframe1['D1':'D34']
        sticker = dataframe1['B1':'B34']
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
            page = BeautifulSoup(str(soup.find_all('div', attrs={'class':'product-list_MXo7M'})), 'html.parser')
            for ref in page.find_all('a', href=True):
                self.items_ref[f'https://ru.tommy.com{ref["href"]}'] = sticker[index]
            index+=1
        return self.items_ref


    def get_items_attributes_and_create_csv_01(self) -> ClothesAttr1:
        
        self.get_items_from_category()
        print('EXTRACTING DATA FROM:')
        for ref, sticker in self.items_ref.items():
            print(ref)
            response = requests.get(ref, params=self.params, headers=self.headers).text
            soup = BeautifulSoup (response, 'html.parser')
            
            articul = soup.find(class_='description__sidebar-content--style_2mbzg').text
            title = soup.find(class_='product__brand_2wPmY').text
            color = soup.find(class_='product-image__image_1mZ0I')['alt'].split()[0]           
            describe = soup.find(class_='product__name_1szxb').text
            compound = soup.find_all(name='div', class_='description__sidebar_13LcB')[0].find("span").text.split('• ')[-1]       
            image = f"https:{soup.find(class_='product-image__image_1mZ0I')['src']}"
            size = [x.text.replace('EU','')  for x in soup.find_all(name='button', class_='attribute-selector__button_Pdbtj attribute-selector__button--btn-min_P2IYQ')]
            try:
                price = round(float(soup.find(class_='price-display__selling_Ub68r').text.replace('руб.','').replace(' ','').replace(',','.')))       
            except AttributeError:
                try:
                    price = round(float(soup.find(class_='price-display__from_2SdRV').text.replace('руб.','').replace('От','').replace(' ','').replace(',','.')))
                except AttributeError:
                    price = soup.find(class_='pricePending').text
                    if price == 'Цена на рассмотрении':
                        continue
            sex = 'Для него' if soup.find(class_='breadcrumb__label_IodAb').text == 'Мужчины' else 'Для нее'                  
            resp = requests.get(image)
            filename = f'{articul}.jpg'.replace("'","")
            with open(f'..\\picture\\{filename}', 'wb') as file:
                file.write(resp.content)   
            for sizes in size:
                with open('..\\TommyClothes.csv', 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';', escapechar=" ", quoting=csv.QUOTE_NONE, doublequote=True)
                    img = f'https://marby.ru/picture/{filename}'
                    writer.writerows([['Tommy Hilfiger',f'{articul}',f'"Размер:{sizes}',f'Цвет:{color}"', f'{img}',f'{describe}', f'{title}', f'{price}', f'{sex}', f'{sticker}', f'{compound}']]) 
        print('The work is DONE.')
        return ClothesAttr1(img = img, colors = color, articul = articul, size = sizes.text, describe = describe, title = title, price = price, sex = sex, sticker = sticker, compound = compound)        




