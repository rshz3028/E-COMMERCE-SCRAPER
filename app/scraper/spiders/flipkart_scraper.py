import time
import psycopg2
import requests
import base64
from playwright.sync_api import sync_playwright
from utils import generate_table_script

def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            if 'image' in response.headers.get('Content-Type', ''):
                image_content = response.content
                return base64.b64encode(image_content).decode('utf-8')
            else:
                print(f"URL does not point to an image: {url}")
                return None
        else:
            print(f"Failed to fetch image. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def insert_product_to_db(conn, product, table_name):
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO {table_name} (title, price, link, rating, image) VALUES (%s, %s, %s, %s, %s);",
            product
        )
        conn.commit()

def create_table(conn, table_script):
    with conn.cursor() as cur:
        cur.execute(table_script)
        conn.commit()

def scrape_flipkart(search_query, max_results=10, show_images=True):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="E-commerce Scraper",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )

        # Create the Flipkart products table if it doesn't exist
        create_table(conn, generate_table_script("flipkart_products"))

        # Launch a headless browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f'https://www.flipkart.com/search?q={search_query}')

            total_results = 0
            while total_results < max_results:
                items = page.query_selector_all('.DOjaWF .LFEi7Z')
                for item in items:
                    if total_results >= max_results:
                        break
                    title = item.query_selector('.col-7-12 .KzDlHZ')
                    title_text = title.inner_text() if title else 'No Title'

                    price = item.query_selector('.col-5-12 ._4b5DiR')
                    price_text = price.inner_text() if price else 'No Price'

                    link = item.get_attribute('.tUxRFH .CGtC98') if title else 'No Link'

                    rating = item.query_selector('._5OesEi .XQDdHH')
                    rating_text = rating.inner_text() if rating else 'No Rating'

                    if show_images:
                        image_element = item.query_selector('img.DByuf4')
                        if image_element:
                            image_url = image_element.get_attribute('src')
                            image_data = download_image(image_url)
                            product = (title_text, price_text, link, rating_text, image_data)
                        else:
                            product = (title_text, price_text, link, rating_text, 'No Image')
                    else:
                        product = (title_text, price_text, link, rating_text, '')

                    # Insert the product into the database
                    if product[0] == "No Title": pass
                    insert_product_to_db(conn, product, "flipkart_products")

                    total_results += 1
                if total_results < max_results:
                    page.wait_for_load_state('networkidle')
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_load_state('networkidle')

            browser.close()

    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    start = time.perf_counter()
    search_query = input("Enter the product name: ")
    max_results = 10
    show_images = True
    scrape_flipkart(search_query, max_results, show_images)
    end = time.perf_counter()
    print(f"Finished in {round(end-start)}s")
