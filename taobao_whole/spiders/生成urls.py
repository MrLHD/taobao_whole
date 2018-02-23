import redis
from concurrent.futures import ThreadPoolExecutor


REDIS_URL = '172.16.5.29'
REDIS_PORT = 6379
REDIS_DB = 1

KEYWORD = ['男装','女装','男鞋','女鞋','箱包','玩具','零食','特色小吃','耳机','啤酒','水果','配件',
            '内衣','用品','家电','数码','美妆','珠宝','眼镜','户外','乐器','生鲜','宠物','农资',
            '房产','汽车','二手车','办公','DIY','五金电子','百货','餐厨','家庭保健','学习','卡券','本地服务',
           '洗护','保健品','动漫','影视','建材','家纺','手机配件','电脑配件','戒指','项链','黄金','坚果','自行车','沙发']

pool = ThreadPoolExecutor(10)

def make_urls(key_word):
    '''
    1、生成每件商品的url
    :param key_word:
    :return:
    '''
    global jishu
    r_page = 0
    try:
        for pg in range(1,101):
            if r_page== 0:
                url = 'https://s.taobao.com/search?q={keyword}&s={page}&sort=sale-desc'.format(keyword=key_word,page=22)
                save_db(url,key_word)
            r_page += 44
            base_url = 'https://s.taobao.com/search?q={keyword}&s={page}&sort=sale-desc'.format(keyword=key_word,page=r_page)
            save_db(base_url,key_word)
    except Exception as e:
        print('make url error!!!')

def save_db(urls,keywords):
    '''
    1、报错到redis数据库
    :param urls:
    :return:
    '''
    try:
        pool = redis.ConnectionPool(host=REDIS_URL,db=REDIS_DB,port=REDIS_PORT)
        redis_store = redis.Redis(connection_pool=pool)
        redis_store.sadd(keywords,urls)
    except Exception as e:
        print('连接数据库失败：', e)

def main():
    for key in KEYWORD:
        pool.submit(make_urls,key)


if __name__ == '__main__':
    main()

pool.shutdown(wait=True)