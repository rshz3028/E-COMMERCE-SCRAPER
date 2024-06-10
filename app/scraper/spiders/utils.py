import requests
import base64
import pandas as pd
import aiohttp
import asyncio

async def download_image(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    if 'image' in response.headers.get('Content-Type', ''):
                        image_content = await response.read()
                        return base64.b64encode(image_content).decode('utf-8')
                    else:
                        print(f"URL does not point to an image: {url}")
                        return None
                else:
                    print(f"Failed to fetch image. Status code: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")
        return None
    except asyncio.TimeoutError:
        print(f"Request timed out for URL: {url}")
        return None


def sanitize_filename(filename):
    return filename.replace('/', '_').replace(':', '_').replace('|', '_').replace('*', '_').replace('?', '_').replace('<', '_').replace('>', '_').replace('"', '_')

def save_to_excel(search_query, products):
    df = pd.DataFrame(products, columns=['Title', 'Price', 'Link', 'Rating', 'People Bought', 'Image'])
    df.to_excel(f'{search_query}_results.xlsx', index=False)

def generate_table_script(table_name):
    if table_name == "amazon_products":
        return """
            CREATE TABLE amazon_products (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                price TEXT,
                link TEXT,
                rating TEXT,
                people_bought TEXT,
                image TEXT
            );
        """
    elif table_name == "flipkart_products":
        return """
            CREATE TABLE flipkart_products (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                price TEXT,
                link TEXT,
                rating TEXT,
                image TEXT
            );
        """
    elif table_name == "ebay_products":
        return """
            CREATE TABLE ebay_products (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                price TEXT,
                link TEXT,
                rating TEXT,
                image TEXT
            );
        """
    elif table_name == "etsy_products":
        return """
            CREATE TABLE etsy_products (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                price TEXT,
                link TEXT,
                rating TEXT,
                image TEXT
            );
        """
    else:
        raise ValueError("Invalid table name")


