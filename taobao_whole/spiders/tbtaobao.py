# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy_splash import SplashRequest


class TbtaobaoSpider(scrapy.Spider):
    name = "tbtaobao"
    allowed_domains = ["www.taobao.com"]
    start_urls = ['https://s.taobao.com/search?q=坚果&s=880&sort=sale-desc']

    def start_requests(self):
        for url in self.start_urls:
            # yield Request(url,dont_filter=True)
            yield SplashRequest(url, self.parse, args={'wait': 0.5})

    def parse(self, response):
        p_name = response.xpath('//div[@class="items"]//div[@class="pic"]/a/img/@alt').extract()
        p_link = response.xpath('//div[@class="items"]//div[@class="pic"]/a/@href').extract()
        p_price = response.xpath('//div[@class="items"]//strong/text()').extract()
        p_volume = response.xpath('//div[@class="items"]//div[@class="deal-cnt"]/text()').extract()
        p_location = response.xpath('//div[@class="items"]//div[@class="location"]/text()').extract()
        for i in zip(p_name,p_link,p_price,p_volume,p_location):
            print(list(i))
