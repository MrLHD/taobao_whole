import redis
from taobao_whole.spiders import config
keyword = []

class con_db_read(object):
    '''
    1、连接数据库
    2、获取所有url的关键字
    3、获取每个关键字下的所有url
    4、以便于爬虫class调用
    '''

    def con_db(self):
        pool = redis.ConnectionPool(host=config.REDIS_URL, db=1, port=config.REDIS_PORT)
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

    def save(self,url):
        pool = redis.ConnectionPool(host=config.REDIS_URL, db=2, port=config.REDIS_PORT)
        redis_store = redis.Redis(connection_pool=pool)
        redis_store.sadd('url',url)

def main():
    read_urls = con_db_read().main()
    while True:
        try:
            con_db_read().save(read_urls.__next__())
        except StopIteration as e:
            print('read database success！',e)
            break
        except Exception as e:
            print('写入失败',e)
            break

if __name__ == '__main__':
    main()