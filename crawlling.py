# 로컬에서 작동하는 코드

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
  app.run(host='0.0.0.0', port=5001)  # Python 서버를 5001번 포트에서 실행




#############################

# AWS 람다에 업로드 했던 함수
#
# import json
# import time
# import requests
# from datetime import datetime, timedelta
# from bs4 import BeautifulSoup
#
#
# def fetch_news_articles():
#   base_url = "https://www.fetimes.co.kr/news/articleList.html?sc_section_code=S1N16&view_type=sm"
#   days_limit = 30
#   all_articles = []
#   today = datetime.now()
#   date_limit = today - timedelta(days=days_limit)
#   page = 1
#
#   while True:
#     url = f"{base_url}&page={page}"
#     response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#
#     if response.status_code != 200:
#       print(f"Failed to fetch page {page}, status code: {response.status_code}")
#       break
#
#     soup = BeautifulSoup(response.text, "html.parser")
#     articles = soup.select("div.view-cont")
#
#     if not articles:
#       break
#
#     for article in articles:
#       try:
#         title_tag = article.select_one("h4.titles a")
#         content = article.select_one("p.lead")
#         img_tag = article.find_previous_sibling("a").find("img") if article.find_previous_sibling("a") else None
#         em_elements = article.select("span.byline em")
#
#         # 필수 요소가 없는 경우 스킵
#         if not title_tag or not content or not img_tag or len(em_elements) < 3:
#           continue
#
#         date_text = em_elements[2].get_text(strip=True) if len(em_elements) > 2 else None
#         if not date_text:  # 날짜 정보가 없으면 스킵
#           print("Skipping article due to missing date.")
#           continue
#
#         try:
#           article_date = datetime.strptime(date_text, "%Y.%m.%d %H:%M")
#         except ValueError as e:
#           print(f"Error parsing date: {e}")
#           continue  # 날짜 형식 오류 시 스킵
#
#         if article_date < date_limit:
#           return all_articles  # 오래된 뉴스면 크롤링 종료
#
#         all_articles.append({
#           "title": title_tag.get_text(strip=True),
#           "content": content.get_text(strip=True),
#           "newsUrl": title_tag["href"] if title_tag["href"] else "N/A",
#           "newsThumbnailUrl": img_tag["src"] if img_tag else "N/A",
#           "date": date_text
#         })
#       except Exception as e:
#         print(f"Error parsing article: {e}")
#
#     page += 1
#
#   return all_articles
#
#
# def lambda_handler(event=None, context=None):
#   try:
#     start_time = time.time()
#     articles = fetch_news_articles()
#     end_time = time.time()
#
#     print(f"Crawling completed in {end_time - start_time:.2f} seconds. Articles: {len(articles)}")
#
#     response = {
#       "statusCode": 200,
#       "body": json.dumps(articles, ensure_ascii=False)
#     }
#
#   except Exception as e:
#     response = {
#       "statusCode": 500,
#       "body": json.dumps({"error": str(e)}, ensure_ascii=False)
#     }
#
#   return response
#
