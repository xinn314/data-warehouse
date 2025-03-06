import requests
from bs4 import BeautifulSoup
import json
import re
import datetime  # 导入 datetime 模块

def is_chinese(text, ratio=0.6):
    """
    判断字符串是否主要由中文字符组成。
    """
    chinese_count = 0
    total_count = 0

    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文 Unicode 范围
            chinese_count += 1
        total_count += 1

    if total_count == 0:
        return False  # 空字符串

    return (chinese_count / total_count) >= ratio

def get_douban_top250():
    all_movies = []
    for start in range(0, 250, 25):
        url = f'https://movie.douban.com/top250?start={start}&filter='
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for movie_item in soup.find_all('div', class_='item'):
                ranking = int(movie_item.find('em').text)
                title_div = movie_item.find('div', class_='hd')
                title_spans = title_div.find('a').find_all('span')
                title_texts = [span.get_text(strip=True) for span in title_spans]

                titles = " / ".join(title_texts).split(" / ")
                chinese_title = titles[0]
                foreign_title = ''

                if len(titles) > 1:
                    temp_foreign = titles[1].replace('\xa0', '').replace(' ', '')
                    if is_chinese(temp_foreign) and len(titles) > 2:
                        foreign_title = titles[2].replace('\xa0', '').replace(' ', '')
                    else:
                        foreign_title = temp_foreign

                rating = float(movie_item.find('span', class_='rating_num').text)
                try:
                    p_tag = movie_item.find('div', class_='bd').find('p')
                    if p_tag:
                        text = p_tag.get_text(strip=True)
                        match = re.search(r'(\d{4})', text)
                        year = int(match.group(1)) if match else None
                    else:
                        year = None
                except AttributeError as e:
                    print(f"在排名 {ranking} 的电影中提取年份时出错: {e}")
                    year = None

                movie_data = {
                    'ranking': ranking,
                    'chinese_title': chinese_title,
                    'foreign_title': foreign_title,
                    'rating': rating,
                    'year': year
                }
                all_movies.append(movie_data)

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return []
        except Exception as e:
            print(f"发生其他错误: {e}")
            return []

    return all_movies

if __name__ == '__main__':
    top250_data = get_douban_top250()
    if top250_data:
        # 获取当前日期时间
        now = datetime.datetime.now()
        update_time = now.strftime("%Y-%m-%d %H:%M:%S")  # 格式化为字符串
        # 在数据中添加更新时间
        data_with_time = {
            'update_time': update_time,
            'movies': top250_data
        }

        # 生成带日期的文件名
        date_str = now.strftime("%Y%m%d")
        filename = f'douban_top250_{date_str}.json'

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_with_time, f, ensure_ascii=False, indent=2)
        print(f"豆瓣Top250数据已保存到 {filename} 文件中。")