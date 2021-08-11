# 1. Написать программу, которая собирает входящие письма из своего или тестового почтового ящика, и сложить
# информацию о письмах в базу данных (от кого, дата отправки, тема письма, текст письма).


from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys


# function to insert data in the database
def insert_data(data_base, data, col):
    client = MongoClient('localhost', 27017)
    db = client[data_base]
    results = db[col]
    results.insert_one(data)


db = 'parsed_jobs'
collection = 'mail'

# indicate where driver is
path_to_driver = 'd:\Py Projects\chromedriver.exe'
driver = webdriver.Chrome(path_to_driver)

# open browser with target page. For this task I created temporary email, so no security concerns =)
driver.get("https://tempr.email/en/")

driver.find_element_by_id('LoginLocalPart').send_keys('gb_hw_7')
Select(driver.find_element_by_id('LoginDomainId')).select_by_visible_text('geekpro.org (PW)')
driver.find_element_by_id('LoginPassword').send_keys('7850524')
driver.find_element_by_name('LoginButton').click()

# let some time page to load
driver.implicitly_wait(5)

# get all links to mails in the inbox
links = driver.find_elements_by_css_selector('.Head a')
links = [i.get_attribute('href') for i in links]

# open each mail
for i in links:
    driver.get(i)

    # switch to text mode of mail representation
    driver.find_element_by_css_selector('.SectionContent a.TabButton').click()

    # retrieve required information. This section also contains Recipient, so this element will be skipped
    message_details = driver.find_elements_by_css_selector('div.MessageDetails div.Value')
    sender = message_details[1].text.split(' ')[0]
    date = message_details[2].text
    subject = message_details[3].text
    body = driver.find_element_by_id('MessageContent').text

    # create dictionary to be passed to the database
    data_fields = {
        "Sender": sender,
        "Sent on": date,
        "Subject": subject,
        "Message text": body
    }

    # call function to insert data
    insert_data(db, data_fields, collection)

# close browser window
driver.close()









# create dictionary
