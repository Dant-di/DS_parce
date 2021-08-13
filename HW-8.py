# В ранее написанное приложение добавить класс с функциями, которые позволят собрать открытые данные по выбранной
# теме при помощи Python с сайта (выберите из списка известных источников данных).

# Data will be collected from https://data.gov.ru.
# For this example the datasets for meteorological data will be retrieved and processed.

import glob
import os
import pandas as pd
from selenium import webdriver
from selenium.common import exceptions


class OpenData:
    def __init__(self, url):
        # set the folder to store downloaded data
        self.options = webdriver.ChromeOptions()
        self.prefs = {"download.default_directory": "d:\Py Projects\Web_Parcing\Lesson_8\\"}
        self.options.add_experimental_option("prefs", self.prefs)

        # indicate where driver is
        self.path_to_driver = 'd:\Py Projects\chromedriver.exe'
        self.driver = webdriver.Chrome(self.path_to_driver, options=self.options)

        # open browser with target page.
        self.driver.get(url)

        # get the links to pages with datasets
        self.links = self.driver.find_elements_by_css_selector('div.field-item.even h2 a')
        self.links = [i.get_attribute('href') for i in self.links]

        # open links and download files, skipping pages with no download links
        for i in self.links:
            try:
                self.driver.get(i)
                self.urls = self.driver.find_element_by_xpath(
                    '//*[@class="multi-download-link-wrapper"]/div[2]/div/a').get_attribute('href')
                self.driver.get(self.urls)
            except exceptions.NoSuchElementException:
                continue

        self.driver.close()

    def process_data(self):

        # get all the downloaded csv files
        file_list = glob.glob('*.csv')

        # create folder to store processed datasets
        os.mkdir('cleaned')
        for file in file_list:
            df = pd.read_csv(file, encoding='cp1251')
            df_cleaned = df.dropna(axis=1, how='all')   # remove columns without data in it
            df_cleaned.to_csv('cleaned/cleaned_' + file, index=False, encoding='cp1251')


data = OpenData("https://data.gov.ru/taxonomy/term/1889/datasets")
data.process_data()
