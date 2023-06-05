# Author: T_Xu(create), S_Sun(modify)

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

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






