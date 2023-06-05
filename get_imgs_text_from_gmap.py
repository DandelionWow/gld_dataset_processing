# Author: T_Xu(create), S_Sun(modify)

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import os
import json
from fake_useragent import UserAgent
import random
import time
import logging

class Chrome:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无头模式，不需要打开浏览器窗口
        options.add_argument('--proxy-server=http://127.0.0.1:7890')  # 设置代理
        self.driver = webdriver.Chrome('D:\Development-Files\ChromeDriver\chromedriver.exe', options=options) # Replace with the path to your ChromeDriver executable

    def get_image_urls(self, url): 
        # 发请求
        self.driver.get(url) 
        # 爬取'Photos & videos'栏中的第一个'All'中的所有图片url
        images = self.driver.find_elements(By.CSS_SELECTOR, ".cRLbXd .ofKBgf img")
        image_urls = [image.get_attribute('src') for image in images]
        # 返回
        return image_urls

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

if __name__ == '__main__':
    parent_path = './dataset/Hawaii/downloaded_multimodal_data/'
    if not os.path.exists(parent_path):
        os.mkdir(parent_path)

    # 初始化日志
    log_file_name = 'download.log'
    logger = init_logger(log_file_path=parent_path, log_file_name=log_file_name)
    
    # 初始化浏览器
    chrome = Chrome()

    image_urls = chrome.get_image_urls('https://www.google.com/maps/place//data=!4m2!3m1!1s0x7c00456eecad3111:0x8217f9600c51f33?authuser=-1&hl=en&gl=us')
    image_urls = chrome.get_image_urls('https://www.google.com/maps/place//data=!4m2!3m1!1s0x7c006e76398089e5:0xa0e364b04ff91fd1?authuser=-1&hl=en&gl=us')
    print(image_urls)
    

# Configure Selenium to use a web driver (e.g., ChromeDriver)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式，不需要打开浏览器窗口
options.add_argument('--proxy-server=http://127.0.0.1:7890')  # 设置代理
driver = webdriver.Chrome('D:\Development-Files\ChromeDriver\chromedriver.exe', options=options)  # Replace with the path to your ChromeDriver executable

url = 'https://www.google.com/maps/place//data=!4m2!3m1!1s0x7c00456eecad3111:0x8217f9600c51f33?authuser=-1&hl=en&gl=us'
driver.get(url)

# Use Selenium to interact with the page, wait for dynamic content to load, and retrieve the image URL
images = driver.find_elements(By.CSS_SELECTOR, ".cRLbXd .ofKBgf img")
image_urls = [image.get_attribute('src') for image in images]
# for url in image_urls:
#    print(url)   OXD3gb

# download images
for i, url in enumerate(image_urls):
    image = requests.get(url)
    with open(f'google_map_{i}.png', 'wb') as f:
        f.write(image.content)

text_elements = driver.find_elements(By.CSS_SELECTOR, ".OXD3gb")
texts = [text.find_elements(By.CSS_SELECTOR, "span") for text in text_elements]
for spans in texts:
    span_text = ''
    for span in spans:
        span_text += span.get_attribute('innerHTML')
    print(span_text)

# Close the web driver
driver.quit()






