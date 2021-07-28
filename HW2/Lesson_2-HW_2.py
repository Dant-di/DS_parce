import requests, lxml
import pandas as pd
from bs4 import BeautifulSoup as Bs
from fake_headers import Headers
import re

headers = Headers(headers=True).generate()
url = 'https://rskrf.ru/ratings/produkty-pitaniya'
main_url = 'https://rskrf.ru'
url_2 = 'https://roscontrol.com/category/produkti'
main_url_2 = 'https://roscontrol.com'

# first site
response = requests.get(url, headers=headers)
soup = Bs(response.text, 'lxml')

# links to explore categories
cat_urls = [i.get('href') for i in soup.select('.categories div a')]


# links to explore subcategories

sub_cat_urls = []
for i, val in enumerate(cat_urls):
    response = requests.get(main_url + cat_urls[i], headers=headers)
    soup = Bs(response.text, 'lxml')
    sub_cat = [i.get('href') for i in soup.select('.categories div a')]
    sub_cat_urls.extend(sub_cat)

# links for products
items_urls =[]

for i, val in enumerate(sub_cat_urls):
    response = requests.get(main_url + sub_cat_urls[i], headers=headers)
    soup = Bs(response.text, 'lxml')
    items = [i.get('href') for i in soup.select("noscript a")]
    items_urls.extend(items)

# data parcing from each product. All required information is taken from product page

name, cat, sub, safety, quality, rating, source = [], [], [], [], [], [], []

for i, val in enumerate(items_urls):
    response = requests.get(main_url + items_urls[i], headers=headers)
    soup = Bs(response.text, 'lxml')
    name.append((soup.find('h1', class_='h1 product-title').text).strip())
    cat.append([i.text for i in soup.select('ol.breadcrumb li')][2])
    sub.append((soup.find('a', class_='rating-id').text).replace(' — смотреть полный рейтинг', ''))

    if soup.find('span', string=re.compile('Безопасность')) == None:
        safety.append('NA')
    else:
        safety.append(soup.find('span', string=re.compile('Безопасность')).next_sibling.findNext('span').text)

    if soup.find('span', string=re.compile('Качество')) == None:
        quality.append('NA')
    else:
        quality.append(soup.find('span', string=re.compile('Качество')).next_sibling.findNext('span').text)
    rating.append([i.text for i in soup.select('div.rating-item.big div span')][0])
    source.append(main_url)

# create dataframe
data_1 = {
    "Product name": name,
    "Category": cat,
    "Subcategory": sub,
    "Safety": safety,
    "Quality": quality,
    "Rating": rating,
    "Source": source
}

df_1 = pd.DataFrame(data_1)


# Second site
response = requests.get(url_2, headers=headers)
soup = Bs(response.text, 'lxml')

cat_urls_2 = [i.get('href') for i in soup.select('.catalog__category-item.util-hover-shadow')]

# list of categories without sub categories
exception = [cat_urls_2[7], cat_urls_2[18],cat_urls_2[16]]

sub_cat_urls_2 = []

for i, val in enumerate(cat_urls_2):
    response = requests.get(main_url_2 + cat_urls_2[i], headers=headers)
    soup = Bs(response.text, 'lxml')
    sub_cat = [i.get('href') for i in soup.select('.catalog__category-item.util-hover-shadow')]
    sub_cat_urls_2.extend(sub_cat)
sub_cat_urls_2.extend(exception)


items_urls_2 =[]

for i, val in enumerate(sub_cat_urls_2):
    response = requests.get(main_url_2 + sub_cat_urls_2[i], headers=headers)
    soup = Bs(response.text, 'lxml')
    items = [i.get('href') for i in soup.select(".block-product-catalog__item.js-activate-rate.util-hover-shadow.clear")]
    items_urls_2.extend(items)


name_2, cat_2, sub_2, safety_2, quality_2, rating_2, source_2 = [], [], [], [], [], [], []

for i, val in enumerate(items_urls_2):
    response = requests.get(main_url_2 + items_urls_2[i], headers=headers)
    soup = Bs(response.text, 'lxml')
    name_2.append((soup.find('h1', class_='main-title testlab-caption-products util-inline-block').text).strip())
    cat_subcat = [i.text for i in soup.select('div.breadcrumb.mod-breadcrumb ol li a span')]
    cat_2.append(cat_subcat[1])
    if len(cat_subcat) == 3: # check fro the products without subcategory
        sub_2.append(cat_subcat[2])
    else:
        sub_2.append('-')

# check if product blacklisted
    if soup.find('span', class_='hide-with-1024', string=re.compile('В черном списке')) != None:
        safety_2.append('В черном списке')
        quality_2.append('В черном списке')
        rating_2.append('В черном списке')
        source_2.append(main_url_2)


# check if product has no info inside
    elif soup.find('div', class_='product__single-rev-total') == None:
        safety_2.append('NA')
        quality_2.append('NA')
        rating_2.append('NA')
        source_2.append(main_url_2)


    else:
        if soup.find('div', string=re.compile('Безопасность')) == None:
            safety_2.append('NA')
        else:
            safety_2.append(soup.find('div', string=re.compile('Безопасность')).parent.parent.previous_sibling.findNext(
                'span').text)

        if soup.find('div', string=re.compile('Качество')) == None:
            quality_2.append('NA')
        else:
            quality_2.append(
                soup.find('div', string=re.compile('Качество')).parent.parent.previous_sibling.findNext('span').text)
        rating_2.append([i.text for i in soup.select('div.product__single-rev-total div')][0])
        source_2.append(main_url_2)

data_2 = {
    "Product name": name_2,
    "Category": cat_2,
    "Subcategory": sub_2,
    "Safety": safety_2,
    "Quality": quality_2,
    "Rating": rating_2,
    "Source": source_2
}

df_2 = pd.DataFrame(data_2)
parce_results = pd.concat([df_1, df_2], axis=0, ignore_index=True)

parce_results.to_pickle('parce_results.pkl')