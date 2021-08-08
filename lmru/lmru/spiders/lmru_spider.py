import scrapy
from scrapy.http import HtmlResponse
from items import LmruItem
from scrapy.loader import ItemLoader


class LmruSpiderSpider(scrapy.Spider):
    name = 'lmru_spider'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/bytovaya-himiya/']

    def parse(self, response: HtmlResponse):
        # get the link to cycle through pages with found products
        next_page = response.css(
            'a.bex6mjh_plp.s15wh9uj_plp.l7pdtbg_plp.r1yi03lb_plp.sj1tk7s_plp::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        goods_links = response.css(
            'a.bex6mjh_plp.b1f5t594_plp.p5y548z_plp.pblwt5z_plp.nf842wf_plp::attr(href)').extract()
        for link in goods_links:
            yield response.follow(link, callback=self.parse_goods)

    def parse_goods(self, response: HtmlResponse):
        l = ItemLoader(item=LmruItem(), selector=response)
        l.add_css('name', 'h1.header-2')
        l.add_xpath('price', '//span[@slot ="price"]')
        l.add_xpath('pictures', '//picture[@slot ="pictures"]/source[4]/@srcset')
        l.add_css('availability', 'uc-stock-availability span')

        yield l.load_item()
