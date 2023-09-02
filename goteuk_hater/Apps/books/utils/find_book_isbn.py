import requests
from bs4 import BeautifulSoup
import find_book_img

def find_ISBN(url):
    response = requests.get(url, verify=False)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    tds = soup.find_all("td", class_="detailBody")
    print(tds)
    
    if not tds:
        return "None"
    return tds[-2].text

