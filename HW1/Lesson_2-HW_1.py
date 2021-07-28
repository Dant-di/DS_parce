import requests, lxml, re
import pandas as pd
from bs4 import BeautifulSoup as Bs
from fake_headers import Headers

headers = Headers(headers=True).generate()

url = 'https://hh.ru'
search_url = 'https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text='

url_2 = 'https://www.superjob.ru/'
search_url_2 = 'https://www.superjob.ru/vacancy/search/?keywords='

# Create empty lists for data collection from sites
name, vacancy_link, min_salary, max_salary, source = [], [], [], [], []
name_2, vacancy_link_2, min_salary_2, max_salary_2, source_2 = [], [], [], [], []

title = input('Введите должность: \n')

# head hunter
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
if soup.find('span', string='дальше') is None:    # if there is only one page button 'Дальше' will not be present
    max_page = 1
elif soup.find(string='...') is not None:    # if there are more than 5 pages there will be a separator between
                                             # blocks and max pages will be on seprate block
    max_page = soup.find('span', string='дальше').previous_sibling.findNext('a').findNext('span').text
else:
    max_page = len(soup.find('span', class_='bloko-button-group').contents)

if max_page == 1:
    print(f'Всего найдено страниц с вакансиями - {max_page}\n')
    parse_hh(soup=soup)  # parse only available page
else:
    print(f'Всего найдено страниц с вакансиями - {max_page}\n')
    pages_to_search = int(input('Сколько страниц рассмотреть: \n'))    # ask for amount of pages to process
    while (pages_to_search > int(max_page)) or (pages_to_search == 0):    # create loop to verify input correctness
        print('Введено некоректное число. Пожалуйста повторите.')
        pages_to_search = int(input('Сколько страниц рассмотреть: \n'))
    print(f'Получаем и обрабатываем данные с сайта {url}...\n')
    parse_hh(soup=soup)     # parse first page
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
df_1 = pd.DataFrame(data_1)
df_1.info()


# SuperJob

# function to parse head hunter
def parse_sj(soup):
    name_2.extend([i.text for i in soup.select('._1h3Zg._2rfUm._2hCDz._21a7u ._2JivQ ')])   # get position name
    vacancy_link_2.extend([i.get('href') for i in soup.select('div._1h3Zg._2rfUm._2hCDz._21a7u a')]) # get position link
    raw_salaries = [i.text for i in soup.select('._1h3Zg._2Wp8I._2rfUm._2hCDz._2ZsgW')]     # get salaries

# process salaries
    for salary in raw_salaries:
        source_2.append(url)
        salary_trimmed = salary.replace(u'\xa0', '')    # replace spaces
        salary_all = re.findall(r"(\d+)", salary_trimmed)   # extract digits
        if len(salary_all) == 2:    # get data if both salaries are present
            min_salary_2.append(int(salary_all[0]))
            max_salary_2.append(int(salary_all[1]))
        elif salary[:2] == 'от':    # get minimal salary
            min_salary_2.append(int(salary_all[0]))
            max_salary_2.append(None)
        elif salary[:2] == 'до':    # get maximal salary
            min_salary_2.append(None)
            max_salary_2.append(int(salary_all[0]))
        else:
            min_salary_2.append(None)
            max_salary_2.append(None)


# get data from site
print(f'Запрос на сайт {url_2}\n')
response = requests.get(search_url_2 + title, headers=headers)
soup = Bs(response.text, 'html5lib')

# define amount of pages found and ask how may pages to process
if soup.find('span', class_='_1BOkc', string='Дальше') is None:     # if only one page found
    max_page = 1
else:   # if there are several pages look into the previosu block from button 'Дальше'
    max_page = soup.find('a', class_='f-test-link-Dalshe').previous_sibling.findNext('span').text

if max_page == 1:
    print(f'Всего найдено страниц с вакансиями - {max_page}\n')
    parse_sj(soup=soup)  # parse only available page
else:
    print(f'Всего найдено страниц с вакансиями - {max_page}\n')
    pages_to_search = int(input('Сколько страниц рассмотреть: \n')) # ask for amount of pages to process
    while (pages_to_search > int(max_page)) or (pages_to_search == 0): # create loop to verify input correctness
        print('Введено некоректное число. Пожалуйста повторите.')
        pages_to_search = int(input('Сколько страниц рассмотреть: \n'))
    print(f'Получаем и обрабатываем данные с сайта {url_2}...\n')
    parse_sj(soup=soup)     # parse first page
    for i in range(1, pages_to_search):     # parse the rest pages
        response = requests.get(search_url_2 + title + '&page=' + str(i), headers=headers)
        soup = Bs(response.text, 'html5lib')
        parse_sj(soup=soup)

# create dictionary with data
data_2 = {
    "Vacancy name": name_2,
    "Min Salary": min_salary_2,
    "Max Salary": max_salary_2,
    "Vacancy link": vacancy_link_2,
    "Source": source_2
}

print('Завершено.\n')
# create data frame
df_2 = pd.DataFrame(data_2)
df_2.info()

# merge two dataframes into resulting one
parse_results = pd.concat([df_1, df_2], axis=0, ignore_index=True)

# save data to file
file_name = 'parse_results_jobs.pkl'
parse_results.to_pickle(file_name)
print(f'Данные сохранены в {file_name}')
