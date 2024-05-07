from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
from config import email, password, website_url, search_word


def login(driver, email, password):
    email_input = driver.find_element(By.NAME, 'login[username]')
    email_input.clear()  
    email_input.send_keys(email)

    pass_input = driver.find_element(By.NAME, 'login[password]')
    pass_input.clear()
    pass_input.send_keys(password)

    #cookie
    cookie_notice = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "notice-cookie-block")))
    allow_cookies_button = cookie_notice.find_element(By.ID, "btn-cookie-allow")
    allow_cookies_button.click()

    #button
    time.sleep(3)
    sign_in_button = driver.find_element(By.ID, "send2")
    driver.execute_script("arguments[0].click();", sign_in_button)
    time.sleep(3)

# search and scrape
def search_and_scrape(driver, search_word):
    search_input = driver.find_element(By.NAME, 'q')
    search_input.send_keys(search_word)
    search_input.send_keys(Keys.RETURN)

    # item_data = {
    #     "title": [],
    #     "sku_code": [],
    #     "product_barcode": [],
    #     "pack_qty": [],
    #     "price": []
    # }
    titles, sku_codes, product_barcodes, pack_qtys, prices = [], [], [], [],[]

    while True:

        main_page_source = BeautifulSoup(driver.page_source, 'html.parser')
        product_links = main_page_source.find_all(class_="product-item-link")

        for link in product_links:
            driver.execute_script("window.open(arguments[0]);", link["href"])
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[-1])

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                title = soup.find('h1', class_='page-title').text.strip()
                sku_code = soup.find(class_='value attribute-code-sku').text.strip()
                product_barcode = soup.find(class_='attribute-code-product_barcode').text.strip()
                pack_qty = soup.find(class_='pack-qty-box').text.strip()
                price = soup.find(class_='price-wrapper').text.strip()

                titles.append(title)
                sku_codes.append(sku_code)
                product_barcodes.append(product_barcode)
                pack_qtys.append(pack_qty)
                prices.append(price)

                df = pd.DataFrame({
                    'Product title': titles,
                    'sku_codes': sku_codes,
                    'product_barcodes': product_barcodes,
                    'pack_qtys': pack_qtys,
                    'price':prices})    
                df.to_csv('data.csv', mode='a', index=False, header=True)

                # df = pd.DataFrame(item_data)
                    
            except Exception as e:
                print("Error:", e)

            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

        try:
            popup_close_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "close_btn")))
            popup_close_button.click()

            next_page_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.item.pages-item-next a")))
            next_page_link.click()

        except NoSuchElementException:
            print("Next button not found.")
            break


if __name__ == "__main__":

    driver = webdriver.Chrome()
    driver.get(website_url)

    login(driver, email, password)
    search_and_scrape(driver, search_word)

    driver.quit()
