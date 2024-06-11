import requests
import base64
import pandas as pd
import aiohttp
import asyncio

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

def generate_table_script(table_name):
    if table_name == "amazon_products":
        return """
            CREATE TABLE IF NOT EXISTS amazon_products (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                price TEXT,
                link TEXT,
                rating TEXT,
                image TEXT
            );
        """
    elif table_name == "flipkart_products":
        return """
            CREATE TABLE IF NOT EXISTS flipkart_products (
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


