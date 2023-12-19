from selenium.webdriver.common.by import By

url_c= 'https://www.wildberries.ru/catalog/novyy-god/karnavalnye-tovary/karnavalnye-aksessuary'
def get_data_category(driver):
    product_names = driver.find_elements(By.CLASS_NAME, "product-card__name")
    final_prices = driver.find_elements(By.CLASS_NAME, "price__lower-price")
    old_prices = driver.find_elements(By.TAG_NAME, "del")
    sales = driver.find_elements(By.CLASS_NAME, "product-card__tip.product-card__tip--sale")
    item ={}
    products = []
    for i in range(len(product_names)):
        item = {
            'product_name': product_names[i].text,
            'final_price': final_prices[i].text,
            'old_price': old_prices[i].text,
            'sale': sales[i].text if i < len(sales) else ""
        }
        products.append(item)
    return products

# def parse_pages(url):
