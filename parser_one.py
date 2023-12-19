from selenium.webdriver.common.by import By

def get_data(driver):
    product_name = driver.find_element(By.TAG_NAME, "h1")
    art = driver.find_element(By.CLASS_NAME, "product-article__copy")
    final_price = driver.find_element(By.CLASS_NAME, "price-block__final-price")
    old_price = driver.find_element(By.CLASS_NAME,"price-block__old-price")
    old_price_for_sale = float(old_price.text.replace(" ", "").replace("₽", ""))
    final_price_for_sale = float(final_price.text.replace(" ", "").replace("₽", ""))
    sale = int(((old_price_for_sale-final_price_for_sale)/old_price_for_sale)*100)
    item = {
        'Название': product_name.text,
        'Цена': final_price.text,
        'Цена без скидки': old_price.text,
        'Артикул': art.text,
        'Скидка': sale
    }
    return item
