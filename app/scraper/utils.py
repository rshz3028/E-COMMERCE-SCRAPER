import requests
import base64
import pandas as pd
import psycopg2

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


def insert_product_to_db(conn, product, table_name):
    cur = conn.cursor()
    try:
        cur.execute(
            f"INSERT INTO {table_name} (title, price, link, rating, image) VALUES (%s, %s, %s, %s, %s);",
            product
        )
        conn.commit()
    except Exception as e:
        print(f"An error occurred during insert: {e}")
        conn.rollback()
    finally:
        cur.close()

def drop_table(conn, table_name):
    try:
        cur = conn.cursor()
        drop_query = f"DROP TABLE IF EXISTS {table_name};"
        cur.execute(drop_query)
        conn.commit()
    except Exception as e:
        print(f"An error occurred during drop: {e}")
        conn.rollback()
    finally:
        cur.close()

def create_table(conn, table_script):
    cur = conn.cursor()
    try:
        cur.execute(table_script)
        conn.commit()
    except Exception as e:
        print(f"An error occurred during create: {e}")
        conn.rollback()
    finally:
        cur.close()

def establish_connection():
    return psycopg2.connect(
        dbname="E-commerce Scraper",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )

def delete_null(conn, table_name):
    cur = conn.cursor()
    try:
        delete_query = f"DELETE FROM {table_name} WHERE title = %s;"
        cur.execute(delete_query, ("No Title",))
        conn.commit()
    except Exception as e:
        print(f"An error occurred during delete: {e}")
        conn.rollback()
    finally:
        cur.close()
