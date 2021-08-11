# 2. Написать программу, которая собирает «Хиты продаж» с сайтов техники М.видео, ОНЛАЙН ТРЕЙД и складывает данные в
# БД. Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары.

# -------------------- M Video --------------------

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions


# function to insert data in the database
def insert_data(data_base, data, col):
    client = MongoClient('localhost', 27017)
    db = client[data_base]
    results = db[col]
    results.insert_one(data)


db = 'parsed_jobs'
collection = 'hits'

# indicate where driver is
path_to_driver = 'd:\Py Projects\chromedriver.exe'
driver = webdriver.Chrome(path_to_driver)

# open browser with target page.
driver.get("https://www.mvideo.ru/")

# load all the top sellers
while True:
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[2]/div/div[3]/div/div[4]/div/div[2]/div/div[1]/a[2]"))).click()

    except exceptions.TimeoutException:
        break

# get the links for each item
hits = driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/div/div[4]/div/div[2]/div/div[1]/div/ul')
links = hits.find_elements_by_css_selector('a.fl-product-tile-title__link.sel-product-tile-title')
links = [i.get_attribute('href') for i in links]

for i in links:
    driver.get(i)

    # retrieve required information
    driver.implicitly_wait(3)
    name = driver.find_element_by_css_selector('div.title-brand.flex.ng-star-inserted h1')
    price = driver.find_element_by_css_selector('p.price__main-value')

    # adjust rating to the same format as for Online Trade
    rate = round(float(driver.find_element_by_xpath('//meta[@itemprop="ratingValue"]').get_attribute('content')))
    reviews = int(driver.find_element_by_xpath('//meta[@itemprop="reviewCount"]').get_attribute('content'))
    if rate == 0 and reviews == 0:
        rating = 'Нет оценок'
    else:
        if rate == 1:
            rating_text = 'звезда'
        elif rate == 5 or rate == 0:
            rating_text = 'звезд'
        else:
            rating_text = 'звезды'

        if (reviews - 1) % 10 != 0 or reviews == 11:
            reviews_text = 'оценкам'
        else:
            reviews_text = 'оценке'
        rating = f'{rate} {rating_text} по {reviews} {reviews_text}'

    # create dictionary to be passed to the database
    data_fields = {
        "Name": name.text,
        "Price": price.text + '₽',
        "Availability": 'NA',   # there is no availability information on Mvideo
        "Rating": rating,
        "Link": driver.current_url
    }

    # call function to insert data
    print(data_fields)
    insert_data(db, data_fields, collection)
driver.close()