# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую
# собранные вакансии в созданную БД.

from pymongo import MongoClient
import pandas as pd
from pprint import pprint
import requests, re
from bs4 import BeautifulSoup as Bs
from fake_headers import Headers

# for this part I will use previously collected data from csv file
df = pd.read_csv('parse_results_jobs.csv')

# convert dataframe to dictionary
dict_jobs = df.to_dict('records')
db = 'parsed_jobs'
collection = 'search_results'


def insert_data(data_base, data, col):
    client = MongoClient('localhost', 27017)
    db = client[data_base]
    results = db[col]
    results.insert_many(data)


insert_data(db, dict_jobs, collection)

# --------------------------------------------------------------------------------------------------------------------
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.

def search_salary(data_base, col, criteria):
    client = MongoClient('localhost', 27017)
    db = client[data_base]
    results = db[col]
    out = results.find({'$or': [{'Min Salary': {'$gt': criteria}}, {'Max Salary': {'$gt': criteria}}]},
                       {'Vacancy name': 1, 'Min Salary': 1, 'Max Salary': 1, 'Vacancy link': 1})
    return out


salary_level = 350000
for i in search_salary(db, collection, salary_level):
    pprint(i)

# --------------------------------------------------------------------------------------------------------------------
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.

# let's get few existing vacancies
df_ex = df.head(10)

# get new vacancies from site. For this I use code from previous lesson

headers = Headers(headers=True).generate()
url = 'https://hh.ru'
search_url = 'https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text='

# Create empty lists for data collection from sites
name, vacancy_link, min_salary, max_salary, source = [], [], [], [], []

title = input('Введите должность: \n')

# reformat input as per site template
title_hh = '+'.join(title.split())


# function to parse head hunter
def parse_hh(soup):
    name.extend([i.text for i in soup.select('span.g-user-content a')])  # get position name
    vacancy_link.extend([i.get('href') for i in soup.select('span.g-user-content a')])  # get position link
    raw_salaries = []  # empty list to process salaries

    # search for all vacancy entries on the site and retrieve salary info from dedicate tag. In case tag is not found
    # salary is not defined
    for i in soup.find_all('div', class_='vacancy-serp-item__row vacancy-serp-item__row_header'):
        res = i.find('div', class_='vacancy-serp-item__sidebar')
        if res is None:
            raw_salaries.append(res)
        else:
            raw_salaries.append(res.text)

    # process entries for found salaries
    for salary in raw_salaries:
        source.append(url)  # on this step website link is added
        if salary is not None:
            salary_trimmed = salary.replace(u'\u202f', '').replace(' ', '')  # clean entries from spaces
            salary_all = re.findall(r"(\d+)", salary_trimmed)  # extract ditis
            if len(salary_all) == 2:  # get data if both min and max salary present
                min_salary.append(int(salary_all[0]))
                max_salary.append(int(salary_all[1]))
            elif salary[:2] == 'от':  # get minimal salary
                min_salary.append(int(salary_all[0]))
                max_salary.append(None)
            elif salary[:2] == 'до':  # get maximal salary
                min_salary.append(None)
                max_salary.append(int(salary_all[0]))
            else:
                min_salary.append(None)
                max_salary.append(None)
        else:
            min_salary.append(None)
            max_salary.append(None)


# get data from site
print(f'Запрос на сайт {url}\n')
response = requests.get(search_url + title_hh, headers=headers)
soup = Bs(response.text, 'html5lib')

# define amount of pages found and ask how may pages to process
if soup.find('span', string='дальше') is None:  # if there is only one page button 'Дальше' will not be present
    max_page = 1
elif soup.find(string='...') is not None:  # if there are more than 5 pages there will be a separator between
    # blocks and max pages will be on seprate block
    max_page = soup.find('span', string='дальше').previous_sibling.findNext('a').findNext('span').text
else:
    max_page = len(soup.find('span', class_='bloko-button-group').contents)

if max_page == 1:
    print(f'Всего найдено страниц с вакансиями - {max_page}\n')
    parse_hh(soup=soup)  # parse only available page
else:
    print(f'Всего найдено страниц с вакансиями - {max_page}\n')
    pages_to_search = int(input('Сколько страниц рассмотреть: \n'))  # ask for amount of pages to process
    while (pages_to_search > int(max_page)) or (pages_to_search == 0):  # create loop to verify input correctness
        print('Введено некоректное число. Пожалуйста повторите.')
        pages_to_search = int(input('Сколько страниц рассмотреть: \n'))
    print(f'Получаем и обрабатываем данные с сайта {url}...\n')
    parse_hh(soup=soup)  # parse first page
    for i in range(1, pages_to_search):  # parse the rest pages
        response = requests.get(search_url + title + '&page=' + str(i), headers=headers)
        soup = Bs(response.text, 'html5lib')
        parse_hh(soup=soup)

# create dictionary to store all found data
data_1 = {
    "Vacancy name": name,
    "Min Salary": min_salary,
    "Max Salary": max_salary,
    "Vacancy link": vacancy_link,
    "Source": source
}
print('Завершено.\n')
# create dataframe
df_new = pd.DataFrame(data_1)
df_new.info()


# merge existing example jobs and new jobs
df_merged = pd.concat([df_ex, df_new], axis=0, ignore_index=True)

source_collection = 'search_results'
target_collection = 'new_search-results'


def new_entries(data_base, col_ex, col_new, df):
    # get all vacancy links from database as unique ID
    client = MongoClient('localhost', 27017)
    db = client[data_base]
    results = db[col_ex]
    links = [i['Vacancy link'] for i in results.find({}, {'_id': 0, 'Vacancy link': 1})]
    df_to_add = df.loc[~df['Vacancy link'].isin(links)]
    dict_jobs = df_to_add.to_dict('records')

    insert_data(data_base, dict_jobs, col_new)


# call function
new_entries(db, source_collection, target_collection, df_merged)