from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # 設定 driver 的行為
from selenium.webdriver.support.ui import Select  # 選擇＂下拉式選單＂
from selenium.webdriver.common.keys import Keys  # 鍵盤操作
from selenium.common.exceptions import NoSuchElementException, TimeoutException  # 載入常見錯誤
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # 更改載入策略
from selenium.webdriver.support.ui import WebDriverWait  # 等待機制
from selenium.webdriver.support import expected_conditions as EC  # 預期事件
from selenium.webdriver.common.by import By  # 找尋元素的方法
import pandas as pd  # 載入 pandas
import pandas.io.formats.excel  # 輸出自定義格式 Excel
import requests
from bs4 import BeautifulSoup
import time  # 強制等待
from crawlers import *

my_options = Options()
my_options.add_argument('--incognito')  # 開啟無痕模式
# my_options.add_argument('--start-maximized')  # 視窗最大化
# my_options.add_argument('--headless')  # 不開啟實體瀏覽器
my_capabilities = DesiredCapabilities.CHROME
my_capabilities['pageLoadStrategy'] = 'eager'  # 頁面加載策略：HTML 解析成 DOM

driver = webdriver.Chrome(
    options=my_options, desired_capabilities=my_capabilities)

table = webpac_gov_crawler(
    driver=driver,
    org='宜蘭縣公共圖書館',
    org_url='https://webpac.ilccb.gov.tw/advanceSearch',
    ISBN='9789868879348'
)
print(table)
