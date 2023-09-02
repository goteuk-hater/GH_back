# var _usedOpenMarketItemIdCol = '16812,2247659';
# https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=16812
import requests
from bs4 import BeautifulSoup

def find_url(book_name, author):
    BOOK_ID_API_ROOT = "https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=Book&SearchWord="
    BOOK_IMG_API_ROOT = "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId="


    remove_index = author.index('(')
    parameter = book_name + ',' + author[:remove_index]

    response = requests.get(BOOK_ID_API_ROOT+parameter)
    html = response.text

    # books_in_category = category.find_next("ul", class_="book_list").find_all("li")
    soup = BeautifulSoup(html, "html.parser") 
    result = soup.find_all("script", type="text/javascript")
    id = soup.find("_usedOpenMarketItemIdCol")
    ids = ''
    for script in result:
        content = script.string
        if content:
            start_index = content.find('_usedOpenMarketItemIdCol')
            if start_index != -1:
                end_index = content[start_index:].find(';')
                ids = content[start_index + 27 : start_index + end_index]
                break

    if ',' in ids:
        end = ids.index(',')
        ids = ids[1:end]
    else:
        ids = ids[1:len(ids)-1]

    response = requests.get(BOOK_IMG_API_ROOT+ids)
    html = response.text

    soup = BeautifulSoup(html, "html.parser") 
    result = soup.find("meta", property="og:image")
    if result == None:
        return 'None'

    return result['content']
# categories = soup.find_all("h4", class_="tit")
# post_api_url = "http://127.0.0.1:8000/books/book_data"
