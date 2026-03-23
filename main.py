import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def parse_pikabu_new_posts(pages=3):
    """
    Парсит новые посты с Pikabu.ru
    :param pages: количество страниц для парсинга
    :return: список словарей с данными постов
    """
    base_url = "https://pikabu.ru"
    posts_data = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for page_num in range(1, pages + 1):
        print(f"Парсим страницу {page_num}...")
        url = f"{base_url}/"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Находим все посты на странице
            posts = soup.select('div.story__main')


            for post in posts:
                post_data = extract_post_data(post, base_url)
                if post_data:
                    posts_data.append(post_data)

            # Случайная задержка между запросами
            time.sleep(random.uniform(1, 3))

        except requests.RequestException as e:
            print(f"Ошибка при запросе страницы {page_num}: {e}")
            continue

    return posts_data



# Основной запуск
if __name__ == '__main__':
    print("Начинаем парсинг новых постов с Pikabu.ru...")
    posts = parse_pikabu_new_posts(pages=1) # выбираем количество страниц pages=1
    print(f"Успешно собрано {len(posts)} постов")
