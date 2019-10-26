import os
import sys
import math
import requests
import re
from lxml import html
from bs4 import BeautifulSoup
from pprint import pprint


FILES_DIR_NAME = "files"
URL_TEMPLATE = 'https://habr.com/ru/top/yearly/page{}/'


def load_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if not response.ok:
        return None

    return response.text


def count_posts_per_page(text):
    soup = BeautifulSoup(text, 'html.parser')
    posts_title = soup.find_all('h2', {'class': 'post__title'})
    return len(posts_title)


def read_file(filename):
    with open(FILES_DIR_NAME + '/' + filename, 'r') as input_file:
        text = input_file.read()
    return text


def parse_file(filename, posts_per_page):
    clean_posts = []

    text = read_file(filename)
    tree = html.fromstring(text)

    for i in range(posts_per_page):
        post = {}
        post['post_author'] = tree.xpath('//header[@class = "post__meta"]/a[@class = "post__user-info user-info"]/span[@class = "user-info__nickname user-info__nickname_small"]/text()')[i]
        post['post_date'] = tree.xpath('//header[@class = "post__meta"]/span/text()')[i]
        post['post_title'] = tree.xpath('//h2[@class = "post__title"]/a/text()')[i]
        
        post_with_tags = tree.xpath('//div[@class="post__body post__body_crop "]/div[@class = "post__text post__text-html js-mediator-article"]')[i]
        post_with_tags_str = post_with_tags.text_content().strip()
        post_str_clean = re.sub('(\\n+|\s{2,})', ' ', post_with_tags_str)
        post['short_description'] = post_str_clean
     
        clean_posts.append(post)
        i += 1

    return clean_posts


def main():
    if len(sys.argv) < 2:
        print('Введите число — количество постов, которые требуется вывести')
    else:
        count = sys.argv[1]
        try:
            count = int(count)
        except ValueError:
            print('Количество постов должно быть целым неотрицательным числом')
            exit()
        if count < 0:
            print('Количество постов должно быть целым неотрицательным числом')
            exit()            
        if count == 0:
            print('Запрошено нулевое количество постов')
            exit()

        # создаем директорию под файлы (если не существует)
        os.makedirs(FILES_DIR_NAME, exist_ok=True)

        # удаляем старые файлы из директории
        for file in os.listdir(FILES_DIR_NAME):
            os.remove(os.path.join(FILES_DIR_NAME, file))

        # вычисляем количество страниц для загрузки
        text = load_page(URL_TEMPLATE.format(1))

        if text is None:
            exit('Не удалось загрузить страницу {}'.format(URL_TEMPLATE.format(1)))

        posts_per_page = count_posts_per_page(text)
        pages_for_parsing = math.ceil(count/posts_per_page)

        # сохраняем на диск нужное количество страниц
        for page_number in range(pages_for_parsing):
            text = load_page(URL_TEMPLATE.format(page_number + 1))

            if text is None:
                exit('Не удалось загрузить страницу {}'.format(URL_TEMPLATE.format(page_number + 1)))

            with open(FILES_DIR_NAME + '/page_{}.html'.format(page_number + 1), 'w') as output_file:
                output_file.write(text)

        # парсим сохраненные страницы
        all_posts = []
        for filename in os.listdir(FILES_DIR_NAME):
            posts = parse_file(filename, posts_per_page)
            all_posts.extend(posts)

        posts_exact_count = all_posts.copy()[0:count]

        # отрисовываем таблицу
        for post in posts_exact_count:
            for key, value in enumerate(post):
                pprint('-' * 78)
                pprint(post[value])
            pprint('-' * 78)
                
          
if __name__ == '__main__':
    main()
