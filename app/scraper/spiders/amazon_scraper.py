import asyncio
from playwright.async_api import async_playwright
from utils import download_image, generate_table_script
import asyncpg

async def insert_product_to_db(conn, product, table_name):
    async with conn.transaction():
        await conn.execute(
            f"INSERT INTO {table_name} (title, price, link, rating, people_bought, image) VALUES ($1, $2, $3, $4, $5, $6);",
            *product
        )

async def create_table(conn, table_script):
    async with conn.transaction():
        await conn.execute(table_script)

async def scrape_amazon(search_query, max_results=10, show_images=True):
    # Connect to the PostgreSQL database
    conn = await asyncpg.connect(
        database="E-commerce Scraper",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )

    # Create the Amazon products table if it doesn't exist
    await create_table(conn, generate_table_script("amazon_products"))

    # Launch a headless browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'https://www.amazon.com/s?k={search_query}')

        total_results = 0
        while total_results < max_results:
            items = await page.query_selector_all('.s-main-slot .s-result-item')
            for item in items:
                if total_results >= max_results:
                    break
                title = await item.query_selector('h2 .a-link-normal')
                title_text = await title.inner_text() if title else 'No Title'

                price = await item.query_selector('.a-price .a-offscreen')
                price_text = await price.inner_text() if price else 'No Price'

                link = await title.get_attribute('href') if title else 'No Link'

                rating = await item.query_selector('.a-icon-star-small .a-icon-alt')
                rating_text = await rating.inner_text() if rating else 'No Rating'

                people_bought = await item.query_selector('.a-size-small .a-color-secondary')
                people_bought_text = await people_bought.inner_text() if people_bought else 'Unknown'

                if show_images:
                    image_element = await item.query_selector('.s-image')
                    if image_element:
                        image_url = await image_element.get_attribute('src')
                        image_data = await download_image(image_url)
                        product = (title_text, price_text, link, rating_text, people_bought_text, image_data)
                    else:
                        product = (title_text, price_text, link, rating_text, people_bought_text, 'No Image')
                else:
                    product = (title_text, price_text, link, rating_text, people_bought_text, '')

                # Insert the product into the database
                await insert_product_to_db(conn, product, "amazon_products")

                total_results += 1
            if total_results < max_results:
                await page.wait_for_load_state('networkidle')
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('networkidle')

        await browser.close()
        await conn.close()

if __name__ == '__main__':
    search_query = input("Enter the item: ")
    asyncio.run(scrape_amazon(search_query, max_results=10, show_images=True))
    print("Finished")