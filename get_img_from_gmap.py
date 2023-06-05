# Author: T_Xu(create), S_Sun(modify)

import requests
from bs4 import BeautifulSoup
import os
import json
from fake_useragent import UserAgent
import random
import time
import logging

class spider:

    def __init__(self, path):
        # 配置代理服务器
        os.environ['http_proxy'] = 'http://127.0.0.1:7890'
        os.environ['https_proxy'] = 'http://127.0.0.1:7890' # 这个也要配置成http://xxx
        # 初始化路径，一般设置为当前路径下的某文件夹，如'./imgs/Hawaii/meta_img'
        self.path = path
        # 若路径不存在，则创建
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))

    def http_get(self, url):
        # 随机生成User-Agent头信息，用于反爬虫
        ua = UserAgent()
        headers = {'User-Agent': ua.random}

        try:
            # get请求，自动跳转，添加头信息
            res = requests.get(url, allow_redirects=True, headers=headers)
        except requests.exceptions.ProxyError: 
            logger.error(f'下载失败, 由于代理断了（或SSLError）, 图片url为:{url}, gmap_id为:{gmap_id}, index为:{index}')
            # 多睡会
            time.sleep(random.randint(20, 25))
            # 方法直接结束，下载下一张，因为没有记录到skip_file中，最后统一执行即可补全
            return None
        except requests.exceptions.SSLError:
            logger.error(f'下载失败, 由于代理断了（或SSLError）, 图片url为:{url}, gmap_id为:{gmap_id}, index为:{index}')
            # 多睡会
            time.sleep(random.randint(20, 25))
            # 方法直接结束，下载下一张，因为没有记录到skip_file中，最后统一执行即可补全
            return None

        return res

    def get_img(self, url, gmap_id, index):
        # 爬取网页
        r = self.http_get(url)
        if r is None:
            return
        
        # 解析r.content
        soup = BeautifulSoup(r.content, 'html.parser')
        # 找出r.content中itemprop="image"的标签
        image = soup.find(itemprop="image")
        # image中的content就是图片的url
        try: 
            image_url = image['content']
        except TypeError:
            logger.error(f'下载失败, 由于反爬虫, 图片url为:{url}, gmap_id为:{gmap_id}, index为:{index}')
            # 多睡会
            time.sleep(random.randint(15, 25))
            # 方法直接结束，下载下一张，因为没有记录到skip_file中，最后统一执行即可补全
            return
        
        # 下载图片
        try: 
            image_ = self.http_get(image_url)
        except requests.exceptions.MissingSchema: # 捕获url中没有'https:'或'http:'异常
            # 添加schema
            image_url = 'https:' + image_url
            # 重新下载图片
            image_ = self.http_get(image_url)
        if image_ is None:
            return
    
        # 保存到本地
        file_path = self.path + 'gmap_' + str(index) + '_' + gmap_id + '.png'
        with open(file_path, 'wb') as f:
            f.write(image_.content)

            # 记录下载成功的图片路径
            logger.info(f'下载成功, 图片路径为:{file_path}')
            # 记录已下载的gmap_id
            skip_file.write(gmap_id + '\n')
            skip_file.flush()
            

if __name__ == '__main__':
    # 指定文件夹
    img_path = './imgs/Hawaii/meta_img/'
    # 初始化爬虫
    sp = spider(img_path)

    # 初始化日志
    logfilename = 'download_imgs.log'
    logfilepath = os.path.join(img_path, logfilename)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    fh = logging.FileHandler(logfilepath, 'a', 'utf-8')
    fh.setLevel(logging.INFO)
    logging.basicConfig(
        level=logging.INFO,
        handlers = [sh, fh]
    )
    logger = logging.getLogger()

    # 数据集路径
    dataset_path = './dataset/Hawaii/meta-Hawaii.json'
    # 打开并解析json文件，按行
    json_file = open(dataset_path, 'r')

    # 根据skip_file文件用于跳过已下载的gmap_id
    skip_file = open(img_path+'skip_file', 'r+')
    skip_set = set(skip_file.read().splitlines()) # 这块还是有问题，用set可以提升效率，但是会造成一些图片缺失，不过有记录，最后可以写程序补全缺失

    for index, line in enumerate(json_file):
        # 解析json对象，得到字典
        obj = json.loads(line)

        # 取出obj.gmap_id和obj.url
        gmap_id = obj['gmap_id'].replace(":", "_")
        url = obj['url']
        
        # 跳过已下载
        if gmap_id in skip_set: 
            continue

        # 线程睡一会，反爬虫
        time.sleep(random.randint(1, 5))

        # 使用spider下载图片到本地
        logger.info(f'即将下载图片gmap_id:{gmap_id}')
        sp.get_img(url, gmap_id, index)
