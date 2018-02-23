# -*- coding: utf-8 -*-
import socket

import scrapy
import re
import redis
import time
import sys
import urllib
from scrapy_splash import SplashRequest
from taobao_whole.spiders import config
from taobao_whole.spiders import send_mail
from  taobao_whole.items import TaobaoWholeItem


keyword = []
SLEEP = 3

class con_db_read(object):
    '''
    1、连接数据库
    2、获取所有url的关键字
    3、获取每个关键字下的所有url
    4、以便于爬虫class调用
    '''

    def con_db(self):
        pool = redis.ConnectionPool(host=config.REDIS_URL, db=config.REDIS_DB, port=config.REDIS_PORT)
        redis_store = redis.Redis(connection_pool=pool)
        return redis_store

    def read_key(self):
        '''
        1、读取关键字
        :param con:
        :return:
        '''
        key = self.con_db().keys()
        for k in key:
            k = k.decode('utf-8')
            keyword.append(k)

    def read_values(self):
        '''
        1、通过关键字，查询每个关键字下的链接
        :param con:
        :return:
        '''
        for links in keyword:
            for keys in self.con_db().smembers(links):
                yield keys.decode('utf-8')

    def main(self):
        self.read_key()
        return self.read_values()


class increment_url(object):
    '''
    1、Already_crawling负责存储已经爬取过的url
    '''
    def con_db(self):
        pool = redis.ConnectionPool(host=config.REDIS_URL, db=config.REDIS_DB, port=config.REDIS_PORT)
        redis_store = redis.Redis(connection_pool=pool)
        return redis_store

    def read_url(self):
        try:
            return list(self.con_db().smembers('url'))
        except Exception as e:
            print(e)

    def Already_crawling(self,url):
        self.con_db().sadd('Already_urls',url)

    def remove_url(self,url):
        pool = redis.ConnectionPool(host=config.REDIS_URL, db=config.REDIS_DB, port=config.REDIS_PORT)
        redis_store = redis.Redis(connection_pool=pool)
        print('正在删除url：',url)
        redis_store.srem('url',url)

    def add_url(self,url):
        self.con_db().sadd('url',url)


class TaobaoSpiderSpider(scrapy.Spider):
    name = "taobao_spider"
    allowed_domains = ["www.taobao.com"]
    start_urls = ['https://www.taobao.com/']

    def start_requests(self):
        '''
        1、启用increment_url，连接数据库读取url
        :return:
        '''
        try:
            for line in increment_url().read_url():
                yield SplashRequest(line.decode('utf-8'), self.parse, args={'wait': 0.5})
                # yield self.make_requests_from_url(line.decode('utf-8'))
        except Exception as e:
            pass

    def parse(self, response):
        if response.status == 200 and len(response.text) > 100:
            time.sleep(config.SLEEP)
            TW = TaobaoWholeItem()
            p_name = response.xpath('//div[@class="items"]//div[@class="pic"]/a/img/@alt').extract()
            p_link = response.xpath('//div[@class="items"]//div[@class="pic"]/a/@href').extract()
            p_price = response.xpath('//div[@class="items"]//strong/text()').extract()
            p_volume = response.xpath('//div[@class="items"]//div[@class="deal-cnt"]/text()').extract()
            p_location = response.xpath('//div[@class="items"]//div[@class="location"]/text()').extract()
            for i in zip(p_name, p_link, p_price,p_volume, p_location):
                item = list(i)
                TW['name'] = item[0]
                TW['link'] = 'https:'+item[1]
                TW['price'] = item[2]
                TW['volume'] = re.search('\d+',item[3]).group()
                TW['location'] = item[4]
                print(TW)
                return TW
            increment_url().Already_crawling(urllib.parse.unquote(response.url))
            increment_url().remove_url(urllib.parse.unquote(response.url))
        elif response.status != 200 and len(response.text) < 100:
            increment_url().add_url(urllib.parse.unquote(response.url))
            print('淘宝官网可能已经开始屏蔽')
            send_mail.send_email('IP:{ip}\n爬取被屏蔽预警'.format(ip=get_ip()))
        else:
            send_mail.send_email('IP:{ip}\n爬取任务停止报警'.format(ip=get_ip()))
            sys.exit()

def get_ip():
    '''
    1、获取当前服务器ip地址
    :return:
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 0))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


