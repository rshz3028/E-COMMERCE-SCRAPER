import asyncio
from spiders import scrape_amazon, scrape_flipkart, scrape_ebay, scrape_etsy

async def main():
    your_search_query = input("Enter your search query: ")
    max_results = int(input("How many products do you want? "))
    imageShow = input("Show images? (y/n)").lower()
    if imageShow == 'n':
        imageShow = False

    # Dictionary to store the product lists
    products_dict = {}

    # Scrape data from all sources
    products_dict['amazon'] = await scrape_amazon(your_search_query, max_results, imageShow)
    products_dict['flipkart'] = await scrape_flipkart(your_search_query, max_results, imageShow)
    products_dict['ebay'] = await scrape_ebay(your_search_query, max_results, imageShow)
    products_dict['etsy'] = await scrape_etsy(your_search_query, max_results, imageShow)

    # Access the product lists from the dictionary
    print("Amazon Products:")
    for product in products_dict['amazon']:
        print(product)
    print()

    print("Flipkart Products:")
    for product in products_dict['flipkart']:
        print(product)
    print()

    print("eBay Products:")
    for product in products_dict['ebay']:
        print(product)
    print()

    print("Etsy Products:")
    for product in products_dict['etsy']:
        print(product)
    print()

asyncio.run(main())
