from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

def get_products_from_db():
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(
        dbname="E-commerce Scraper",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT title, price, link, rating, image FROM amazon_products")
    products = cur.fetchall()
    cur.close()
    conn.close()

    # Ensure links are absolute URLs
    formatted_products = []
    for product in products:
        title, price, link, rating, image = product
        if not link.startswith('http'):
            link = f'https://www.amazon.com{link}'
        formatted_products.append((title, price, link, rating, image))

    return formatted_products

@app.route('/')
def index():
    products = get_products_from_db()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
