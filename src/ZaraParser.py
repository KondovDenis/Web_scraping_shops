import requests
from bs4 import BeautifulSoup
from typing import List
from dataclasses import dataclass
from dataclasses import field
import json
import csv






@dataclass
class ClothingAttributes:
    title: str = field(default=str)
    articul: str = field(default=str)
    image: str = field(default=str)
    describe: str = field(default=str)
    size: tuple[str] = field(default_factory=tuple)
    colors: tuple[str] = field(default_factory=tuple)
    

        

@dataclass
class ReferenceAttributes:
    keyword: list[str] = field(default_factory=list)
    seoProductId: list[str] = field(default_factory=list)
    discernProductId: list[str] = field(default_factory=list)


class ZaraParser:

    categories_id_ajax = []

    headers = {
            'authority': 'widget.fitanalytics.com',
            'accept': 'application/json',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            # 'cookie': 'connect.sid.zara=s%3AbV5VAVgWh5aS8LJf8V8-kk-qh-4aVIOf.4%2FpBkWMjBenL2z3i2oLnklL%2Fntj3W%2B0qTRi38TPx8b8',
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

    def get_categories(self) -> list[int]:
        ''' Parsing main page of Zara and extracting categories. 
            Return list with categories_id. '''
        
        response = requests.get('https://www.zara.com/ru/ru/categories', params=self.params, headers=self.headers).json()
    
        man = response['categories'][1]
        woman = response['categories'][0]

        for index in range(len(man['subcategories'])):
            self.categories_id_ajax.append(man['subcategories'][index]['id'])
        
        for index1 in range(len(woman['subcategories'])):
            self.categories_id_ajax.append(woman['subcategories'][index1]['id'])
        print(f"Founded {len(man['subcategories'])+len(woman['subcategories'])} categories.")
    
    
    
    def get_items_from_categories(self) -> ReferenceAttributes:
        """  Generate reference with categorie's id which we get from self.get_categories() after that
           get reference's attributes for everyone items from category. """
        self.get_categories()
        
        
        for ids in self.categories_id_ajax:
            response = requests.get(f'https://www.zara.com/ru/ru/category/{ids}/products',  headers=self.headers, params=self.params).json()
            try:
                keyword = []
                seoProductId = []
                discernProductId = []
                
                for index1 in range(len(response['productGroups'][0]['elements'])):
                    for index2 in range(len(response['productGroups'][0]['elements'][index1]['commercialComponents'])):
                        keyword.append(response['productGroups'][0]['elements'][index1]['commercialComponents'][index2]['seo']['keyword'])
                        seoProductId.append(response['productGroups'][0]['elements'][index1]['commercialComponents'][index2]['seo']['seoProductId'])
                        discernProductId.append(response['productGroups'][0]['elements'][index1]['commercialComponents'][index2]['seo']['discernProductId'])
                    
                return ReferenceAttributes(keyword = keyword, seoProductId = seoProductId,  discernProductId = discernProductId)
                        
            except TypeError:
                print("WARNING!!!! Something goes wrong. You need debug function 'get_items_from_categories()'")
                           


    def get_items_attributes_and_create_csv(self) -> ClothingAttributes:
        """Get all clothe's attributes and write it in file clothes.csv"""
        print('Running...')
        print('Start getting categories...')
        attributes = self.get_items_from_categories() 

        for category in self.categories_id_ajax:
            print(f'Parsing category ID {category}....')    
            for new_num in range (len(attributes.keyword)):
                try:
                    response =  requests.get(f'https://www.zara.com/ru/ru/{attributes.keyword[new_num]}-p{attributes.seoProductId[new_num]}.html?v1={attributes.discernProductId[new_num]}&v2={category}', headers=self.headers).text
                    soup = BeautifulSoup(response, 'html.parser')
                    #print(soup.prettify())
                    title = soup.find(class_='product-detail-info__header-name').text
                    image = str(soup.find('source', sizes="40vw")['srcset'].split()[0])
                    colors = soup.find(class_='product-detail-selected-color product-detail-info__color').text.split()[:-2] if len(tuple([x.text.strip() for x in soup.find_all(class_='product-detail-color-selector__color-marker', recursive=True)])) == 0  else tuple([x.text.strip() for x in soup.find_all(class_='product-detail-color-selector__color-marker', recursive=True)])
                    articul = articul = soup.find(class_='product-detail-selected-color product-detail-info__color').text.split()[-1]  if soup.find(class_='product-detail-selected-color product-detail-color-selector__selected-color-name')  is None else soup.find(class_='product-detail-selected-color product-detail-color-selector__selected-color-name').text.split()[-1]
                    size = tuple(soup.find(class_='product-detail-size-selector__size-list').text.replace('(','').strip().replace("Похожие товары","").split(')')[:-1])
                    describe = soup.find(class_='expandable-text__inner-content').text.replace('\n','')

                    for color in colors:
                        for sizes in size:
                            if 'Мы сообщим вам' in sizes or 'Coming soon' in sizes:
                                continue
                            
                            sizes = sizes.strip().split()
                            
                            if '/' in sizes[-1]:
                                sizes = sizes[0]
                            else:
                                sizes = sizes[-1]
                            
                            with open('C:\\Users\\DK\\onedrive\\desktop\\parser\\ZaraClothes.csv', 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f, delimiter=';', escapechar=" ", quoting=csv.QUOTE_NONE, doublequote=True)
                                writer.writerows([['ZARA',f'{articul}',f'"Размер:{sizes}',f'Цвет:{color}"', f'{image}',f'{describe}', f'{title}']]) 
                except Exception:
                    pass
        print('The work is DONE !')                           
        return ClothingAttributes(image = image, colors = colors, articul = articul, size = size, describe = describe, title = title)         

    
            
        
       



        


        