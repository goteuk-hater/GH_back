import requests
from bs4 import BeautifulSoup
from .find_book_img import find_url
from  .find_book_isbn import find_ISBN
from ..models import Book
import requests

BOOK_LIST_API_ROOT = "https://classic.sejong.ac.kr/seletTermBookList.json"

def create_books():

    SejongUNV_API_ROOT = "http://classic.sejong.ac.kr/info/MAIN_02_03.do"
    response = requests.get(SejongUNV_API_ROOT)
    html = response.text

    soup = BeautifulSoup(html, "html.parser") 

    categories = soup.find_all("h4", class_="tit")

    cid = [1000, 2000, 3000, 4000]
    index = 0
    for category in categories:
        books_in_category = category.find_next("ul", class_="book_list").find_all("li")
        form_data = {"opTermId": "TERM-00568", "bkAreaCode" : cid[index]}
        response = requests.post(BOOK_LIST_API_ROOT, data=form_data).json()

        for book, data in zip(books_in_category, response['results']):
            ISBN_API_ROOT = book.find("a").get('href')
            ISBN = find_ISBN(ISBN_API_ROOT)
            ISBN = ISBN.split()
            title = data['bkName']
            author = book.find("span", class_="book_wr").text.strip()
            publisher = book.find("span", class_="book_com").text.strip()
            url = find_url(ISBN[0])

            book_data = {
                "book_code": data['bkCode'],
                "title": title,
                "author": author,
                "publisher": publisher,
                "image_url": url,
                "category_id": cid[index],
            }
            
            Book.objects.create(**book_data)
            
        index += 1