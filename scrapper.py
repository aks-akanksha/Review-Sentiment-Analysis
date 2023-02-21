import requests
from bs4 import BeautifulSoup
import re

def scrape_product(url):
    # Send a request to the product page
    response = requests.get(url)
    # Parse the HTML content of the response
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the product name
    name_element = soup.find('h1', {'class': 'product-name'})
    if name_element:
        name = name_element.text.strip()
    else:
        name = None
    # Find the product price
    price_element = soup.find('span', {'class': 'post-card__content-price-offer'})
    if price_element:
        price = price_element.text.strip()
    else:
        price = None
    # Find the product brand
    brand_element = soup.find('h2', {'class': 'product-brand'})
    if brand_element:
        brand = brand_element.text.strip()
    else:
        brand = None
    # Find the reviews section of the page
    reviews_section = soup.find('div', {'id': 'customer-review'})
    # Check if the reviews section is present on the page
    if reviews_section:
        # Find the total number of pages of reviews
        pagination = reviews_section.find('div', {'class': 'pagination'})
        num_pages = 1
        if pagination:
            page_links = pagination.find_all('a')
            if page_links:
                last_page_link = page_links[-2]
                num_pages = int(last_page_link.text)
        # Loop through each page of reviews
        all_reviews = []
        for page in range(1, num_pages+1):
            page_url = url + '?pageNumber={}'.format(page)
            page_response = requests.get(page_url)
            page_soup = BeautifulSoup(page_response.content, 'html.parser')
            page_reviews = page_soup.find_all('div', {'class': 'content-section review-section'})
            # Extract the review text and rating for each review
            for review in page_reviews:
                text_element = review.find('div', {'class': 'content'}).find('div', {'class': 'text'}).find('div', {'class': 'review-text'})
                rating_element = review.find('div', {'class': 'content'}).find('div', {'class': 'rating-stars'})
                if text_element and rating_element:
                    text = text_element.text.strip()
                    rating = rating_element.attrs['style']
                    rating = int(re.search(r'\d+', rating).group())
                    # Append the review to the list of all reviews
                    all_reviews.append({'text': text, 'rating': rating})
        # Create a dictionary for the product with its name, price, brand, and reviews
        product_dict = {
            'name': name,
            'price': price,
            'brand': brand,
            'reviews': all_reviews
        }
        return product_dict
    else:
        return None

def scrape_products(urls):
    all_products = []
    for url in urls:
        product = scrape_product(url)
        if product:
            all_products.append(product)
    return all_products

# Example usage
products = ['https://www.nykaa.com/nykaa-so-creme-creamy-matte-lipstick/p/683166?productId=683166&pps=1&skuId=683163', 
            'https://www.nykaa.com/maybelline-new-york-color-sensational-creamy-matte-lipsticks/p/353926?productId=353926&pps=2&skuId=116400', 
            'https://www.nykaa.com/lakme-forever-matte-liquid-lip-colour/p/623306?productId=623306&pps=12&skuId=746109']
all_product_dicts = []
for product_url in products:
    product_dict = scrape_product(product_url)
    if product_dict:
        print('Scraped data for {} - {}'.format(product_dict['brand'], product_dict['name']))
        all_product_dicts.append(product_dict)
    else:
        print('No data found for {}'.format(product_url))
