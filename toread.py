#!/usr/bin/env python
# coding: utf-8

from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
import gspread
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
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()  # 關閉錯誤警告
from urllib.request import HTTPError  # 載入 HTTPError
from bs4 import BeautifulSoup
import time  # 強制等待

my_options = Options()
my_options.add_argument("--incognito")  # 開啟無痕模式
my_options.add_experimental_option('excludeSwitches', ['enable-automation'])  #把新版google的自動控制提醒關掉
# my_options.add_argument('--start-maximized')  # 視窗最大化
# my_options.add_argument('--headless')  # 不開啟實體瀏覽器
my_capabilities = DesiredCapabilities.CHROME
my_capabilities[
    'pageLoadStrategy'] = 'none'  # 當 html下載完成之後，不等待解析完成，selenium會直接返回

def toread_crawlers(org, org_url, ISBN, url_behind, thetable, del_lst, driver):
    wait = WebDriverWait(driver, 10)
    search_url = org_url + ISBN + url_behind
    driver.get(search_url)
    time.sleep(5)

    try: # 有的書有不只一種版本
        version = int(len(driver.find_elements_by_name('book_link')))
    except:
        version = 0
    df_lst = []
    if version != 0:
        for i in range(version):
            edition = driver.find_elements_by_name('book_link')[i].click()
            time.sleep(5)

            df_ntc = pd.read_html(driver.page_source, encoding="utf-8")[thetable]

            df_ntc.insert(0, "圖書館", [org for i in range(df_ntc.shape[0])])
            df_ntc.insert(10, "連結", [org_url for i in range(df_ntc.shape[0])])
            for deleted in del_lst:
                df_ntc.pop(deleted)

            df_ntc.rename(columns={ "借閱狀態": "館藏狀態", "典藏地名稱": "館藏地"}, inplace=True)
            df_lst.append(df_ntc)

            driver.find_element_by_link_text("回首頁").click()
            time.sleep(6)
        table = pd.concat(df_lst, axis=0, ignore_index=True)
        return(table.dropna())

    else:
        driver.find_element_by_name('book_link').click()
        time.sleep(8)

        df_ntc = pd.read_html(driver.page_source, encoding="utf-8")[thetable]
        df_ntc.insert(0, "圖書館", [org for i in range(df_ntc.shape[0])])
        df_ntc.insert(10, "連結", [org_url for i in range(df_ntc.shape[0])])
        for deleted in del_lst:
            df_ntc.pop(deleted)

        df_ntc.rename(columns={ "借閱狀態": "館藏狀態", "典藏地名稱": "館藏地"}, inplace=True)
        df_lst.append(df_ntc)
        table = pd.concat(df_lst, axis=0, ignore_index=True)
        return(table.dropna())

def toread(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    worksheet.clear()

    output = []
    final = ""
    goal = "https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit?usp=sharing"
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        toread_crawlers(
        org='國立臺東專科學校',
        org_url='https://library.ntc.edu.tw/toread/opac/search?q=',
        ISBN=ISBN,
        url_behind='&max=0&view=LIST&level=all&material_type=all&location=0',
        thetable=int(5),
        del_lst=["條碼號", "資料類型", "館藏流通類別", "預約人數", "備註欄", "使用類型", "Unnamed: 12", "附件", "調閱人數", "尋書單"],
        driver=driver
        )
    )

    output.append(
        toread_crawlers(
        org='醒吾科技大學',
        org_url="http://120.102.129.237/toread/opac/search?q=",
        ISBN=ISBN,
        url_behind='&max=0&view=LIST&level=all&material_type=all&location=0',
        thetable=int(5),
        del_lst=["尋書單", "條碼號", "資料類型", "館藏流通類別", "備註欄", "使用類型", "Unnamed: 11", "附件", "預約人數"],
        driver=driver
        )
    )
    '''
    output.append(
        toread_crawlers(
        org="國立東華大學",
        org_url="https://books-lib.ndhu.edu.tw/toread/opac/search?q=",
        ISBN=ISBN,
        url_behind='&max=0&view=LIST&level=all&material_type=all&location=0',
        thetable=int(6),
        del_lst=["條碼號", "資料類型", "館藏流通類別", "預約狀態", "備註欄", "使用類型", "附件", "Unnamed: 10"],
        driver=driver
        )
    )
    '''
    
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.update([gg.columns.values.tolist()] + gg.values.tolist())
    return "https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit?usp=sharing"




