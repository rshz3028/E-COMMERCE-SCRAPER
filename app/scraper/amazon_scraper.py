import sys
import time
import psycopg2
from playwright.sync_api import sync_playwright
from .utils import download_image, generate_table_script, insert_product_to_db, drop_table, create_table, establish_connection, delete_null

def scrape_amazon(search_query, max_results=11, show_images=True):
    conn = None
    try:
        conn = establish_connection()
        if conn is None:
            raise Exception("Failed to connect to the database")

        drop_table(conn, "amazon_products")
        create_table(conn, generate_table_script("amazon_products"))

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
                    title_element = item.query_selector('h2 .a-link-normal')
                    title_text = title_element.inner_text() if title_element else 'No Title'

                    price_element = item.query_selector('.a-price .a-offscreen')
                    price_text = price_element.inner_text() if price_element else 'No Price'

                    link = title_element.get_attribute('href') if title_element else 'No Link'

                    rating_element = item.query_selector('.a-icon-star-small .a-icon-alt')
                    rating_text = rating_element.inner_text() if rating_element else 'No Rating'

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

                    insert_product_to_db(conn, product, "amazon_products")
                    total_results += 1

                if total_results < max_results:
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_load_state('networkidle')

            browser.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            delete_null(conn, "amazon_products")
            conn.close()

if __name__ == '__main__':
    start = time.perf_counter()
    if len(sys.argv) > 1:
        search_query = sys.argv[1]
        scrape_amazon(search_query)
    else:
        print("Please provide a search query.")
    end = time.perf_counter()
    print(f"Finished in {round(end - start, 2)} seconds")
