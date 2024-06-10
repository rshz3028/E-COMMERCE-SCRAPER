from playwright.sync_api import sync_playwright

def scrape_flipkart_laptops():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Set headless to False to see browser actions
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to Flipkart
        page.goto('https://www.flipkart.com')
        
        # Attempt to close the login popup if it appears
        try:
            page.wait_for_selector('button._2KpZ6l._2doB4z', timeout=5000)
            page.click('button._2KpZ6l._2doB4z')
            print('Closed login popup')
        except Exception as e:
            print('Login popup did not appear:', e)

        # Perform a search for laptops
        search_query = 'laptop'
        page.fill('input[name="q"]', search_query)
        page.press('input[name="q"]', 'Enter')
        
        # Wait for the results to load
        page.wait_for_selector('div._1YokD2._3Mn1Gg')
        
        # Extract product names and prices
        products = page.evaluate('''() => {
            const items = document.querySelectorAll('div._1AtVbE');
            const data = [];
            items.forEach(item => {
                const nameElement = item.querySelector('a.IRpwTa') || item.querySelector('a._2WkVRV');
                const priceElement = item.querySelector('div._30jeq3');
                if (nameElement && priceElement) {
                    const name = nameElement.textContent;
                    const price = priceElement.textContent;
                    data.push({ name, price });
                }
            });
            return data;
        }''')
        
        # Display product names and prices
        if products:
            print('Laptop Products:')
            for index, product in enumerate(products):
                print(f"{index + 1}. Name: {product['name']}, Price: {product['price']}")
        else:
            print('No products found.')

        # Close the browser
        browser.close()

# Run the scraper
scrape_flipkart_laptops()
