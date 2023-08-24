import requests
from bs4 import BeautifulSoup


SejongUNV_API_ROOT = "http://classic.sejong.ac.kr/info/MAIN_02_03.do"
response = requests.get(SejongUNV_API_ROOT)
html = response.text

soup = BeautifulSoup(html, "html.parser") 

categories = soup.find_all("h4", class_="tit")
post_api_url = "http://127.0.0.1:8000/books/book_data"

category_index = 1
index = 1
for category in categories:
    books_in_category = category.find_next("ul", class_="book_list").find_all("li")

    for i, book in enumerate(books_in_category):
        title = book.find("span", class_="book_tit").text.strip()
        author = book.find("span", class_="book_wr").text.strip()
        publisher = book.find("span", class_="book_com").text.strip()

        book_data = {
            "id": index,
            "title": title,
            "author": author,
            "publisher": publisher,
            "category": category_index
        }
        
        response = requests.post(post_api_url, json=book_data)  # json으로 변경
        print(response.content)
        index += 1
    category_index += 1