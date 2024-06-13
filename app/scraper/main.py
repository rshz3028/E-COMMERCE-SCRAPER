# main.py
import multiprocessing
from app.amazon_scraper import scrape_amazon
from spiders.flipkart_scraper import scrape_flipkart

if __name__ == '__main__':
    search_query = input("Enter the item: ")
    max_results = 10
    show_images = True

    amazon_process = multiprocessing.Process(target=scrape_amazon, args=(search_query, max_results, show_images))
    flipkart_process = multiprocessing.Process(target=scrape_flipkart, args=(search_query, max_results, show_images))

    amazon_process.start()
    flipkart_process.start()

    amazon_process.join()
    flipkart_process.join()
