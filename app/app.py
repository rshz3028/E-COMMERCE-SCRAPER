from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import subprocess
import time

app = Flask(__name__)

def get_products_from_db():
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

    formatted_products = []
    for product in products:
        title, price, link, rating, image = product
        if not link.startswith('http'):
            link = f'https://www.amazon.com{link}'
        formatted_products.append((title, price, link, rating, image))

    return formatted_products

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    product_name = request.form['product_name']
    
    # Trigger scrapers (update these lines to match your actual scraper commands)
    subprocess.Popen(["python", "spiders/amazon_scraper.py", product_name])
    
    # Give some time for scrapers to fetch data (adjust as needed)
    time.sleep(50)
    
    return redirect(url_for('index'))

@app.route('/products')
def index():
    products = get_products_from_db()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
