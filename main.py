import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

# функция которая парсит посты
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

    with open("data.txt", "w") as data:
        data.write(str(posts_data))

    return posts_data

# функция показа собранных данных в терминал
def written_posts_data():
    with open("data.txt", 'r') as data:

        r = data.read()
        print(r)

# Извлекает данные из элемента поста
def extract_post_data(post_element, base_url):
    try:
        # Заголовок
        title_elem = post_element.select_one('.story__title a')
        title = title_elem.get_text(strip=True) if title_elem else 'Без заголовка'
        link = title_elem['href'] if title_elem and title_elem.get('href') else ''

        # Автор
        author_elem = post_element.select_one('.user__nick')
        author = author_elem.get_text(strip=True) if author_elem else 'Неизвестный'


        # Количество комментариев
        comments_elem = post_element.select_one('.story__comments-link-count')
        comments = comments_elem.get_text(strip=True).split()[0] if comments_elem else '0'

        return {
            'title': title,
            'link': link,
            'author': author,
            'comments': comments
        }
    except Exception as e:
        print(f"Ошибка при парсинге поста: {e}")
        return None


# Сохраняет данные в CSV-файл, дополняя его
def save_to_csv(data, filename='pikabu_posts.csv', unique_key='link'):
    df = pd.DataFrame(data)
    df_clean = df[df['comments'] != '0']
    file_exists = os.path.isfile(filename)
    if file_exists:
        try:
            # Читаем существующие данные
            existing_df = pd.read_csv(filename)
            # Получаем множество существующих уникальных идентификаторов
            existing_ids = set(existing_df[unique_key].dropna())
            print(f"Загружено {len(existing_ids)} существующих идентификаторов")

            # Фильтруем новые данные: оставляем только строки с новыми ID
            new_posts = df_clean[~df_clean[unique_key].isin(existing_ids)]
            duplicates_count = len(df_clean) - len(new_posts)
            print(f"Обнаружено {duplicates_count} дубликатов — они не будут сохранены")
        except Exception as e:
            print(f"Ошибка при чтении существующего файла: {e}")
            # Если ошибка чтения, сохраняем все отфильтрованные данные
            new_posts = df_clean
    else:
        # Если файла нет, все отфильтрованные данные — новые
        new_posts = df_clean
        print("Файл не существует, все данные считаются новыми")

        # Сохраняем только новые данные
        if new_posts.empty:
            print("Нет новых статей для сохранения")
            return
        try:
            new_posts.to_csv(
                filename,
                mode='a',
                header=not file_exists,  # заголовки только для нового файла
                index=False,
                encoding='utf-8-sig'
            )
            print(f"Добавлено {len(new_posts)} новых статей в {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")

# Основной запуск
if __name__ == '__main__':
    print("Начинаем парсинг новых постов с Pikabu.ru...")
    posts = parse_pikabu_new_posts(pages=1) # выбираем количество страниц pages=1
    save_to_csv(posts)
    written_posts_data()
    print(f"Успешно собрано {len(posts)} постов")
