import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

# TODO: 백엔드 서버와 연동
def fetch_news_articles(base_url, days_limit):
  all_articles = []
  today = datetime.now()
  date_limit = today - timedelta(days=days_limit)
  page = 1

  while True:
    url = f"{base_url}&page={page}"
    print(f"페이지 크롤링 중: {page}, URL: {url}")
    response = requests.get(url)

    if response.status_code != 200:
      print(f"페이지 {page} 요청 실패: HTTP 상태 코드 {response.status_code}")
      break

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.select('div.view-cont')

    if not articles:
      print(f"페이지 {page}에서 기사를 찾을 수 없습니다. 크롤링을 종료합니다.")
      break

    for article in articles:
      try:
        title = article.select_one('h4.titles a')
        summary = article.select_one('p.lead')
        img_tag = article.find_previous_sibling('a').find('img') if article.find_previous_sibling('a') else None
        em_elements = article.select('span.byline em')

        # 데이터 유효성 검사
        if not title or not summary or not img_tag or len(em_elements) < 3:
          print("불완전한 기사 데이터가 발견되었습니다. 해당 기사를 건너뜁니다.")
          continue

        date_text = em_elements[2].get_text(strip=True)
        try:
          article_date = datetime.strptime(date_text, "%Y.%m.%d %H:%M")
          if article_date < date_limit:
            print("기사가 기준 날짜보다 오래되었습니다. 크롤링을 종료합니다.")
            return all_articles
        except ValueError:
          print(f"날짜 형식이 올바르지 않습니다: {date_text}")
          continue

        all_articles.append({
          'title': title.get_text(strip=True),
          'summary': summary.get_text(strip=True),
          'image_url': img_tag['src'] if img_tag else "N/A",
          'date': date_text
        })
      except Exception as e:
        print(f"기사 파싱 중 오류 발생: {e}")

    page += 1

  return all_articles

def save_to_file(data, filename):
  try:
    with open(filename, "w", encoding="utf-8") as file:
      json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"데이터가 저장되었습니다: {filename}")
  except Exception as e:
    print(f"파일 저장 중 오류 발생: {e}")

# 기본 URL 및 날짜 범위 설정
base_url = "https://www.fetimes.co.kr/news/articleList.html?sc_section_code=S1N16&view_type=sm"
days_limit = 30  # 최근 30일 기준

# 뉴스 데이터 가져오기 및 저장
news_data = fetch_news_articles(base_url, days_limit)

if news_data:
  save_to_file(news_data, "finance_articles.json")
else:
  print("기사를 찾을 수 없습니다.")
