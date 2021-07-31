import requests
from lxml import html
import pandas as pd
from fake_headers import Headers
from datetime import datetime, timedelta
from pymongo import MongoClient

header = Headers(headers=True).generate()
url_1 = 'https://lenta.ru'
url_2 = 'https://yandex.ru/news'
url_3 = 'https://news.mail.ru'

# Lenta.ru
response = requests.get(url_1, headers=header)
parsed = html.fromstring(response.text)
headlines_raw = parsed.xpath('//*[@class="item news b-tabloid__topic_news"]/a/h3/text()') # get headlines
links_raw = parsed.xpath('//*[@class="item news b-tabloid__topic_news"]/a/@href') # get links fro headlines


# refine links and title, removing news from external sources
headlines_1 = []
date_1 = []
links_1 = []
source_1 = []

for i in links_raw:
    if 'https:' in i: # external news have full url. We skip such news
        continue
    else:
        links_1.append(url_1+i) # add main url to parsed links
        headlines_1.append(headlines_raw[links_raw.index(i)]) # add respective headline to the list
        source_1.append(url_1) # add main source
headlines_1 = [i.replace('\xa0', ' ') for i in headlines_1] # remove non-breaking spaces


# date will be retrieved from the article itself
for i in links_1:
    response = requests.get(i, headers=header)
    parsed = html.fromstring(response.text)
    temp_date = parsed.xpath('//*[@class="g-date"]/@datetime') # get date from the attribute
    date_1.append(datetime.strptime(temp_date[0], '%Y-%m-%dT%H:%M:%S%z').strftime('%d %b %Y at %H:%M')) # convert date to desired format


# create dictionary
data_1 = {
    "Headline": headlines_1,
    "Publish date": date_1,
    "News link": links_1,
    "Source": source_1
}

#create dataframe
df_lenta = pd.DataFrame(data_1)


# function to add data in database
def insert_data(data_base, data, col):
    client = MongoClient('localhost', 27017)
    db = client[data_base]
    results = db[col]
    results.insert_many(data)


dict_news = df_lenta.to_dict('records')
db = 'parsed_jobs'
collection = 'news'
insert_data(db, dict_news, collection)


# Yandex News
response = requests.get(url_2, headers=header)
parsed = html.fromstring(response.text)

headlines_raw = parsed.xpath('//*[@class="mg-card__title"]/text()') # get headlines
links_2 = parsed.xpath('//*[@class="mg-card__text"]/a/@href') # get links for headlines
time_raw = parsed.xpath('//*[@class="mg-card-source__time"]') # get time data
time = [i.xpath('./text()')[0] for i in time_raw] # get times

headlines_2 = [i.replace('\xa0', ' ') for i in headlines_raw[1:]]  # refine headlines and remove first element

# get dates to add to date list
today = datetime.now().strftime('%d %b at ')
yesterday = (datetime.now() - timedelta(1)).strftime('%d %b at ')
date_2 = []

for i in time[1:]:
    if len(i) == 5:
        date_2.append(today+i)
    elif len(i) == 13:
        date_2.append(yesterday+i[-5:])
    else:
        date_2.append(i)

source_2 = [url_2 for i in headlines_2]

data_2 = {
    "Headline": headlines_2,
    "Publish date": date_2,
    "News link": links_2,
    "Source": source_2
}
# create dataframe
df_yandex = pd.DataFrame(data_2)

dict_news = df_yandex.to_dict('records')
insert_data(db, dict_news, collection)

# mail ru
# news are contained in 3 different blocks, I will retrieve data from each block
response = requests.get(url_3, headers=header)
parsed = html.fromstring(response.text)

headlines_from_list = parsed.xpath('//*/li[@class="list__item"]/a/text()')
links_from_list = parsed.xpath('//*/li[@class="list__item"]/a/@href')
headlines_from_body = parsed.xpath('//*[@class="list__text"]/a/span/text()') 
links_from_body = parsed.xpath('//*[@class="list__text"]/a/@href') 
headlines_with_img = parsed.xpath('//*[@class="cell"]/a/span/text()') 
links_with_img = parsed.xpath('//*[@class="cell"]/a/@href') 

headlines_raw = headlines_from_list + headlines_from_body + headlines_with_img
headlines_3 = [i.replace('\xa0', ' ').replace('\r\n','') for i in headlines_raw]  # refine headlines
links_3 = links_from_list + links_from_body + links_with_img

date_3 = []

# date will be retrieved from the article itself
for i in links_3:
    response = requests.get(i, headers=header)
    parsed = html.fromstring(response.text)
    temp_date = parsed.xpath('//*[@class="note__text breadcrumbs__text js-ago"]/@datetime') # get date from the attribute
    date_3.append(datetime.strptime(temp_date[0], '%Y-%m-%dT%H:%M:%S%z').strftime('%d %b %Y at %H:%M')) # convert date to desired format

source_3 = [url_3 for i in headlines_3]

data_3 = {
    "Headline": headlines_3,
    "Publish date": date_3,
    "News link": links_3,
    "Source": source_3
}

# create dataframe
df_mailru = pd.DataFrame(data_3)

dict_news = df_mailru.to_dict('records')
insert_data(db, dict_news, collection)

df_news = pd.concat([df_lenta, df_yandex, df_mailru], axis=0, ignore_index=True)

df_news.to_csv('news_parse.csv')