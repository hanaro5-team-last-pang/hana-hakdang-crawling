import requests
from bs4 import BeautifulSoup
import json

def crawl_finance_articles(url):
  response = requests.get(url)
  if response.status_code != 200:
    return None

  soup = BeautifulSoup(response.text, 'html.parser')

  articles = soup.select('div.view-cont')  # Updated selector

  data = []

  for article in articles:
    try:
      title = article.select_one('h4.titles a').get_text(strip=True)
      summary = article.select_one('p.lead').get_text(strip=True)
      img_tag = article.find_previous_sibling('a').find('img')
      img_url = img_tag['src'] if img_tag else None
      em_elements = article.select('span.byline em')  # 모든 <em> 태그를 리스트로 가져옴
      if len(em_elements) >= 3:  # 세 번째 요소가 존재하는지 확인
        date = em_elements[2].get_text(strip=True)  # 리스트의 세 번째 요소 (인덱스 2) 가져오기
      else:
        date = None  # 세 번째 <em> 태그가 없을 경우 처리
      # date = article.select_one('span.byline em').get_text(strip=True)
      data.append({
        'title': title,
        'summary': summary,
        'image_url': img_url,
        'date':date
      })
    except Exception as e:
      print(f"Error parsing: {e}")

  return json.dumps(data, ensure_ascii=False, indent=4)

url = "https://www.fetimes.co.kr/news/articleList.html?page=1&total=60351&sc_section_code=S1N16&view_type=sm"
articles_json = crawl_finance_articles(url)

if articles_json:
  print(articles_json)

  with open("finance_articles.json", "w", encoding="utf-8") as file:
    file.write(articles_json)
