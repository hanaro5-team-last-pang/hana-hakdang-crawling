from flask import Flask, jsonify
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# 크롤링 함수
def fetch_news_articles():
  base_url = "https://www.fetimes.co.kr/news/articleList.html?sc_section_code=S1N16&view_type=sm"
  days_limit = 30
  all_articles = []
  today = datetime.now()
  date_limit = today - timedelta(days=days_limit)
  page = 1

  while True:
    url = f"{base_url}&page={page}"
    response = requests.get(url)

    if response.status_code != 200:
      break

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.select('div.view-cont')

    if not articles:
      break

    for article in articles:
      try:
        title_tag = article.select_one('h4.titles a')
        content = article.select_one('p.lead')
        img_tag = article.find_previous_sibling('a').find('img') if article.find_previous_sibling('a') else None
        em_elements = article.select('span.byline em')

        if not title_tag or not content or not img_tag or len(em_elements) < 3:
          continue

        date_text = em_elements[2].get_text(strip=True)
        article_date = datetime.strptime(date_text, "%Y.%m.%d %H:%M")
        if article_date < date_limit:
          return all_articles

        all_articles.append({
          'title': title_tag.get_text(strip=True),
          'content': content.get_text(strip=True),
          'newsUrl': title_tag['href'] if title_tag['href'] else "N/A",
          'newsThumbnailUrl': img_tag['src'] if img_tag else "N/A",
          'date': date_text
        })
      except Exception as e:
        print(f"Error parsing article: {e}")

    page += 1

  return all_articles

# Flask 엔드포인트
@app.route('/news', methods=['GET'])
def get_news():
  articles = fetch_news_articles()
  return jsonify(articles)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5001)  # Python 서버를 5000번 포트에서 실행

