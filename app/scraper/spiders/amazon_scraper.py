import time
import psycopg2
from playwright.sync_api import sync_playwright
from utils import download_image, generate_table_script

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

def scrape_amazon(search_query, max_results=10, show_images=True):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="E-commerce Scraper",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )

        # Create the Amazon products table if it doesn't exist
        create_table(conn, generate_table_script("amazon_products"))

        # Launch a headless browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f'https://www.amazon.com/s?k={search_query}')

            total_results = 0
            while total_results < max_results:
                items = page.query_selector_all('.s-main-slot .s-result-item')
                for item in items:
                    if total_results >= max_results:
                        break
                    title = item.query_selector('h2 .a-link-normal')
                    title_text = title.inner_text() if title else 'No Title'

                    price = item.query_selector('.a-price .a-offscreen')
                    price_text = price.inner_text() if price else 'No Price'

                    link = title.get_attribute('href') if title else 'No Link'

                    rating = item.query_selector('.a-icon-star-small .a-icon-alt')
                    rating_text = rating.inner_text() if rating else 'No Rating'

                    if show_images:
                        image_element = item.query_selector('.s-image')
                        if image_element:
                            image_url = image_element.get_attribute('src')
                            image_data = download_image(image_url)
                            product = (title_text, price_text, link, rating_text, image_data)
                        else:
                            product = (title_text, price_text, link, rating_text, 'No Image')
                    else:
                        product = (title_text, price_text, link, rating_text, '')

                    # Insert the product into the database
                    if product[0] == 'No Title': pass
                    insert_product_to_db(conn, product, "amazon_products")

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
    scrape_amazon(search_query, max_results, show_images)
    end = time.perf_counter()
    print(f"Finished in {round(end-start)}s")