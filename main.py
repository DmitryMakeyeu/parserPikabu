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

def extract_post_data(post_element, base_url):
    """Извлекает данные из элемента поста"""
    try:
        # ID поста
        post_id = post_element.get('data-post-id', '')

        # Заголовок
        title_elem = post_element.select_one('.story__title a')
        title = title_elem.get_text(strip=True) if title_elem else 'Без заголовка'
        link = base_url + title_elem['href'] if title_elem and title_elem.get('href') else ''

        # Автор
        author_elem = post_element.select_one('.user__nick')
        author = author_elem.get_text(strip=True) if author_elem else 'Неизвестный'


        # Рейтинг
        rating_elem = post_element.select_one('.rating__value')
        rating = rating_elem.get_text(strip=True) if rating_elem else '0'

        # Количество комментариев
        comments_elem = post_element.select_one('.story-meta__comments-link')
        comments = comments_elem.get_text(strip=True).split()[0] if comments_elem else '0'

        return {
            'id': post_id,
            'title': title,
            'link': link,
            'author': author,
            'rating': rating,
            'comments': comments
        }
    except Exception as e:
        print(f"Ошибка при парсинге поста: {e}")
        return None

def save_to_csv(data, filename='pikabu_posts.csv'):
    """Сохраняет данные в CSV-файл"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Данные сохранены в {filename}")

# Основной запуск
if __name__ == '__main__':
    print("Начинаем парсинг новых постов с Pikabu.ru...")
    posts = parse_pikabu_new_posts(pages=1) # выбираем количество страниц pages=1
    save_to_csv(posts)
    print(f"Успешно собрано {len(posts)} постов")
