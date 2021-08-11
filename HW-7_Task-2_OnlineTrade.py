# 2. Написать программу, которая собирает «Хиты продаж» с сайтов техники М.видео, ОНЛАЙН ТРЕЙД и складывает данные в
# БД. Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары.


# -------------------- Online Trade --------------------

from pymongo import MongoClient
from selenium import webdriver


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
driver.get("https://www.onlinetrade.ru/")

# get all the links for the hits goods
links = driver.find_elements_by_css_selector('#tabs_hits a.indexGoods__item__image')
links = [i.get_attribute('href') for i in links]

for i in links:
    driver.get(i)

    # retrieve required information
    name = driver.find_element_by_tag_name('h1')
    price = driver.find_element_by_css_selector('.js__actualPrice')
    availability = driver.find_element_by_css_selector('.catalog__displayedItem__availabilityCount')
    rating = driver.find_element_by_css_selector('.starsSVG').get_attribute('title')

    # create dictionary to be passed to the database
    data_fields = {
        "Name": name.text,
        "Price": price.text,
        "Availability": availability.text,
        "Rating": rating,
        "Link": driver.current_url
    }

    # call function to insert data
    print(data_fields)
    insert_data(db, data_fields, collection)

driver.close()