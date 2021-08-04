import scrapy
from scrapy.http import HtmlResponse
from items import HhItem    # it works even if it's highlighted as error
import re

class HhSpiderSpider(scrapy.Spider):
    name = 'hh_spider'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&area=1&enable_snippets=true&salary=&st=searchVacancy&text=%D0%9C%D0%B5%D0%BD%D0%B5%D0%B4%D0%B6%D0%B5%D1%80+%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%BE%D0%B2']

    def parse(self, response: HtmlResponse):
        # get the link to cycle through pages with found vacancies
        next_page = response.css('span.bloko-form-spacer a.bloko-button::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        # get the vacancy link
        vacansy = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)'
        ).extract()

        # follow each vacancy link to parse the page
        for link in vacansy:
            yield response.follow(link, callback=self.vacansy_parse)

    # parse page
    def vacansy_parse(self, response: HtmlResponse):
        name = response.css('h1.bloko-header-1::text').extract_first() # get vacancy title
        temp_sal = response.css('span.bloko-header-2::text').extract()  # temporary variable for salaries
        salary_trimmed = temp_sal[0].replace('\xa0', '')    # clean data
        salary_all = re.findall(r"(\d+)", salary_trimmed)   # extract numbers

        # define which salary is available and store under respective variable
        if len(salary_all) == 2:
            min_salary = salary_all[0]
            max_salary = salary_all[1]
        elif salary_trimmed[:2] == 'от':
            min_salary = salary_all[0]
            max_salary = 'NA'
        elif salary_trimmed[:2] == 'до':
            min_salary = 'NA'
            max_salary = salary_all[0]
        else:
            min_salary = 'NA'
            max_salary = 'NA'
        vacancy_link = response.request.url     # get the vacancy link
        source = 'https://hh.ru/'

        yield HhItem(name=name, min_salary=min_salary, max_salary=max_salary, vacancy_link=vacancy_link, source=source)
