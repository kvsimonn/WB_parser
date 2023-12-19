import time
from fake_useragent import UserAgent
from selenium import webdriver
from parser_one import get_data

async def parse_url(url):
    useragent = UserAgent()
    option = webdriver.ChromeOptions()
    option.add_argument(f"user-agent={useragent.random}")
    driver = webdriver.Chrome(options=option)
    try:
        driver.get(url)
        time.sleep(3)
        res=get_data(driver)
        return res

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

