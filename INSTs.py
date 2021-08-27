#!/usr/bin/env python
# coding: utf-8

import os
import re
import time  # 強制等待
from bs4 import BeautifulSoup
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
# import requests.packages.urllib3
# requests.packages.urllib3.disable_warnings()  # 關閉錯誤警告
# from urllib.request import HTTPError  # 載入 HTTPError
from crawlers import *

# driver plus
# def get_chrome():
#     print('（./INSTs.py）執行 get_chrome() 函式')
#     my_options = webdriver.ChromeOptions()
#     my_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
#     my_options.add_argument("--incognito")  # 開啟無痕模式
#     my_options.add_argument("--headless")  # 不開啟實體瀏覽器
#     my_options.add_argument("--disable-dev-shm-usage")
#     my_options.add_argument("--no-sandbox")
#     my_options.add_argument('--disable-infobars')
#     my_options.add_experimental_option('useAutomationExtension', False)
#     my_options.add_experimental_option(
#         "excludeSwitches", ["enable-automation"])  # 把新版 google 的自動控制提醒關掉

#     # 當 html下載完成之後，不等待解析完成，selenium 會直接返回
#     my_capabilities = DesiredCapabilities.CHROME
#     my_capabilities['pageLoadStrategy'] = 'eager'


#     return webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=my_options, desired_capabilities=my_capabilities)
my_options = Options()
my_options.add_argument('--incognito')  # 開啟無痕模式
my_options.add_argument('--headless')  # 不開啟實體瀏覽器
my_capabilities = DesiredCapabilities.CHROME
my_capabilities['pageLoadStrategy'] = 'eager'  # 頁面加載策略：HTML 解析成 DOM


# ------------------------Primo找書--------------------------
def primo_finding(driver, org, tcn):  # 改wait
    sub_df_lst = []
    try:
        back = wait_for_element_clickable(
            driver, ".tab-header > prm-opac-back-button > button", 20, By.CSS_SELECTOR).click()
    except:
        back = None

    thelist = wait_for_elements_present(driver, tcn, 30, By.CLASS_NAME)
    if tcn == 'md-2-line.md-no-proxy._md':  # 如果是東吳或銘傳
        thelist = thelist[0:-2]
    else:
        pass

    for row in thelist:
        plist = row.find_elements_by_tag_name("p")
        where = row.find_elements_by_tag_name("h3")
        i = len(where)
        for sth in plist:
            a = sth.find_elements_by_tag_name("span")
            for _ in range(i):
                now_url = driver.current_url
                if org == "銘傳大學":
                    new_row = [org, where[_].text,
                               "沒有索書號喔QQ", a[0].text, now_url]
                else:
                    new_row = [org, where[_].text,
                               a[4].text, a[0].text, now_url]
                sub_df_lst.append(new_row)
                break
            break
    return sub_df_lst


def primo_two_finding(driver, org):
    print("進two_finding了")
    sub_df_lst = []

    similar_xpath = "/html/body/primo-explore/div[3]/div/md-dialog/md-dialog-content/sticky-scroll/prm-full-view/div/div/div[2]/div/div[1]/div[4]/div/prm-full-view-service-container/div[2]/div/prm-opac/md-tabs/md-tabs-content-wrapper/md-tab-content[2]/div/md-content/prm-location-items/div[2]/div[1]/p/span["
    status_xpath = similar_xpath + "1]"
    place_xpath = similar_xpath + "3]"
    num_xpath = similar_xpath + "5]"
    all = wait_for_element_present(
        driver, "ng-binding.ng-scope.zero-margin", 20, By.CLASS_NAME).text
    print(all)
    status = all.split(",")[0]
    place = (all.split(",")[1]).split("(")[0]
    number = (all.split(",")[1]).split("(")[1].strip(')')

    now_url = driver.current_url

    new_row = [org, place, number, status, now_url]
    sub_df_lst.append(new_row)
    print(sub_df_lst)
    return sub_df_lst


# ------------------------綠點點找書--------------------------
def primo_greendot_finding(driver, org):  # 改 wait
    sub_df_lst = []
    try:
        num = wait_for_elements_present(
            driver, 'EXLLocationTableColumn1', 10, By.CLASS_NAME)
        status = wait_for_elements_present(
            driver, 'EXLLocationTableColumn3', 10, By.CLASS_NAME)
        for i in range(0, len(num)):
            now_url = driver.current_url
            new_row = [org, "圖書館總館", num[i].text, status[i].text, now_url]
            sub_df_lst.append(new_row)
    except:
        pass

    return sub_df_lst


# webpac_gov_crawler(driver, org, org_url, ISBN)
# 宜蘭縣公共圖書館 ILCCB V OK
def ILCCB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    # driver = webdriver.Chrome(
    #     options=my_options, desired_capabilities=my_capabilities)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = webpac_gov_crawler(
        driver,
        '宜蘭縣公共圖書館',
        'https://webpac.ilccb.gov.tw/',
        ISBN
    )

    driver.close()
    print("banana")
    worksheet.append_rows(gg.values.tolist())
    print("+++")
    return gg

# 桃園市立圖書館 TYPL V OK


def TYPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_gov_crawler(
        driver,
        '桃園市立圖書館',
        'https://webpac.typl.gov.tw/',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 高雄市立圖書館 KSML V OK


def KSML(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_gov_crawler(
        driver,
        '高雄市立圖書館',
        'https://webpacx.ksml.edu.tw/',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 屏東縣公共圖書館 PTPL V OK


def PTPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_gov_crawler(
        driver,
        '屏東縣公共圖書館',
        'https://library.pthg.gov.tw/',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 花蓮縣公共圖書館 HLPL V


def HLPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_gov_crawler(
        driver,
        '花蓮縣公共圖書館',
        'https://center.hccc.gov.tw/',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 澎湖縣公共圖書館 PHPL V


def PHPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_gov_crawler(
        driver,
        '澎湖縣公共圖書館',
        'https://webpac.phlib.nat.gov.tw/',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立雲林科技大學 NYUST V


def NYUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_gov_crawler(
        driver,
        '國立雲林科技大學',
        'https://www.libwebpac.yuntech.edu.tw/',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國家電影及視聽文化中心 TFAI V


def TFAI(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_gov_crawler(
        driver,
        '國家電影及視聽文化中心',
        'https://lib.tfi.org.tw/',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# -----------------------------------------jsp系列-----------------------------------------------------
# webpac_jsp_crawler()
# 佛光|經國學院|宜大|中華|北基督|宏國德霖|嘉藥|臺北市|臺藝大|北市大|北醫|北商大|新竹市|新竹縣|苗栗縣
# 育達|仁德醫專|景文|致理|萬能|健行|明新|空大|中國科大|中教大|臺體|東海|靜宜|僑光|彰師
# 雲林縣|嘉義市|嘉義縣|南華|遠東|正修|美和|臺東|臺東縣|金門|金門縣
# def webpac_jsp_crawler(driver, org, org_url, ISBN):
#     try:
#         table = []

#         driver.get(org_url)
#         try:
#             select_ISBN_strategy(driver, 'search_field', 'ISBN')
#         except:
#             select_ISBN_strategy(driver, 'search_field', 'STANDARDNO')  # 北科大
#         search_ISBN(driver, ISBN, 'search_input')

#         # 一筆
#         if wait_for_element_present(driver, 'table.order'):
#             i = 0
#             while True:
#                 try:
#                     tgt = accurately_find_table_and_read_it(
#                         driver, 'table.order')
#                     tgt['圖書館'], tgt['連結'] = org, driver.current_url
#                     table.append(tgt)

#                     wait_for_element_clickable(driver, str(2+i), 2).click()
#                     i += 1
#                     time.sleep(0.5)
#                 except:
#                     break
#         # 多筆、零筆
#         elif wait_for_element_present(driver, 'iframe#leftFrame'):
#             iframe = driver.find_element_by_id('leftFrame')
#             driver.switch_to.frame(iframe)
#             time.sleep(1)  # 切換到 <frame> 需要時間，否則會無法讀取

#             # 判斷是不是＂零筆＂查詢結果
#             if wait_for_element_present(driver, '#totalpage').text == '0':
#                 print(f'在「{org}」找不到「{ISBN}」')
#                 return

#             # ＂多筆＂查詢結果
#             tgt_urls = []
#             anchors = driver.find_elements(By.LINK_TEXT, '詳細內容')
#             if anchors == []:
#                 anchors = driver.find_elements(By.LINK_TEXT, '內容')
#             for anchor in anchors:
#                 tgt_urls.append(anchor.get_attribute('href'))

#             for tgt_url in tgt_urls:
#                 driver.get(tgt_url)
#                 # 等待元素出現，如果出現，那麼抓取 DataFrame；如果沒出現，那麼跳出迴圈
#                 if wait_for_element_present(driver, 'table.order'):
#                     i = 0
#                     while True:
#                         try:
#                             tgt = accurately_find_table_and_read_it(
#                                 driver, 'table.order')
#                             tgt['圖書館'], tgt['連結'] = org, driver.current_url
#                             table.append(tgt)

#                             wait_for_element_clickable(
#                                 driver, str(2+i), 2).click()
#                             i += 1
#                             time.sleep(0.5)
#                         except:
#                             break
#                 else:
#                     continue
#         table = organize_columns(table)
#     except Exception as e:
#         print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
#         return
#     else:
#         return table


# 佛光大學 FGU V
def FGU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '佛光大學',
        "http://libils.fgu.edu.tw/webpacIndex.jsp",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 經國管理暨健康學院 CKU V


def CKU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '經國管理暨健康學院',
        "http://203.64.136.248/webpacIndex.jsp",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立宜蘭大學 NIU V


def NIU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立宜蘭大學',
        "https://lib.niu.edu.tw/webpacIndex.jsp",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中華科技大學 CUST V


def CUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '中華科技大學',
        "http://192.192.231.232/bookDetail.do?id=260965&nowid=3&resid=188809854",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺北基督學院 CCT V


def CCT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '臺北基督學院',
        "http://webpac.cct.edu.tw/webpacIndex.jsp",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 宏國德霖科技大學 HDUT V


def HDUT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '宏國德霖科技大學',
        "http://210.60.142.23/webpacIndex.jsp",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 嘉南藥理大學 CNU V


def CNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '嘉南藥理大學',
        "https://webpac.cnu.edu.tw/webpacIndex.jsp",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺北市立圖書館 TPML V


def TPML(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '臺北市立圖書館',
        'https://book.tpml.edu.tw/webpac/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺灣藝術大學 NTUA V


def NTUA(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立臺灣藝術大學',
        'http://webpac.ntua.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺北市立大學 UTaipei V


def UTaipei(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '臺北市立大學',
        'http://lib.utaipei.edu.tw/webpac/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺北科技大學 NTUT V


def NTUT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立臺北科技大學',
        'https://libholding.ntut.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺北醫學大學 TMU V


def TMU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '臺北醫學大學',
        'https://libelis.tmu.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺北商業大學 NTUB V


def NTUB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立臺北商業大學',
        'http://webpac.ntub.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 景文科技大學 JUST V


def JUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '景文科技大學',
        'https://jinwenlib.just.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 致理科技大學 CLUT V


def CLUT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '致理科技大學',
        'http://hylib.chihlee.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 萬能科技大學 VNU V


def VNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '萬能科技大學',
        'http://webpac.lib.vnu.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 健行科技大學 UCH V


def UCH(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '健行科技大學',
        'https://library.uch.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 明新科技大學 MUST V


def MUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '明新科技大學',
        'https://hylib.lib.must.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立空中大學 NOU V


def NOU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立空中大學',
        'https://hyweblib.nou.edu.tw/webpac/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 新竹市立圖書館 HCLIB V


def HCLIB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '新竹市立圖書館',
        'https://webpac.hcml.gov.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 新竹縣公共圖書館 HCPL V


def HCPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '新竹縣公共圖書館',
        'https://book.hchcc.gov.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 苗栗縣立圖書館 Miaoli V


def Miaoli(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '苗栗縣立圖書館',
        'https://webpac.miaoli.gov.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 育達科技大學 YDU V


def YDU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '育達科技大學',
        'http://120.106.11.155/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 仁德醫護管理專科學校 Jente V


def Jente(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '仁德醫護管理專科學校',
        'http://libopac.jente.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中國科技大學 CUTE V


def CUTE(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '中國科技大學',
        'https://webpac.cute.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺中教育大學 NTCU V


def NTCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立臺中教育大學',
        'http://webpac.lib.ntcu.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺灣體育運動大學 NTUS V


def NTUS(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立臺灣體育運動大學',
        'https://hylib.ntus.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 東海大學 THU V


def THU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '東海大學',
        'https://webpac.lib.thu.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 靜宜大學 PU V


def PU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '靜宜大學',
        'http://webpac.lib.pu.edu.tw/webpac/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 僑光科技大學 OCU V


def OCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '僑光科技大學',
        'http://lib.webpac.ocu.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立彰化師範大學 NCUE V


def NCUE(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立彰化師範大學',
        'https://book.ncue.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 雲林縣公共圖書館 YLCCB V


def YLCCB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '雲林縣公共圖書館',
        'http://library.ylccb.gov.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 嘉義市立圖書館 CYLIB X(進不去...)


def CYLIB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '嘉義市立圖書館',
        'http://library.cabcy.gov.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 嘉義縣圖書館 CYCPL V


def CYCPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '嘉義縣圖書館',
        'https://www.cycab.gov.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 南華大學 NHU V


def NHU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '南華大學',
        'http://hylib.nhu.edu.tw//webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 遠東科技大學 FEU V


def FEU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '遠東科技大學',
        'http://hy.lib.feu.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 正修科技大學 CSU V


def CSU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '正修科技大學',
        'https://webpac2.csu.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 美和科技大學 Meiho V


def Meiho(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '美和科技大學',
        'http://webpac.meiho.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺東大學 NTTU V


def NTTU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立臺東大學',
        'http://hylib.lib.nttu.edu.tw/webpac/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺東縣立圖書館 TTCPL V


def TTCPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '臺東縣立圖書館',
        'http://library.ccl.ttct.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立金門大學 NQU V


def NQU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '國立金門大學',
        'https://lib.nqu.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 金門縣立圖書館 KMCPL V


def KMCPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_jsp_crawler(
        driver,
        '金門縣立圖書館',
        'http://library.kmccc.edu.tw/webpacIndex.jsp',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ------------------------------------最簡單的那種------------------------------------------
# easy_crawler()
# 海大|台科大|台師大|中原|逢甲|朝陽|中山|高師|文藻|大仁|中央
def easy_crawler(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)
        search_ISBN(driver, ISBN, 'SEARCH')

        if not wait_for_element_present(driver, 'table.bibItems'):
            print(f'在「{org}」找不到「{ISBN}」')
            return

        table = accurately_find_table_and_read_it(driver, 'table.bibItems')
        table['圖書館'], table['連結'] = org, driver.current_url
        table = organize_columns(table)
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        return table

# 國立臺灣海洋大學 NTOU V


def NTOU(ISBN):
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(
            "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
        gs = gspread.authorize(creds)
        sheet = gs.open_by_url(
            'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
        worksheet = sheet.get_worksheet(0)
        driver = webdriver.Chrome(
            options=my_options, desired_capabilities=my_capabilities)

        gg = easy_crawler(
            driver,
            '國立臺灣海洋大學',
            'https://ocean.ntou.edu.tw/search*cht/i?SEARCH=',
            ISBN
        )

        driver.close()
        worksheet.append_rows(gg.values.tolist())
    except Exception as e:
        print(f'在 NTOU()，發生錯誤：「{e}」')
        return
    else:
        return gg

# 國立臺灣科技大學 NTUST V


def NTUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '國立臺灣科技大學',
        "https://sierra.lib.ntust.edu.tw/search*cht/i?SEARCH=",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺灣師範大學 NTNU V


def NTNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '國立臺灣師範大學',
        "https://opac.lib.ntnu.edu.tw/search*cht/i?SEARCH=",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中原大學 CYCU V


def CYCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '中原大學',
        "http://cylis.lib.cycu.edu.tw/search*cht/i",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 逢甲大學 FCU V


def FCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '逢甲大學',
        "https://innopac.lib.fcu.edu.tw/search*cht/i",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 朝陽科技大學 CYUT V


def CYUT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '朝陽科技大學',
        "https://millennium.lib.cyut.edu.tw/search*cht/i",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立中山大學 NSYSU V


def NSYSU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '國立中山大學',
        "https://dec.lib.nsysu.edu.tw/search*cht/i",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立高雄師範大學 NKNU V


def NKNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '國立高雄師範大學',
        "https://nknulib.nknu.edu.tw/search*cht/i",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 文藻外語大學 WZU V


def WZU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '文藻外語大學',
        "https://libpac.wzu.edu.tw/search*cht/i",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 大仁科技大學 Tajen V


def Tajen(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '大仁科技大學',
        "http://lib.tajen.edu.tw/search*cht/i",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立中央大學 NCU V


def NCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = easy_crawler(
        driver,
        '國立中央大學',
        "https://opac.lib.ncu.edu.tw/search*cht/i",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# -------------------------------------改版?------------------------------------------
# webpac_pro_crawler()
# 中研院|文化|輔仁|陽交大
def webpac_pro_crawler(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)
        select_ISBN_strategy(driver, 'searchtype', 'i')
        search_ISBN(driver, ISBN, 'searcharg')

        if not wait_for_element_present(driver, 'table.bibItems'):
            print(f'在「{org}」找不到「{ISBN}」')
            return

        table = accurately_find_table_and_read_it(driver, 'table.bibItems')
        table['圖書館'], table['連結'] = org, driver.current_url
        table = organize_columns(table)
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        return table

# 中央研究院 SINICA V


def SINICA(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_pro_crawler(
        driver,
        '中央研究院',
        "https://las.sinica.edu.tw/*cht",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中國文化大學 PCCU V


def PCCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_pro_crawler(
        driver,
        '中國文化大學',
        "https://webpac.pccu.edu.tw/*cht",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 輔仁大學 FJU V


def FJU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_pro_crawler(
        driver,
        '輔仁大學',
        "https://library.lib.fju.edu.tw/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立陽明交通大學 NYCU V


def NYCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_pro_crawler(
        driver,
        '國立陽明交通大學',
        "https://library.ym.edu.tw/screens/opacmenu_cht_s7.html",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# -----------------------------------ajax_page------------------------------------------------
# webpac_ajax_crawler()
# 新北市|高空大|屏大
def webpac_ajax_crawler(driver, org, org_url, ISBN):
    try:
        table = []
        driver.get(org_url)
        wait_for_element_clickable(driver, '進階查詢').click()  # 點擊＂進階查詢＂
        select_ISBN_strategy(driver, 'as_type_1', 'i', by=By.ID)
        search_ISBN(driver, ISBN, 'as_keyword_1', by=By.ID)

        org_url = org_url.replace('/search.cfm', '')
        if wait_for_element_present(driver, '詳細書目', by=By.LINK_TEXT):
            tgt_urls = []
            anchors = driver.find_elements_by_link_text('詳細書目')
            for anchor in anchors:
                tgt_urls.append(anchor.get_attribute('href'))

            for tgt_url in tgt_urls:
                mid = tgt_url.split('mid=')[-1].split('&')[0]
                ajax_page_url = f'{org_url}/ajax_page/get_content_area.cfm?mid={mid}&i_list_number=250&i_page=1&i_sory_by=1'
                tgt = pd.read_html(ajax_page_url, encoding='utf-8')[0]
                tgt['圖書館'], tgt['連結'] = org, tgt_url
                table.append(tgt)
        # 高雄市立空中大學、國立屏東大學才會遇到跳轉
        elif wait_for_element_present(driver, 'div.book-detail'):
            tgt_url = driver.current_url
            mid = tgt_url.split('mid=')[-1].split('&')[0]
            ajax_page_url = f'{org_url}/ajax_page/get_content_area.cfm?mid={mid}&i_list_number=250&i_page=1&i_sory_by=1'
            tgt = pd.read_html(ajax_page_url, encoding='utf-8')[0]
            tgt['圖書館'], tgt['連結'] = org, tgt_url
            table.append(tgt)
        table = organize_columns(table)
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        return table

# 新北市立圖書館 NTPC V


def NTPC(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_ajax_crawler(
        driver,
        '新北市立圖書館',
        "https://webpac.tphcc.gov.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 高雄市立空中大學 OUK V


def OUK(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_ajax_crawler(
        driver,
        '高雄市立空中大學',
        "https://webpac.ouk.edu.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立屏東大學 NPTU V


def NPTU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_ajax_crawler(
        driver,
        '國立屏東大學',
        "https://webpac.nptu.edu.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# -----------------------------------一直切iframe------------------------------------------------
# webpac_aspx_crawler()
# 樹德|首府|崑山|弘光|修平|華夏|真理|實踐|華梵|聯合
def webpac_aspx_crawler(driver, org, org_url, ISBN):
    try:
        print('（./INSTs.py/webpac_aspx_crawler()）執行這行1')
        table = []

        print('（./INSTs.py/webpac_aspx_crawler()）執行這行2')
        driver.get(org_url)

        print('（./INSTs.py/webpac_aspx_crawler()）執行這行3')
        time.sleep(1.5)
        print('（./INSTs.py/webpac_aspx_crawler()）執行這行4')
        iframe = wait_for_element_present(driver, 'default', by=By.NAME)
        print('（./INSTs.py/webpac_aspx_crawler()）執行這行5')
        driver.switch_to.frame(iframe)
        print('（./INSTs.py/webpac_aspx_crawler()）執行這行6')
        select_ISBN_strategy(
            driver, 'ctl00$ContentPlaceHolder1$ListBox1', 'Info000076')
        print('（./INSTs.py/webpac_aspx_crawler()）執行這行7')
        search_ISBN(driver, ISBN, 'ctl00$ContentPlaceHolder1$TextBox1')
        print('（./INSTs.py/webpac_aspx_crawler()）執行這行8')
        driver.switch_to.default_content()

        print('（./INSTs.py/webpac_aspx_crawler()）執行這行9')
        i = 0
        print('（./INSTs.py/webpac_aspx_crawler()）執行這行10')
        while True:
            print('（./INSTs.py/webpac_aspx_crawler()）執行這行11')
            time.sleep(1.5)
            print('（./INSTs.py/webpac_aspx_crawler()）執行這行12')
            iframe = wait_for_element_present(driver, 'default', by=By.NAME)
            print('（./INSTs.py/webpac_aspx_crawler()）執行這行13')
            driver.switch_to.frame(iframe)
            print('（./INSTs.py/webpac_aspx_crawler()）執行這行14')
            try:
                print('（./INSTs.py/webpac_aspx_crawler()）執行這行15')
                wait_for_element_present(
                    driver, f'//*[@id="ctl00_ContentPlaceHolder1_dg_ctl0{i+2}_lbtgcd2"]', by=By.XPATH).click()
            except:
                break
            driver.switch_to.default_content()

            time.sleep(1.5)
            iframe = wait_for_element_present(driver, 'default', by=By.NAME)
            driver.switch_to.frame(iframe)
            tgt = accurately_find_table_and_read_it(
                driver, '#ctl00_ContentPlaceHolder1_dg')
            tgt['圖書館'], tgt['連結'] = org, driver.current_url
            table.append(tgt)
            driver.switch_to.default_content()

            driver.back()
            i += 1

        try:
            table = organize_columns(table)
        except:
            print(f'在「{org}」找不到「{ISBN}」')
            return
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        return table

# 樹德科技大學 STU V


def STU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_aspx_crawler(
        driver,
        '樹德科技大學',
        "https://webpac.stu.edu.tw/webopac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 台灣首府大學 TSU V


def TSU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_aspx_crawler(
        driver,
        '台灣首府大學',
        "http://120.114.1.19/webopac/Jycx.aspx?dc=1&fc=1&n=7",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 崑山科技大學 KSU V


def KSU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_aspx_crawler(
        driver,
        '崑山科技大學',
        "https://weblis.lib.ksu.edu.tw/webopac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 弘光科技大學 HKU V


def HKU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_aspx_crawler(
        driver,
        '弘光科技大學',
        "https://webpac.hk.edu.tw/webopac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 修平科技大學 HUST V


def HUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_aspx_crawler(
        driver,
        '修平科技大學',
        "http://163.17.79.108/webopac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 華夏科技大學 HWH V


def HWH(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_aspx_crawler(
        driver,
        '華夏科技大學',
        "http://webopac.lib.hwh.edu.tw/webopac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 真理大學 AU V


def AU(ISBN):
    try:
        print('（./INSTs.py）執行這行1')
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        print('（./INSTs.py）執行這行2')
        creds = Credentials.from_service_account_file(
            "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
        print('（./INSTs.py）執行這行3')
        gs = gspread.authorize(creds)
        print('（./INSTs.py）執行這行4')
        sheet = gs.open_by_url(
            'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
        print('（./INSTs.py）執行這行5')
        worksheet = sheet.get_worksheet(0)
        print('（./INSTs.py）執行這行6')

        print('（./INSTs.py）執行這行7')
        driver = webdriver.Chrome(
            options=my_options, desired_capabilities=my_capabilities)
        print('（./INSTs.py）執行這行8')

        print('（./INSTs.py）執行這行9')
        gg = webpac_aspx_crawler(
            driver,
            '真理大學',
            "https://lib.au.edu.tw/webopac/",
            ISBN
        )

        driver.close()
        worksheet.append_rows(gg.values.tolist())
    except Exception as e:
        print(f'函式 AU() 發生錯誤：{e}')
        return
    else:
        return gg

# 實踐大學 USC V


def USC(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_aspx_crawler(
        driver,
        '實踐大學',
        "https://webopac.usc.edu.tw/webopac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 華梵大學 HFU V


def HFU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_aspx_crawler(
        driver,
        '華梵大學',
        "http://210.59.113.12/webopac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立聯合大學 NUU V


def NUU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_aspx_crawler(
        driver,
        '國立聯合大學',
        "http://210.60.171.7/webopac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# -----------------------------------按館藏地展開table------------------------------------------------
# uhtbin_crawler()
# 國北護|大同|國體大
def uhtbin_crawler(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)
        try:
            select_ISBN_strategy(driver, 'srchfield1',
                                 'GENERAL^SUBJECT^GENERAL^^所有欄位')
        except:
            select_ISBN_strategy(driver, 'srchfield1',
                                 '020^SUBJECT^SERIES^Title Processing^ISBN')
        search_ISBN(driver, ISBN, 'searchdata1')

        if '未在任何圖書館找到' in driver.find_element(By.CSS_SELECTOR, 'table').text:
            print(f'在「{org}」找不到「{ISBN}」')
            return

        table = accurately_find_table_and_read_it(driver, 'table')

        # 特殊處理
        table.drop([0, 1, 2], inplace=True)
        table.drop([1, 2, 4], axis='columns', inplace=True)
        table.rename(columns={0: '索書號', 3: '館藏狀態'}, inplace=True)
        table['圖書館'], table['連結'], table['館藏地'] = org, driver.current_url, table['館藏狀態']

        table = organize_columns(table)
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        return table

# 國立臺北護理健康大學 NTUNHS V


def NTUNHS(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = uhtbin_crawler(
        driver,
        '國立臺北護理健康大學',
        "http://140.131.94.8/uhtbin/webcat",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 大同大學 TTU V


def TTU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = uhtbin_crawler(
        driver,
        '大同大學',
        "http://140.129.23.14/uhtbin/webcat",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立體育大學 NTSU V


def NTSU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = uhtbin_crawler(
        driver,
        '國立體育大學',
        "http://192.83.181.243/uhtbin/webcat",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# --------------------------------------醜得清新脫俗------------------------------------------------
# ugly_crawler()
# 連江縣|開南
def ugly_crawler(driver, org, org_url, ISBN):
    try:
        table = []
        driver.get(org_url)
        search_ISBN(driver, ISBN, 'ISBN')

        if wait_for_element_present(driver, '重新查詢', by=By.LINK_TEXT):
            print(f'在「{org}」找不到「{ISBN}」')
            return

        tgt = accurately_find_table_and_read_it(driver, 'table', -2)
        tgt['圖書館'], tgt['連結'] = org, driver.current_url
        table.append(tgt)

        table = organize_columns(table)
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        return table

# 連江縣公共圖書館 Matsu V


def Matsu(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = ugly_crawler(
        driver,
        '連江縣公共圖書館',
        "http://210.63.206.76/Webpac2/msearch.dll/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 開南大學 KNU V


def KNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = ugly_crawler(
        driver,
        '開南大學',
        "http://www.lib.knu.edu.tw/Webpac2/msearch.dll/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ---------------------------------------藍藍放大鏡------------------------------------------------
# toread_crawler()
# 東專|醒吾|彰化縣|高醫|虎科|聖約翰|東南|新生|崇仁|元培
def toread_crawler(driver, org, org_url, ISBN):
    try:
        table = []

        driver.get(org_url)
        search_ISBN(driver, ISBN, 'q')

        if not wait_for_element_present(driver, 'div#results'):
            print(f'在{org}裡，沒有《{ISBN}》')
            return

        # 有 div#results，找出所有的＂書目資料＂的網址
        tgt_urls = []
        anchors = driver.find_elements(By.CSS_SELECTOR, 'div.img_reslt > a')
        for anchor in anchors:
            tgt_urls.append(anchor.get_attribute('href'))

        # 進入各個＂書目資料＂爬取表格
        for tgt_url in tgt_urls:
            driver.get(tgt_url)

            # 電子書沒有 table
            if not wait_for_element_present(driver, 'table.gridTable'):
                continue

            tgt = accurately_find_table_and_read_it(driver, 'table.gridTable')
            tgt['圖書館'], tgt['連結'] = org, tgt_url

            # 以下兩行，是＂彰化縣公共圖書館＂有多餘的 row，須要特別篩選調 NaN
            try:
                tgt = tgt.dropna(subset=['典藏地名稱'])
            except:  # 國立高雄大學沒有這個狀況
                pass
            tgt.reset_index(drop=True, inplace=True)

            table.append(tgt)

            # 換頁：書沒有那麼多吧 XD，土法煉鋼法
            i = 0
            while True:
                try:
                    wait_for_element_clickable(driver, str(2+i)).click()
                    time.sleep(2.5)
                    tgt = accurately_find_table_and_read_it(
                        driver, 'table.gridTable')
                    tgt['圖書館'], tgt['連結'] = org, tgt_url

                    # 以下兩行，是＂彰化縣公共圖書館＂有多餘的 row，須要特別篩選調 NaN
                    try:
                        tgt = tgt.dropna(subset=['典藏地名稱'])
                    except:  # 國立高雄大學沒有這個狀況
                        pass
                    tgt.reset_index(drop=True, inplace=True)

                    table.append(tgt)
                    i += 1
                except:
                    break
        table = organize_columns(table)
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        return table

# ------------國立臺東專科學校-------------


def NTC(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '國立臺東專科學校',
        'https://library.ntc.edu.tw/toread/opac',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# ------------醒吾科技大學-------------


def HWU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        org='醒吾科技大學',
        org_url="http://120.102.129.237/toread/opac",
        ISBN=ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 彰化縣公共圖書館 CHPL V


def CHPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '彰化縣公共圖書館',
        "https://library.toread.bocach.gov.tw/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 高雄醫學大學 KMU V


def KMU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '高雄醫學大學',
        "https://toread.kmu.edu.tw/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立虎尾科技大學 NFU V


def NFU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '國立虎尾科技大學',
        "https://toread.lib.nfu.edu.tw/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 聖約翰科技大學 SJU V


def SJU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '聖約翰科技大學',
        "http://163.21.66.231:8080/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 東南科技大學 TNU V


def TNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '東南科技大學',
        "http://140.129.140.176/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 新生醫護管理專科學校 HSC V


def HSC(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '新生醫護管理專科學校',
        "http://163.25.34.60:8080/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 崇仁醫護管理專科學校 CJC V


def CJC(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '崇仁醫護管理專科學校',
        "http://toread.cjc.edu.tw/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 元培醫事科技大學 YPU V


def YPU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '元培醫事科技大學',
        "http://120.106.195.31/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 嶺東科技大學 LTU V


def LTU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '嶺東科技大學',
        "http://192.192.100.39/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 明道大學 MDU V


def MDU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '明道大學',
        "http://210.60.94.144/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 大葉大學 DYU V


def DYU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    toread_crawler(
        driver,
        '大葉大學',
        "http://webpac.dyu.edu.tw/toread311_DYU/opac/Search.page",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 建國科技大學 CTU V


def CTU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '建國科技大學',
        "https://webpac.lib.ctu.edu.tw/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 南開科技大學 NKUT V


def NKUT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '南開科技大學',
        "http://webpac.nkut.edu.tw/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立高雄大學 NUK V


def NUK(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = toread_crawler(
        driver,
        '國立高雄大學',
        "https://libopac.nuk.edu.tw/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立東華大學 NDHU V


def NDHU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = toread_crawler(
        driver,
        '國立東華大學',
        "https://books-lib.ndhu.edu.tw/toread/opac",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ---------------------------------------Webpac2.0------------------------------------------------
# webpac_two_cralwer()
# 北藝大|勤益|義守|中山醫|國衛院
def webpac_two_cralwer(driver, org, org_url, ISBN):
    try:
        tgt_url = f'{org_url}search/?q={ISBN}&field=isn&op=AND&type='
        driver.get(tgt_url)

        wait_for_element_clickable(
            driver, '/html/body/div/div[1]/div[2]/div/div/div[2]/div[3]/div[1]/div[3]/div/ul/li/div/div[2]/h3/a', waiting_time=15, by=By.XPATH).click()

        table = accurately_find_table_and_read_it(
            driver, '#LocalHolding > table')
        table['圖書館'], table['連結'] = org, driver.current_url

        # 特殊狀況：國家衛生研究院
        if 'http://webpac.nhri.edu.tw/webpac/' in org_url:
            table.rename(
                columns={'館藏狀態': 'wow', '狀態／到期日': '館藏狀態'}, inplace=True)

        table = organize_columns(table)
    except:
        print(f'在「{org}」找不到「{ISBN}」')
        return
    else:
        return table

# 國立臺北藝術大學 TNUA V


def TNUA(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_two_cralwer(
        driver,
        '國立臺北藝術大學',
        "http://203.64.5.158/webpac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立勤益科技大學 NCUT V


def NCUT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_two_cralwer(
        driver,
        '國立勤益科技大學',
        "http://140.128.95.172/webpac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 義守大學 ISU V


def ISU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_two_cralwer(
        driver,
        '義守大學',
        "http://webpac.isu.edu.tw/webpac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中山醫學大學 CSMU V


def CSMU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_two_cralwer(
        driver,
        '中山醫學大學',
        "http://140.128.138.208/webpac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國家衛生研究院 NHRI V


def NHRI(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_two_cralwer(
        driver,
        '國家衛生研究院',
        "http://webpac.nhri.edu.tw/webpac/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ------------------------------------cfm------------------------------------------
# webpac_cfm_crawler()
# 北大|城市科大|德明|龍華|臺中市|中國醫|亞洲|臺南市|慈濟|澎科
def webpac_cfm_crawler(driver, org, org_url, ISBN):
    try:
        table = []
        table_position = 'table.list_border'
        if 'ntpu' in org_url:  # ＂國立臺北大學＂的 table_position 是 table.book_location
            table_position = 'div.book_location > table.list'

        driver.get(org_url)

        wait_for_element_clickable(driver, '進階檢索').click()
        time.sleep(1)
        select_ISBN_strategy(driver, 'as_type_1', 'i')
        search_ISBN(driver, ISBN, 'as_keyword_1')

        # Case1. 是否 driver 在＂書目資料＂的頁面？
        if wait_for_element_present(driver, 'div.info_box', 10):
            table += crawl_all_tables_on_page(driver,
                                              table_position, org, driver.current_url)

        # Case2. 是否 driver 在＂查詢結果＂的頁面？且有搜尋結果。
        elif wait_for_element_present(driver, 'div#list'):
            tgt_urls = get_all_tgt_urls(driver, '詳細書目')

            for tgt_url in tgt_urls:
                driver.get(tgt_url)

                # 是否 driver 在＂書目資料＂的頁面？
                if wait_for_element_present(driver, 'div.info_box'):
                    table += crawl_all_tables_on_page(driver,
                                                      table_position, org, driver.current_url)

        # Case3. 無搜尋結果，driver 會在＂查詢結果＂，並顯示訊息「無符合館藏資料」
        elif wait_for_element_present(driver, 'div.msg'):
            print(f'在「{org}」找不到「{ISBN}」')
            return

        # Case. 抓不到 table，離開 function
        if table == []:
            print(f'在「{org}」爬取「{ISBN}」時，抓取不到 table')
            return

    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return

    else:
        table = organize_columns(table)
        return table

# 國立臺北大學 NTPU X(卡在進table前的頁面)


def NTPU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '國立臺北大學',
        "http://webpac.lib.ntpu.edu.tw/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺北城市科技大學 TPCU V


def TPCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '臺北城市科技大學',
        "http://120.102.52.73/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 德明財經科技大學 TMUST V


def TMUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '德明財經科技大學',
        "http://140.131.140.11/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 龍華科技大學 LHU V


def LHU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '龍華科技大學',
        "https://webpac.lhu.edu.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺中市立圖書館 TCPL V


def TCPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '臺中市立圖書館',
        "https://ipac.library.taichung.gov.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中國醫藥大學 CMU V


def CMU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '中國醫藥大學',
        "http://weblis.cmu.edu.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 亞洲大學 Asia V


def Asia(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '亞洲大學',
        "http://aulib.asia.edu.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺南市立圖書館 TNPL V


def TNPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '臺南市立圖書館',
        "https://lib.tnml.tn.edu.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 慈濟大學 TCU V


def TCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '慈濟大學',
        "http://www.webpac.tcu.edu.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立澎湖科技大學 NPU V


def NPU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = webpac_cfm_crawler(
        driver,
        '國立澎湖科技大學',
        "https://inspire.npu.edu.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ------------------------------被獨立出來的基隆---------------------------------------
def 基隆市公共圖書館(driver, org, org_url, ISBN):
    try:
        # 進入＂搜尋主頁＂
        driver.get(org_url)
        # 等待點擊＂進階查詢＂按鈕，接著點擊
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.LINK_TEXT, '進階檢索'))).click()
        time.sleep(2)  # JavaScript 動畫，強制等待
        # 等待定位＂下拉式選單＂，選擇以 ISBN 方式搜尋
        search_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'as_type_1')))
        select = Select(search_field)
        select.select_by_value('i')
        # 定位＂搜尋欄＂，輸入 ISBN
        search_input = driver.find_element_by_id('as_keyword_1')
        search_input.send_keys(ISBN)
        search_input.send_keys(Keys.ENTER)

        time.sleep(8)  # 基隆的系統太詭異了，強制等待
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = len(soup.find_all("div", "list_box"))
        if results < 2:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table.list.list_border")))
            time.sleep(2)
            table = pd.read_html(driver.page_source)[0]
        else:
            table = []
            for li in soup.find_all("div", "list_box"):
                url_temp = "https://webpac.klccab.gov.tw/webpac/" + li.find(
                    "a", "btn")["href"]
                driver.get(url_temp)
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "table.list.list_border")))
                time.sleep(2)
                table.append(
                    pd.read_html(driver.page_source, encoding="utf-8")[0])
            table = pd.concat(table, axis=0, ignore_index=True)
        table['圖書館'], table['連結'] = org, driver.current_url
        table = organize_columns(table)
        return table
    except:
        print(f'《{ISBN}》在「{org_url}」無法爬取')

# 基隆市公共圖書館 KLCCAB X(無館藏資料時會掛掉)


def KLCCAB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = 基隆市公共圖書館(
        driver,
        '基隆市公共圖書館',
        "https://webpac.klccab.gov.tw/webpac/search.cfm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ------------------------------------難形容的特殊------------------------------------------
# sirsidynix_crawler()
# 中科大|南投縣|南藝大
def sirsidynix_crawler(driver, org, org_url, ISBN):
    try:
        table = []

        driver.get(org_url)
        select_ISBN_strategy(driver, 'restrictionDropDown',
                             'false|||ISBN|||ISBN（國際標準書號）')
        search_ISBN(driver, ISBN, 'q')

        # ＂書目資料＂
        if wait_for_element_present(driver, 'div.detailItems'):
            time.sleep(0.5)

            tgt = accurately_find_table_and_read_it(
                driver, 'table.detailItemTable')

            if 'ntit' in org_url:
                tgt['館藏地'] = tgt['圖書館'].str.rsplit('-', expand=True)[2]
            elif 'tnnua' in org_url:
                tgt['館藏地'] = tgt['狀態'].str.rsplit('-', expand=True)[1]
            tgt['圖書館'], tgt['連結'] = org, driver.current_url
            table.append(tgt)
        # ＂查詢結果＂
        elif wait_for_element_present(driver, 'div#results_wrapper'):
            wait_for_element_present(driver, 'a.hideIE').click()

            if wait_for_element_present(driver, 'div.detailItems'):
                while True:
                    time.sleep(0.5)

                    tgt = accurately_find_table_and_read_it(
                        driver, 'table.detailItemTable', -1)

                    if 'ntit' in org_url:
                        tgt['館藏地'] = tgt['圖書館'].str.rsplit('-', expand=True)[2]
                    elif 'tnnua' in org_url:
                        tgt['館藏地'] = tgt['狀態'].str.rsplit('-', expand=True)[1]

                    tgt['圖書館'], tgt['連結'] = org, driver.current_url
                    table.append(tgt)

                    try:
                        wait_for_elements_present(
                            driver, '.nextArrowRight')[-1].click()
                        time.sleep(3.5)
                    except:
                        break
        else:
            print(f'在「{org}」找不到「{ISBN}」')
            return

    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return

    else:
        table = organize_columns(table)
        return table

# 國立臺中科技大學 NUTC


def NUTC(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = sirsidynix_crawler(
        driver,
        '國立臺中科技大學',
        "https://ntit.ent.sirsidynix.net/client/zh_TW/NUTC",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 南投縣圖書館 NTCPL


def NTCPL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = sirsidynix_crawler(
        driver,
        '南投縣圖書館',
        'https://nccc.ent.sirsi.net/client/zh_TW/main',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺南藝術大學 TNNUA


def TNNUA(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = sirsidynix_crawler(
        driver,
        '國立臺南藝術大學',
        'https://tnnua.ent.sirsi.net/client/zh_TW/tnnua/?',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ------------------------------------文化局旗下------------------------------------------
# moc_thm_crawler()
# 臺史館|臺文館|史前館|
def moc_thm_crawler(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)

        select_ISBN_strategy(driver, 'find_code', 'ISBN')
        search_ISBN(driver, ISBN, 'request')

        try:
            wait_for_element_present(
                driver, '/html/body/form/table[1]/tbody/tr[8]/td[3]/a', by=By.XPATH).click()
        except:
            print(f'在「{org}」找不到「{ISBN}」')
            return
        wait_for_element_present(
            driver, '/html/body/table[9]/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/a', by=By.XPATH).click()

        table = accurately_find_table_and_read_it(driver, 'table', -2)
        table['圖書館'], table['連結'] = org, driver.current_url
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        table = organize_columns(table)
        return table

# 國立臺灣史前文化博物館 NMP


def NMP(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = moc_thm_crawler(
        driver,
        '國立臺灣史前文化博物館',
        "https://lib.moc.gov.tw/F?func=find-d-0&local_base=THM04",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ---------------------------------被獨立出來的國圖----------------------------------------
def 國家圖書館(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)
        select_ISBN_strategy(driver, 'find_code', 'ISBN')
        search_ISBN(driver, ISBN, 'request')

        # 點擊＂書在哪裡(請點選)＂，進入＂書目資料＂
        wait_for_element_clickable(driver, '書在哪裡(請點選)').click()

        table = accurately_find_table_and_read_it(driver, 'table', -2)
        if 0 in table.columns:
            print(f'在「{org}」找不到「{ISBN}」')
            return
        table['圖書館'], table['連結'] = org, driver.current_url
        table = organize_columns(table)
    except Exception as e:
        # 沒有物件可以 click，表示＂零筆＂搜尋結果
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    return table

# 國家圖書館 NCL V


def NCL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = 國家圖書館(
        driver,
        '國家圖書館',
        "https://aleweb.ncl.edu.tw/F",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ---------------------------------被獨立出來的世新----------------------------------------
def 世新大學(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)
        search_ISBN(driver, ISBN, 'q')

        table = accurately_find_table_and_read_it(driver, '#holdingst')
        table['圖書館'], table['連結'] = org, driver.current_url
        table = organize_columns(table)
    except Exception as e:
        print(f'在「{org}」找不到「{ISBN}」')
        return
    else:
        return table

# 世新大學 SHU V


def SHU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = 世新大學(
        driver,
        '世新大學',
        "https://koha.shu.edu.tw/",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# 台北海洋科技大學 TUMT V
def TUMT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = 台北海洋科技大學(
        driver,
        '台北海洋科技大學',
        'http://140.129.253.4/webopac7/sim_data2.php?pagerows=15&orderby=BRN&pageno=1&bn=',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ---------------------------------被獨立出來的敏實科大----------------------------------------
def 敏實科技大學(driver, org, org_url, ISBN):
    try:
        table = []

        driver.get(org_url)
        search_ISBN(driver, ISBN, 'DB.IN1')

        if wait_for_element_present(driver, 'span.sm9'):
            search_result_message = BeautifulSoup(
                driver.page_source, 'html.parser').find_all('span', 'sm9')[-2].text
            search_result_regex = re.compile(r'\d')
            mo = search_result_regex.search(search_result_message)
            if int(mo.group()) == 0:
                print(f'在「{org}」找不到「{ISBN}」')
                return

        driver.find_elements_by_tag_name('a')[1].click()

        tgt = accurately_find_table_and_read_it(driver, 'table', -1)
        tgt['圖書館'], tgt['連結'] = org, driver.current_url
        table.append(tgt)
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        table = organize_columns(table)
        return table

# 敏實科技大學 MITUST


def MITUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = 敏實科技大學(
        driver,
        '敏實科技大學',
        'http://120.105.200.52/xsearch-b.html',
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ------------------------------------------Primo-----------------------------------------
# primo_crawler()
# 臺大|政大|淡江|銘傳|東吳
def primo_crawler(driver, org, url_front, ISBN, url_behind, tcn):
    url = url_front + ISBN + url_behind
    primo_lst = []

    try:
        # 進入《館藏系統》頁面
        driver.get(url)

        try:  # 開始爬蟲
            editions = wait_for_elements_present(
                driver, 'item-title', 20, By.CLASS_NAME)
            print("進入搜尋")
            if len(editions) > 1:  # 如果最外面有兩個版本(默認點進去不會再分版本了啦)(ex.政大 9789861371955)，直接交給下面處理
                pass
            else:  # 如果最外面只有一個版本，那有可能點進去還有再分，先click進去，再分一個版本跟多個版本的狀況
                time.sleep(5)
                editions[0].click()
                if org == "國立政治大學":
                    try:
                        editions = driver.find_elements_by_class_name(
                            'item-title', 10)  # 這時候是第二層的分版本了！(ex.政大 9789869109321)
                    except:
                        pass

            try:  # 先找叉叉確定是不是在最裡層了
                back_check = wait_for_element_present(
                    driver, "md-icon-button.close-button.full-view-navigation.md-button.md-primoExplore-theme.md-ink-ripple")
                print("找叉叉成功，準備找表格")
            except:
                back_check = None
                print("沒有叉叉，進版本迴圈")
            if back_check == None:  # 多個版本才要再跑迴圈(找不到叉叉代表不在最裡面，可知不是一個版本)
                for i in range(0, len(editions)):  # 有幾個版本就跑幾次，不管哪一層版本都適用
                    time.sleep(5)
                    into = editions[i].click()
                    print("版本" + str(i))
                    if org == "國立屏東科技大學" or org == "國立高雄餐旅大學":
                        primo_lst += primo_two_finding(driver, org)
                    else:
                        primo_lst += primo_finding(driver, org, tcn)
                    try:
                        back2 = wait_for_element_clickable(
                            driver, "md-icon-button.close-button.full-view-navigation.md-button.md-primoExplore-theme.md-ink-ripple").click()
                    except:
                        back2 = None

            else:  # 如果只有一個版本(有叉叉的意思)，那前面已經click過了不能再做
                if org == "國立屏東科技大學" or org == "國立高雄餐旅大學":
                    primo_lst += primo_two_finding(driver, org)
                    print(primo_lst)
                else:
                    primo_lst += primo_finding(driver, org, tcn)
                    print(primo_lst)
        except:
            print("爬蟲失敗")
    except:
        print("沒進網址")
    table = pd.DataFrame(primo_lst)
    table.rename(columns={0: '圖書館', 1: '館藏地', 2: '索書號',
                 3: '館藏狀態', 4: '連結'}, inplace=True)
    return table

# 國立臺灣大學 NTU V


def NTU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = primo_crawler(
        driver,
        '國立臺灣大學',
        "https://ntu.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
        ISBN,
        "&tab=Everything&search_scope=MyInst_and_CI&vid=886NTU_INST:886NTU_INST&offset=0",
        "layout-align-space-between-center.layout-row.flex-100"
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立政治大學 NCCU V


def NCCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = primo_crawler(
        driver,
        '國立政治大學',
        "https://nccu.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
        ISBN,
        "&tab=Everything&search_scope=MyInst_and_CI&vid=886NCCU_INST:886NCCU_INST",
        "layout-align-space-between-center.layout-row.flex-100"
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 淡江大學 TKU V OK


def TKU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = primo_crawler(
        driver,
        '淡江大學',
        "https://uco-network.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
        ISBN,
        "&tab=Everything&search_scope=MyInst_and_CI&vid=886UCO_TKU:886TKU_INST&lang=zh-tw&offset=0",
        "neutralized-button.layout-full-width.layout-display-flex.md-button.md-ink-ripple.layout-row"
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 銘傳大學 MCU V(索書號是空的) OK


def MCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = primo_crawler(
        driver,
        '銘傳大學',
        "https://uco-mcu.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
        ISBN,
        "&tab=Everything&search_scope=MyInst_and_CI&vid=886UCO_MCU:886MCU_INST&lang=zh-tw&offset=0",
        "md-2-line.md-no-proxy._md"
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 東吳大學 SCU V OK


def SCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = primo_crawler(
        driver,
        '東吳大學',
        "https://uco-scu.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
        ISBN,
        "&tab=Everything&search_scope=MyInst_and_CI&vid=886UCO_SCU:886SCU_INST&lang=zh-tw&offset=0",
        "md-2-line.md-no-proxy._md"
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立高雄科技大學 NKUST V OK


def NKUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = primo_crawler(
        driver,
        '國立高雄科技大學',
        "https://nkust.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
        ISBN,
        "&tab=Everything&search_scope=MyInst_and_CI&vid=886NKUST_INST:86NKUST&lang=zh-tw&offset=0,",
        "layout-align-space-between-center.layout-row.flex-100"
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ------------------------------------------Primo v2-----------------------------------------
# primo_two_crawler()
# 屏科大|高餐|高科大
def primo_two_crawler(driver, org, url_front, ISBN, url_behind):
    url = url_front + ISBN + url_behind
    primo_two_lst = []

    def primo_two_finding(org):  # 爬資訊的def
        sub_df_lst = []
        time.sleep(2)
        try:
            back = driver.find_element_by_css_selector(
                ".tab-header .back-button.button-with-icon.zero-margin.md-button.md-primoExplore-theme.md-ink-ripple")
        except:
            back = None
        if back != None:
            back.click()

        similar_xpath = "/html/body/primo-explore/div[3]/div/md-dialog/md-dialog-content/sticky-scroll/prm-full-view/div/div/div[2]/div/div[1]/div[4]/div/prm-full-view-service-container/div[2]/div/prm-opac/md-tabs/md-tabs-content-wrapper/md-tab-content[2]/div/md-content/prm-location-items/div[2]/div[1]/p/span["
        status = driver.find_element_by_xpath(similar_xpath + "1]")
        place = driver.find_element_by_xpath(similar_xpath + "3]")
        num = driver.find_element_by_xpath(similar_xpath + "5]")

        now_url = driver.current_url
        number = num.text.replace("(", "").replace(")", "")
        new_row = [org, place.text, number, status.text, now_url]
        sub_df_lst.append(new_row)

        return sub_df_lst

    try:
        # 進入《館藏系統》頁面
        driver.get(url)
        # 等待＂進階查詢的按鈕＂直到出現：click
        time.sleep(15)

        try:  # 開始爬蟲
            editions = driver.find_elements_by_class_name('item-title', 20)
            if len(editions) > 1:  # 如果最外面有兩x`個版本(默認點進去不會再分版本了啦)(ex.政大 9789861371955)，直接交給下面處理
                pass
            else:  # 如果最外面只有一個版本，那有可能點進去還有再分，先click進去，再分一個版本跟多個版本的狀況
                time.sleep(2)
                editions[0].click()
                time.sleep(5)
                editions = driver.find_elements_by_class_name(
                    'item-title', 20)  # 這時候是第二層的分版本了！(ex.政大 9789869109321)

            try:  # 先找叉叉確定是不是在最裡層了
                back_check = driver.find_element_by_class_name(
                    "md-icon-button.close-button.full-view-navigation.md-button.md-primoExplore-theme.md-ink-ripple")
            except:
                back_check = None
            if back_check == None:  # 多個版本才要再跑迴圈(找不到叉叉代表不在最裡面，可知不是一個版本)
                for i in range(0, len(editions)):  # 有幾個版本就跑幾次，不管哪一層版本都適用
                    into = editions[i].click()
                    time.sleep(3)
                    primo_two_lst += primo_two_finding(org)
                    try:
                        back2 = driver.find_element_by_class_name(
                            "md-icon-button.close-button.full-view-navigation.md-button.md-primoExplore-theme.md-ink-ripple").click()
                    except:
                        back2 = None

            else:  # 如果只有一個版本(有叉叉的意思)，那前面已經click過了不能再做
                time.sleep(3)
                primo_two_lst += primo_two_finding(org)
        except:
            pass
    except:
        pass

    table = pd.DataFrame(primo_two_lst)
    table.rename(columns={0: '圖書館', 1: '館藏地', 2: '索書號',
                 3: '館藏狀態', 4: '連結'}, inplace=True)
    return table

# 國立屏東科技大學 NPUST V


def NPUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = primo_crawler(
        driver,
        '國立屏東科技大學',
        "http://primo.lib.npust.edu.tw/primo-explore/search?institution=NPUST&vid=NPUST&tab=default_tab&search_scope=SearchAll&mode=basic&query=any,contains,",
        ISBN,
        "&displayMode=full&bulkSize=10&highlight=true&dum=true&lang=zh_TW&displayField=all&pcAvailabiltyMode=true",
        ""
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立高雄餐旅大學 NKUHT V


def NKUHT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = primo_crawler(
        driver,
        '國立高雄餐旅大學',
        "https://find.nkuht.edu.tw/primo-explore/search?query=any,contains,",
        ISBN,
        "&tab=default_tab&search_scope=%E6%9F%A5%E9%A4%A8%E8%97%8F&vid=NKUHT_N&offset=0",
        ""
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ------------------------------------------綠點點----------------------------------------------
# primo_greendot_crawler()
# 長庚|中正|長榮
def primo_greendot_crawler(driver, org, url_front, ISBN, url_behind):
    url = url_front + ISBN + url_behind
    primo_greendot_lst = []

    try:
        driver.get(url)
        try:  # 只有一個版本

            place_click = wait_for_element_clickable(
                driver, 'exlidResult0-LocationsTab', 10, By.ID).click()

            primo_greendot_lst += primo_greendot_finding(driver, org)
        except:  # 有多個版本，所以要點進去再做
            manyeditions = wait_for_element_clickable(
                driver, 'titleLink', 10, By.ID).click()
            for i in range(1, 10):  # 假設有十個版本吧
                try:
                    id = 'exlidResult' + str(i) + '-LocationsTab'
                    place2_click = wait_for_element_clickable(
                        driver, id, 15, By.ID).click()
                    primo_greendot_lst += primo_greendot_finding(driver, org)
                except:
                    continue
    except:
        pass
    table = pd.DataFrame(primo_greendot_lst)
    table.rename(columns={0: '圖書館', 1: '館藏地', 2: '索書號',
                 3: '館藏狀態', 4: '連結'}, inplace=True)
    return table

# 長庚大學 CGU V OK


def CGU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = primo_greendot_crawler(
        driver,
        '長庚大學',
        "https://primo.lib.cgu.edu.tw/primo_library/libweb/action/search.do?fn=search&ct=search&initialSearch=true&mode=Advanced&tab=default_tab&indx=1&dum=true&srt=rank&vid=CGU&frbg=&tb=t&vl%2812508471UI0%29=isbn&vl%2812508471UI0%29=title&vl%2812508471UI0%29=isbn&vl%281UIStartWith0%29=contains&vl%28freeText0%29=",
        ISBN,
        "&vl%28boolOperator0%29=AND&vl%2812508474UI1%29=creator&vl%2812508474UI1%29=title&vl%2812508474UI1%29=creator&vl%281UIStartWith1%29=contains&vl%28freeText1%29=&vl%28boolOperator1%29=AND&vl%2812508470UI2%29=any&vl%2812508470UI2%29=title&vl%2812508470UI2%29=any&vl%281UIStartWith2%29=contains&vl%28freeText2%29=&vl%28boolOperator2%29=AND&vl%2812626940UI3%29=any&vl%2812626940UI3%29=title&vl%2812626940UI3%29=any&vl%281UIStartWith3%29=contains&vl%28freeText3%29=&vl%28boolOperator3%29=AND&vl%28D2240502UI4%29=all_items&vl%2853081356UI5%29=all_items&vl%28D2240500UI6%29=all_items&Submit=%E6%AA%A2%E7%B4%A2"
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立中正大學 CCU V OK


def CCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = primo_greendot_crawler(
        driver,
        '國立中正大學',
        "http://primo.lib.ccu.edu.tw/primo_library/libweb/action/search.do?fn=search&ct=search&initialSearch=true&mode=Advanced&tab=default_tab&indx=1&dum=true&srt=rank&vid=CCU&frbg=&tb=t&vl%28256032279UI0%29=isbn&vl%28256032279UI0%29=title&vl%28256032279UI0%29=any&vl%281UIStartWith0%29=contains&vl%28freeText0%29=",
        ISBN,
        "&vl%282853831UI0%29=AND&vl%28256032278UI1%29=any&vl%28256032278UI1%29=title&vl%28256032278UI1%29=any&vl%281UIStartWith1%29=contains&vl%28freeText1%29=&vl%282853829UI1%29=AND&vl%28256032320UI2%29=any&vl%28256032320UI2%29=title&vl%28256032320UI2%29=any&vl%281UIStartWith2%29=contains&vl%28freeText2%29=&vl%282853831UI2%29=AND&vl%28D2853835UI3%29=all_items&vl%28256032346UI4%29=all_items&vl%28D2853833UI5%29=all_items&Submit=%E6%AA%A2%E7%B4%A2"
    )
    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 長榮大學 CJCU V OK


def CJCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = primo_greendot_crawler(
        driver,
        '長榮大學',
        "http://discovery.lib.cjcu.edu.tw:1701/primo_library/libweb/action/search.do?fn=search&ct=search&initialSearch=true&mode=Advanced&tab=ils_pc&indx=1&dum=true&srt=rank&vid=CJCU&frbg=&tb=t&vl%28D2348462UI0%29=any&vl%28D2348462UI0%29=title&vl%28D2348462UI0%29=any&vl%281UIStartWith0%29=contains&vl%28freeText0%29=,",
        ISBN,
        "&vl%28boolOperator0%29=AND&vl%2812508474UI1%29=creator&vl%2812508474UI1%29=title&vl%2812508474UI1%29=creator&vl%281UIStartWith1%29=contains&vl%28freeText1%29=&vl%28boolOperator1%29=AND&vl%2812508470UI2%29=any&vl%2812508470UI2%29=title&vl%2812508470UI2%29=any&vl%281UIStartWith2%29=contains&vl%28freeText2%29=&vl%28boolOperator2%29=AND&vl%2812626940UI3%29=any&vl%2812626940UI3%29=title&vl%2812626940UI3%29=any&vl%281UIStartWith3%29=contains&vl%28freeText3%29=&vl%28boolOperator3%29=AND&vl%28D2240502UI4%29=all_items&vl%2853081356UI5%29=all_items&vl%28D2240500UI6%29=all_items&Submit=%E6%AA%A2%E7%B4%A2"
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ----------------------------------------要一直點進去------------------------------------------
# clickclick_crawler()
# 馬偕醫|工研院|明志|長庚科大|清華|暨南|臺南大|兩廳院|台神
def clickclick_crawler(driver, org, org_url, ISBN, xpath_num, gogo_xpath, xpath_detail, table_xpath, index_lst):
    clickclick_lst = []
    into_1_lst = ["馬偕醫學院", "工業技術研究院", "國立清華大學", "國立臺灣美術館", "國立臺灣史前文化博物館"]

    try:
        # 分三類的進入方式
        driver.get(org_url)
        if org in into_1_lst:  # 那種類型的沒辦改網址進進階搜尋QQ
            pro_search = wait_for_element_clickable(
                driver, "進階查詢", 5, By.LINK_TEXT).click()
        # 換成ISBN搜尋，xpath_num
        ISBN_xpath = "/html/body/form/table[1]/tbody/tr[2]/td[1]/select/option[" + xpath_num + "]"
        use_ISBN = wait_for_element_clickable(
            driver, ISBN_xpath, 5, By.XPATH).click()
        search_input = wait_for_element_clickable(
            driver, "request", 5, By.NAME)
        search_input.send_keys(ISBN)
        gogo = wait_for_element_clickable(
            driver, gogo_xpath, 5, By.XPATH).click()  # 按下確定，gogo_xpath
        click_result = wait_for_element_clickable(
            driver, "/html/body/form/table[1]/tbody/tr[2]/td[4]/a", 10, By.XPATH).click()

        # 終於結束前面的輸入可以開始爬蟲了
        try:  # 暨南有"直接進去書的頁面"的案例，所以先用try避開看看
            where2 = wait_for_element_clickable(
                driver, "brieftit", 5, By.CLASS_NAME).click()
        except:
            pass
        if org == "國立暨南國際大學":
            where3_xpath = "/html/body/table[9]/tbody/tr[1]/td[2]/a"
        else:
            # 按下書在哪裡?，xpath_detail
            where3_xpath = "/html/body/table[9]/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/" + xpath_detail
        where3 = wait_for_element_clickable(
            driver, where3_xpath, 5, By.XPATH).click()
        table = wait_for_element_clickable(
            driver, table_xpath, 5, By.XPATH)  # 找表格位置，table_xpath
        print("101010")
        trlist = table.find_elements_by_tag_name('tr')
        now_url = driver.current_url
        for row in trlist:
            tdlist = row.find_elements_by_tag_name('td')
            for sth in tdlist:
                new_row = [org, tdlist[index_lst[0]].text,
                           tdlist[index_lst[1]].text, tdlist[index_lst[2]].text, now_url]
                clickclick_lst.append(new_row)
                break
    except:
        pass
    table = pd.DataFrame(clickclick_lst)
    table.rename(columns={0: '圖書館', 1: '館藏地', 2: '索書號',
                 3: '館藏狀態', 4: '連結'}, inplace=True)
    return table

# 馬偕醫學院 MMC V OK


def MMC(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = clickclick_crawler(
        driver,
        '馬偕醫學院',
        "http://aleph.library.mmc.edu.tw/F?func=find-b&adjacent=Y&find_code=WRD&local_base=TOP02&request=&TY=",
        ISBN,
        "7",
        "/html/body/form/table[1]/tbody/tr[7]/td/input",
        "span/a[1]",
        '/html/body/table[10]',
        [2, 4, 7]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 工業技術研究院 ITRI V


def ITRI(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = clickclick_crawler(
        driver,
        '工業技術研究院',
        "http://61.61.255.73/F?func=find-d-0",
        ISBN,
        "7",
        "/html/body/form/table[1]/tbody/tr[9]/td/input",
        "a/img",
        '/html/body/table[10]',
        [5, 2, 8]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 明志科技大學 MCUT V


def MCUT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = clickclick_crawler(
        driver,
        '明志科技大學',
        "https://aleph.lib.cgu.edu.tw/F/?func=find-d-0&local_base=FLY03",
        ISBN,
        "7",
        "/html/body/form/table[1]/tbody/tr[9]/td/input",
        "a",
        '/html/body/table[9]',
        [3, 4, 7]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 長庚科技大學 CGUST V


def CGUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = clickclick_crawler(
        driver,
        '長庚科技大學',
        "https://aleph.lib.cgu.edu.tw/F/?func=find-d-0&local_base=FLY02",
        ISBN,
        "7",
        "/html/body/form/table[1]/tbody/tr[9]/td/input",
        "a",
        '/html/body/table[9]',
        [3, 4, 7]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# 國立清華大學 NTHU V
def NTHU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = clickclick_crawler(
        driver,
        '國立清華大學',
        "https://webpac.lib.nthu.edu.tw/F/?func=find-d-0",
        ISBN,
        "7",
        "/html/body/form/table[1]/tbody/tr[7]/td/input",
        "span/a",
        '/html/body/table[12]',
        [2, 4, 8]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立暨南國際大學 NCNU V


def NCNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = clickclick_crawler(
        driver,
        '國立暨南國際大學',
        "https://aleph.lib.ncnu.edu.tw/F/?func=find-d-0",
        ISBN,
        "7",
        "/html/body/form/table[1]/tbody/tr[9]/td/input",
        "",
        '/html/body/table[11]',
        [3, 4, 7]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺南大學 NUTN V


def NUTN(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = clickclick_crawler(
        driver,
        '國立臺南大學',
        "https://aleph.nutn.edu.tw/F/?func=find-d-0",
        ISBN,
        "7",
        "/html/body/form/table[1]/tbody/tr[9]/td/input",
        "a",
        '/html/body/table[9]',
        [2, 4, 8]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國家兩廳院 NTCH 9573308436 V


def NTCH(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = clickclick_crawler(
        driver,
        '國家兩廳院',
        "https://opac.npac-ntch.org/F/?func=find-d-0",
        ISBN,
        "13",
        "/html/body/form/table[3]/tbody/tr/td/input",
        "a[1]",
        '/html/body/table[9]',
        [3, 4, 7]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 台灣神學研究學院 TGST V


def TGST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = clickclick_crawler(
        driver,
        '台灣神學研究學院',
        "http://aleph.flysheet.com.tw/F/?func=find-d-0",
        ISBN,
        "7",
        "/html/body/form/table[1]/tbody/tr[9]/td/input",
        "a",
        '/html/body/table[10]',
        [3, 4, 8]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺灣美術館 NTMOFA 9784897376547


def NTMOFA(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = clickclick_crawler(
        driver,
        '國立臺灣美術館',
        "http://lib.moc.gov.tw/F?func=find-b-0&local_base=THM06",
        ISBN,
        "",
        "a",
        '/html/body/table[9]'
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 高苑科技大學 KYU X (您所想要連結的資料庫目前維護中)


def KYU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = clickclick_crawler(
        driver,
        '高苑科技大學',
        "http://210.60.92.160/F/?func=find-d-0&local_base=FLY04",
        ISBN,
        "6",
        "/html/body/form/table[1]/tbody/tr[8]/td/input",
        "a",
        '/html/body/table[8]',
        [2, 4, 8]
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg


# ---------------------------------------難以形容|很有特色------------------------------------------------
# chungchung_crawler()
# 中臺|中州
def chungchung_crawler(driver, org, org_url, ISBN):
    driver.get(org_url)
    search_input = wait_for_element_clickable(driver, "input", 5, By.NAME)
    search_input.send_keys(ISBN)
    gogo = wait_for_element_clickable(driver, "query", 5, By.NAME).click()

    where = wait_for_element_clickable(
        driver, "body > div > font > font > form > center:nth-child(1) > table > tbody > tr:nth-child(2) > td:nth-child(4) > font > a", 5, By.CSS_SELECTOR).click()
    table = accurately_find_table_and_read_it(driver, "table", table_index=3)
    table = organize_columns(table)
    table.drop([0], inplace=True)
    return table

# 中臺科技大學 CTUST


def CTUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)

    gg = chungchung_crawler(
        driver,
        '中臺科技大學',
        "http://120.107.56.24/isbn1.htm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中州科技大學 CCUST


def CCUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        "json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url(
        'https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    driver = webdriver.Chrome(
        options=my_options, desired_capabilities=my_capabilities)
    gg = chungchung_crawler(
        driver,
        '中州科技大學',
        "http://163.23.234.194/isbn1.htm",
        ISBN
    )

    driver.close()
    worksheet.append_rows(gg.values.tolist())
    return gg
