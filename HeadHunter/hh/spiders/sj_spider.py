import scrapy
from scrapy.http import HtmlResponse
from items import HhItem    # it works even if it's highlighted as error
import re

class SjSpiderSpider(scrapy.Spider):
    name = 'sj_spider'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=менеджер проектов']

    def parse(self, response: HtmlResponse):
        # get the link to cycle through pages with found vacancies
        next_page = response.css('a.f-test-link-Dalshe::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        # get the vacancy link
        vacansy = response.css(
            '.f-test-vacancy-item ._2JivQ::attr(href)'
        ).extract()

        # follow each vacancy link to parse the page
        for link in vacansy:
            yield response.follow(link, callback=self.vacansy_parse)

    # parse page
    def vacansy_parse(self, response: HtmlResponse):
        name = response.css('h1._1h3Zg.rFbjy._2dazi._2hCDz::text').extract_first() # get vacancy title

        # create temporary variable to store all retrieved data on salary
        temp_sal = response.css('span._1OuF_.ZON4b span._1h3Zg._2Wp8I._2rfUm._2hCDz::text').extract()
        # due to odd format of salary stored in html, convert to string and clean
        salary_trimmed = ' '.join(temp_sal).replace('\xa0', '')
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
        source = 'https://superjob.ru/'

        yield HhItem(name=name, min_salary=min_salary, max_salary=max_salary, vacancy_link=vacancy_link, source=source)
