import requests as re
from bs4 import BeautifulSoup as bs
import csv

URL = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/bryuki-i-shorty'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'accept': '*/*',
    'accept-language': 'ru'
}
HOST = 'https://www.wildberries.ru'
FILE = 'bd.csv'

# Количество страниц которые нужно спарсить
AMOUNT_PG = 10


#Получение страницы, передаем в неё URL, HEADERS эмулирует запросы с браузера
def get_page(url, params=None):
    page = re.get(url, headers=HEADERS, params=params)
    return page


# Сохранение файла в формате таблицы в Excel
def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Имя/Модель', 'Ссылка'])
        for item in items:
            writer.writerow([item['title'], item['href']])

# Ищем следующую страницу
def next_page(html):
    soup = bs(html, 'html.parser')
    pagination = soup.find('a', class_='pagination-next').get('href')
    if pagination:
        return pagination
    else:
        return 'Error'

# Заполняем список именем, ссылкой и ценой товара.
def get_content(html):
    soup = bs(html, 'html.parser')
    items = soup.find_all('div', class_='dtList-inner')
    shirts = []
    for item in items:
        shirts.append({
            'title': item.find('strong', class_='brand-name c-text-sm').get_text(strip=True) + item.find('span', class_='goods-name c-text-sm').get_text(strip=True),
            'href': HOST + item.find('a', class_='ref_goods_n_p j-open-full-product-card').get('href'),
            'price': item.find('span', class_='price').get_text()
        })
    return shirts

def parse():
    page = get_page(URL)
    newpg = next_page(page.text)
    shirts = []
    if newpg == 'Error':
        print('Error')
    else:
        for i in range(AMOUNT_PG):
            # Парсим пока ответ от сервера в пределах 200-299
            if page.status_code >= 200 and page.status_code < 300:
                i += 1
                shirts.extend(get_content(page.text))
                newpg = next_page(page.text)
                if newpg == 'Error':
                    print('Bad reading new page')
                    break
                else:
                    page = get_page(HOST + newpg)
                print(f'Parse {i}')
            else:
                print('Error')
    save_file(shirts, FILE)

parse()