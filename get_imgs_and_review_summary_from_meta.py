# Author: T_Xu(create), S_Sun(modify)
'''
获取每个POI对应的图片集和review summary

POI信息来自meta-xxx.json(from Google Local Data), 根据POI的url获取信息.
下载的数据保存在'./dataset/xxx(region name)/downloaded_multimodal_data/'中
其中, 'download.log'为下载日志, 'xxx.png'为下载图片, 'skip_img_file'为已下载的POI的图片(用于下次跳过不再下载), 
'review_summary.json'为下载的review summary, 'skip_review_summary_file'为已下载的POI的review summary(用于跳过). 
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import requests
import os
import json
from fake_useragent import UserAgent
import random
import time
import logging
import argparse

class Chrome:
    def __init__(self, proxy, path):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无头模式，不需要打开浏览器窗口
        options.add_argument('--proxy-server=' + proxy)  # 设置代理
        options.add_argument('--log-level=3')  # 禁用日志输出
        self.driver = webdriver.Chrome(path, options=options) # Replace with the path to your ChromeDriver executable

    def get(self, url):
        # 发请求，不主动抓异常，出现异常停止程序
        self.driver.get(url) 

    def get_image_urls(self): # 这块有点问题
        # 爬取'Photos & videos' or 'Photos'栏中的第一个'All'中的所有图片url
        images = self.driver.find_elements(By.CSS_SELECTOR, ".cRLbXd .ofKBgf img")
        # 没爬到可能是只有'Photos'栏
        if images is None or len(images) == 0:
            images = self.driver.find_elements(By.CSS_SELECTOR, ".h2Jmld .jtJMuf img")
        # 取出url
        image_urls = [image.get_attribute('src') for image in images]
        # 返回
        return image_urls
    
    def get_review_summary(self):
        # 爬取'Review summary'栏中的评论
        text_elements = self.driver.find_elements(By.CSS_SELECTOR, ".OXD3gb")
        texts = [text.find_elements(By.CSS_SELECTOR, "span") for text in text_elements]

        # 组织为数组
        res = []
        for spans in texts:
            span_text = ''
            for span in spans:
                span_text += span.get_attribute('innerText')
            span_text = span_text.replace('"', '')
            res.append(span_text)

        return res

def http_get(url):
    # 随机生成User-Agent头信息，用于反爬虫
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    try:
        # get请求，自动跳转，添加头信息
        res = requests.get(url, allow_redirects=True, headers=headers)
    except requests.exceptions.ProxyError: 
        logger.error(f'下载失败, 由于代理断了（或SSLError）, 图片url为:{url}')
        # 多睡会
        time.sleep(random.randint(2, 4))
        # 方法直接结束，下载下一张，因为没有记录到skip_file中，最后统一执行即可补全
        return None
    except requests.exceptions.SSLError:
        logger.error(f'下载失败, 由于代理断了（或SSLError）, 图片url为:{url}')
        # 多睡会
        time.sleep(random.randint(2, 4))
        # 方法直接结束，下载下一张，因为没有记录到skip_file中，最后统一执行即可补全
        return None

    return res

def init_logger(log_file_path, log_file_name):
    log_file_path = os.path.join(log_file_path, log_file_name)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    fh = logging.FileHandler(log_file_path, 'a', 'utf-8')
    fh.setLevel(logging.INFO)
    logging.basicConfig(
        level=logging.INFO,
        handlers = [sh, fh]
    )
    return logging.getLogger()

def download_images(row_i, gmap_id, image_urls, downloaded_data_path, skip_img_set, skip_img_file):
    
    
    for i, url in enumerate(image_urls):
        # 每张图片的唯一标识
        img_id = str(row_i + 1) + '_' + gmap_id + '_' + str(i + 1)
        
        # 跳过已下载
        if img_id in skip_img_set: 
            return

        try:
            # 下载单张
            image = http_get(url)
        except requests.exceptions.MissingSchema: # 捕获url中没有'https:'或'http:'异常
            # 添加schema
            url = 'https:' + url
            # 重新下载
            image = http_get(url)
        # 睡一会
        time.sleep(random.randint(1, 2))
        # 判空
        if image is None:
            continue

        # 保存图片
        img_file_path = downloaded_data_path + 'gmap_' + img_id + '.png'
        with open(img_file_path, 'wb') as f:
            f.write(image.content)
            f.flush()
            f.close()

            # 记录下载成功的图片路径
            logger.info(f'下载成功, 图片路径为:{img_file_path}')
            # 记录已下载的gmap_id
            skip_img_file.write(img_id + '\n')
            skip_img_file.flush()

if __name__ == '__main__':
    # paremeters
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', type=str, default='Alabama', help='the region name of datasets(e.g. California)')
    parser.add_argument('--proxy', type=str, default='http://127.0.0.1:7890', help='proxy server(http://ip+port)')
    parser.add_argument('--chromedriver_path', type=str, default='D:\Development-Files\ChromeDriver\chromedriver.exe', help='chrome driver local path')
    args, _ = parser.parse_known_args()

    # 配置代理服务器
    os.environ['http_proxy'] = args.proxy
    os.environ['https_proxy'] = args.proxy # 这个也要配置成http://xxx

    # path设置
    parent_path = './dataset/' + args.region + '/'
    if not os.path.exists(parent_path):
        os.mkdir(parent_path)
    downloaded_data_path = parent_path + 'downloaded_multimodal_data/'
    if not os.path.exists(downloaded_data_path):
        os.mkdir(downloaded_data_path)
    dataset_path = parent_path + 'meta-' + args.region + '.json'
    review_summary_file_path = downloaded_data_path + 'review_summary.json'
    skip_img_file_path = downloaded_data_path + 'skip_img_file'
    skip_review_summary_file_path = downloaded_data_path + 'skip_review_summary_file'

    # 初始化日志
    log_file_name = 'download.log'
    logger = init_logger(log_file_path=downloaded_data_path, log_file_name=log_file_name)
    
    # 初始化浏览器
    chrome = Chrome(args.proxy, args.chromedriver_path)

    # 打开跳过文件
    skip_img_file = open(skip_img_file_path, 'a+')
    skip_img_file.seek(0) # 光标移到文件开始
    skip_review_summary_file = open(skip_review_summary_file_path, 'a+')
    skip_review_summary_file.seek(0) 
    # 转为set集合
    skip_img_set = set(skip_img_file.read().splitlines()) # 记录：row_gid_index
    skip_review_summary_set = set(skip_review_summary_file.read().splitlines()) # 记录：row_gid
    
    # 打开meta-xxx.json文件
    json_file = open(dataset_path, 'r')
    # 遍历json，row_i为行号，line为一行数据
    for row_i, line in enumerate(json_file):
        # 解析json对象，得到字典
        obj = json.loads(line)

        # 取出obj.gmap_id和obj.url
        gmap_id = obj['gmap_id'].replace(":", "-")
        url = obj['url']

        # 跳过img和review_summary都已下载的，因为chrome.get(url)执行速度太慢
        if (str(row_i + 1) + '_' + gmap_id) in skip_review_summary_set and (str(row_i + 1) + '_' + gmap_id + '_' + str(1)) in skip_img_set:
            continue

        # 打开网页
        chrome.get(url)

        # 获取image_urls
        image_urls = chrome.get_image_urls()
        # 下载图片集
        download_images(row_i, gmap_id, image_urls, downloaded_data_path, skip_img_set, skip_img_file)

        # review_summary标识
        review_summary_id = str(row_i + 1) + '_' + gmap_id
        # 跳过已获取
        if review_summary_id in skip_review_summary_set: 
            continue
        # 获取review summary
        review_summary = chrome.get_review_summary()
        # 组织为json
        review_summary_dict = {review_summary_id: review_summary}
        review_summary_json = json.dumps(review_summary_dict)
        # 保存到文件中
        with open(review_summary_file_path, 'a+') as f:
            f.write(review_summary_json + '\n')
            f.flush()
            logger.info(f'保存review summary成功, review_sum_id为:{review_summary_id}')
            # 记录已下载的gmap_id
            skip_review_summary_file.write(review_summary_id + '\n')
            skip_review_summary_file.flush()
    
    chrome.driver.quit()

    skip_img_file.close()
    skip_review_summary_file.close()
