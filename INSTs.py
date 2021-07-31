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
my_capabilities['pageLoadStrategy'] = 'eager'  # 當 html下載完成之後，不等待解析完成，selenium會直接返回

# --------------------------處理欄位----------------------------
def organize_columns(df1):
    # 合併全部的 DataFrame
    try:
        df1 = pd.concat(df1, axis=0, ignore_index=True)
    except:
        df1.reset_index(drop=True, inplace=True)

    # 處理 column 2：館藏地
    c2 = [
        '分館/專室', '館藏地/室', '館藏室', '館藏地/館藏室', '館藏地', '典藏館', '館藏位置', '館藏地/區域',
        '典藏地名稱', '館藏地/館別', '館藏地(已外借/總數)', '館藏地/區域Location'
    ]
    df1['c2'] = ''
    for c in c2:
        try:
            df1['c2'] += df1[c]
        except:
            pass

    # 處理 column 3：索書號
    c3 = ['索書號', '索書號/期刊合訂本卷期', '索書號 / 部冊號', '索書號Call No.']
    df1['c3'] = ''
    for c in c3:
        try:
            df1['c3'] += df1[c]
        except:
            pass

    # 處理 column 4：館藏狀態
    c4 = [
        '館藏位置(到期日期僅為期限，不代表上架日期)', '狀態/到期日', '目前狀態 / 到期日', '館藏狀態', '處理狀態',
        '狀態 (說明)', '館藏現況 說明', '目前狀態/預計歸還日期', '圖書狀況 / 到期日', '調閱說明', '借閱狀態',
        '狀態', '館藏狀態(月-日-西元年)', '圖書狀況', '現況/異動日', 'Unnamed: 24', '圖書狀況Book Status'
    ]
    df1['c4'] = ''
    for c in c4:
        try:
            df1['c4'] += df1[c]
        except:
            pass

    # 直接生成另一個 DataFrame
    df2 = pd.DataFrame()
    df2['圖書館'] = df1['圖書館']
    df2['館藏地'] = df1['c2']
    df2['索書號'] = df1['c3']
    df2['館藏狀態'] = df1['c4']
    df2['連結'] = df1['連結']

    # 遇到值為 NaN時，將前一列的值填補進來
    df2.fillna(method="ffill", axis=0, inplace=True)

    return df2

# -------------------------等待ele出現--------------------------
def wait_for_element_present(element_position, driver, waiting_time=5, by=By.CSS_SELECTOR):
    try:
        element = WebDriverWait(driver, waiting_time).until(
            EC.presence_of_element_located((by, element_position)))
    except:
        return
    else:
        return element

# ------------------------等待網址改變--------------------------
def wait_for_url_changed(old_url, driver, waiting_time=10):
    try:
        WebDriverWait(driver, time).until(EC.url_changes(old_url))
    except:
        return
    else:
        return True

# ------------------------精準定位table-------------------------
def accurately_find_table_and_read_it(table_position, driver,table_position2=0):
    try:
        if not wait_for_element_present(table_position):
            print(f'找不到 {table_position}！')
            return
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_innerHTML = soup.select(table_position)[table_position2]
        tgt = pd.read_html(str(table_innerHTML), encoding='utf-8')[0]
        # tgt['圖書館'], tgt['連結'] = org, driver.current_url
    except:
        return
    else:
        return tgt

# --------------------等待input出現|ISBN----------------------
def search_ISBN(ISBN, input_position, driver, waiting_time=10):   
    search_input = WebDriverWait(driver, waiting_time).until(EC.presence_of_element_located((By.NAME, input_position)))
    search_input.send_keys(ISBN)
    search_input.send_keys(Keys.ENTER)

# --------------------等待select出現|ISBN----------------------
def select_ISBN_strategy(select_position, option_position, driver, waiting_time=30):
    time.sleep(0.5)
    search_field = WebDriverWait(driver, waiting_time).until(EC.presence_of_element_located((By.NAME, select_position)))
    select = Select(search_field)
    select.select_by_value(option_position)

#------------------------按載入更多----------------------------
def click_more_btn(driver):
    try:
        while True:
            more_btn = wait_for_element_present('載入更多', by=By.PARTIAL_LINK_TEXT)
            if not more_btn:
                return
            more_btn.click()
            time.sleep(2)  # 不得已的強制等待
    except:
        return

# ----------------------載入更多系列--------------------------
# webpac_gov_crawler() 
# 宜蘭|桃園|高雄|屏東|花蓮|澎湖|雲科|影視中心
def webpac_gov_crawler(org, org_url, ISBN,driver):
    try:
        table = []
        driver.get(org_url)
        select_ISBN_strategy('searchField', 'ISBN', driver)
        search_ISBN(ISBN, 'searchInput', driver)

        # 一筆
        if wait_for_element_present('.bookplace_list > table', driver):
            click_more_btn(driver)
            tgt = accurately_find_table_and_read_it('.bookplace_list > table', driver)
            tgt['圖書館'], tgt['連結'] = org, driver.current_url
            table.append(tgt)
        # 多筆
        elif wait_for_element_present('.data_all .data_quantity2 em', driver):
            tgt_urls = []
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            anchors = soup.select('.bookdata > h2 > a')
            for anchor in anchors:
                tgt_urls.append(org_url.replace('advanceSearch', '') + anchor['href'])
            for tgt_url in tgt_urls:
                driver.get(tgt_url)
                if wait_for_element_present('.bookplace_list > table', driver):
                    click_more_btn(driver)
                    tgt = accurately_find_table_and_read_it('.bookplace_list > table', driver)
                    tgt['圖書館'], tgt['連結'] = org, driver.current_url
                    table.append(tgt)
        # 無
        else:
            print(f'在「{org}」找不到「{ISBN}」')
            return

        table = organize_columns(table)
    except:
        print(f'在「{org}」搜尋「{ISBN}」時，發生不明錯誤！')
        return
    else:
        return table

# 宜蘭縣公共圖書館 ILCCB X(在「宜蘭縣公共圖書館」搜尋「9789861371955」時，發生不明錯誤！)
def ILCCB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_gov_crawler(
        '宜蘭縣公共圖書館',
        'https://webpac.ilccb.gov.tw/search?searchField=ISBN&searchInput=',
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# ---------------------被獨立出來的基隆---------------------
# 臺北市立圖書館 TPML X(兩筆)
def 臺北市立圖書館(org, org_url, ISBN, driver):
    try:
        # 進入＂搜尋主頁＂
        driver.get(org_url)
        # 等待定位＂下拉式選單＂，選擇以 ISBN 方式搜尋
        search_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, 'search_field')))
        select = Select(search_field)
        select.select_by_value('ISBN')
        # 定位＂搜尋欄＂，輸入 ISBN
        search_input = driver.find_element_by_name('search_input')
        search_input.send_keys(ISBN)
        search_input.submit()

        # 等待＜表格＞出現
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'table.order')))

        # 取得當前網頁的 html 進行解析，以取得 DataFrame
        tgt = pd.read_html(driver.page_source, encoding="utf-8")
        table = tgt[-3]
        table['圖書館'], table['連結'] = org, driver.current_url
        table = organize_columns(table)
        return table
    except:
        print(f'《{ISBN}》在「{org_url}」無法爬取')

def TPML(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        臺北市立圖書館(
        '臺北市立圖書館',
        'https://book.tpml.edu.tw/webpac/webpacIndex.jsp',
        ISBN,
        driver
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# --------------------------jsp系列--------------------------------
# webpac_jsp_crawler()
# 宜大|佛光|嘉藥|中華
def webpac_jsp_crawler(org, org_url, ISBN,driver):
    try:
        table = []       
        driver.get(org_url)
        try:
            select_ISBN_strategy('search_field', 'ISBN')
        except:
            select_ISBN_strategy('search_field', 'STANDARDNO')  # 北科大
        search_ISBN(ISBN, 'search_input')
        
        # 一筆
        if wait_for_element_present('div.mainCon'):
            if not wait_for_element_present('table.order'):
                return
            tgt = accurately_find_table_and_read_it('table.order')
            tgt['圖書館'], tgt['連結'] = org, driver.current_url
            table.append(tgt)
        # 多筆、零筆
        elif wait_for_element_present('iframe#leftFrame'):
            iframe = driver.find_element_by_id('leftFrame')
            driver.switch_to.frame(iframe)
            # 切換到 <frame> 需要時間，否則會無法讀取
            time.sleep(1)
            # 解析 html，以取得 tgt_urls
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # 判斷是不是＂零筆＂
            if soup.find('em', {'id': 'totalpage'}).text == '0':
                print(f'在「{org}」找不到「{ISBN}」')
                return
            anchors = soup.find_all('a', 'bookname')
            # tgt_urls 為各個＂詳細書目＂的網址
            tgt_urls = []
            for anchor in anchors:
                tgt_urls.append(org_url.replace('webpacIndex.jsp', '') + anchor['href'])
            # 取得 tgt_urls 後，開始進入 tgt_url
            for tgt_url in tgt_urls:
                # 進入＂詳細書目＂
                driver.get(tgt_url)
                # 等待元素出現，如果出現，那麼抓取 DataFrame；如果沒出現，那麼跳出迴圈
                if not wait_for_element_present('table.order'):
                    continue  # 暫停＂本次＂迴圈，以下敘述不會執行
                tgt = accurately_find_table_and_read_it('table.order')
                tgt['圖書館'], tgt['連結'] = org, driver.current_url
                table.append(tgt)
        table = organize_columns(table)
    except:
        print(f'在「{org}」搜尋「{ISBN}」時，發生不明錯誤！')
        return
    else:
        return table

# 佛光大學 FGU X(name 'driver' is not defined)
def FGU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_jsp_crawler(
        '佛光大學',
        "http://libils.fgu.edu.tw/webpacIndex.jsp",
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# ------------------------最簡單的那種------------------------------
# easy_crawler()
# 海大|陽明|台科大|台師大|文化|輔仁|中研院
def easy_crawler(table_position, org, org_url, ISBN, driver):
    try:
        # 組合成書本的網址
        tgt_url = org_url + ISBN
        # 載入 html，如果發生 HTTPError，那麼就使用 requests.get(url, verify=False)
        try:
            tgt = pd.read_html(tgt_url, encoding="utf-8")
        except HTTPError:
            resp = requests.get(tgt_url,
                                verify=False)  # 設定 verify=False，以解決 SSLError
            tgt = pd.read_html(resp.text, encoding="utf-8")
        # 定位表格
        table = tgt[table_position]
        table['圖書館'], table['連結'] = org, tgt_url
        table = organize_columns(table)
        return table  # 完成抓取 table
    except:
        print(f'《{ISBN}》在「{url}」無法爬取')

# 國立臺灣海洋大學 NTOU V
def NTOU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    worksheet.get_all_values()
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        easy_crawler(
        2,
        '國立臺灣海洋大學',
        'https://ocean.ntou.edu.tw/search*cht/i?SEARCH=',
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立陽明大學 YM V
def YM(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    worksheet.get_all_values()
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        easy_crawler(
        4,
        '國立陽明大學',
        "https://library.ym.edu.tw/search*cht/a?searchtype=i&searcharg=",
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺灣科技大學 YM V
def NTUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    worksheet.get_all_values()
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        easy_crawler(
        6,
        '國立臺灣科技大學',
        "https://sierra.lib.ntust.edu.tw/search*cht/i?SEARCH=",
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺灣師範大學 NTNU V
def NTNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    worksheet.get_all_values()
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        easy_crawler(
        4,
        '國立臺灣師範大學',
        "https://opac.lib.ntnu.edu.tw/search*cht/i?SEARCH=",
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中國文化大學 PCCU V
def PCCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    worksheet.get_all_values()
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        easy_crawler(
        7,
        '中國文化大學',
        "https://webpac.pccu.edu.tw/search*cht/?searchtype=i&searcharg=",
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 輔仁大學 FJU ?
def FJU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        easy_crawler(
        7,
        '輔仁大學',
        "https://library.lib.fju.edu.tw/search~S0*cht/?searchtype=i&searcharg=",
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# ----------------------改版?-----------------------------
# changed_crawler()
# 中研院|輔仁|陽交大 ?
def changed_crawler(org, org_url, ISBN, driver):
    driver.get(org_url)   
    select_ISBN_strategy('searchtype', 'i', driver)  
    search_ISBN(ISBN, 'searcharg', driver)

    if not wait_for_element_present('table.bibItems', driver):
        print(f'在「{org}」找不到「{ISBN}」')
        return

    table = accurately_find_table_and_read_it('table.bibItems', driver)
    table['圖書館'], table['連結'] = org, driver.current_url
    table = organize_columns(table)
    return table

# 中央研究院 SINICA ?
def SINICA(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        changed_crawler(
        '中央研究院',
        "https://las.sinica.edu.tw/search*cht/a?searchtype=i&searcharg=",
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# --------------------ajax_page-----------------------------
# webpac_ajax_page_crawler()
# 新北市|高空大|屏大
def webpac_ajax_page_crawler(org, org_url, ISBN, driver):
    try:
        # 進入＂搜尋主頁＂
        driver.get(org_url)
        # 等待點擊＂進階查詢＂按鈕，接著點擊
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.LINK_TEXT, '進階查詢'))).click()
        # 等待定位＂下拉式選單＂，選擇以 ISBN 方式搜尋
        search_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'as_type_1')))
        select = Select(search_field)
        select.select_by_value('i')
        # 定位＂搜尋欄＂，輸入 ISBN
        search_input = driver.find_element_by_id('as_keyword_1')
        search_input.send_keys(ISBN)
        search_input.send_keys(
            Keys.ENTER)  # 無法 submit()，用 send_keys(keys.ENTER) 來替代

        # 在＂搜尋結果頁面＂，等待定位＂詳細書目＂。
        # try-except 來判斷有沒有在＂搜尋結果頁面＂
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, '詳細書目')))
        except:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.book-detail')))

                # 抓取方式：找出 mid 後，進入 ajax pag 抓取 DataFrame
                org_url = org_url.replace('/search.cfm', '')
                tgts = []
                url = driver.current_url
                mid = url.split('mid=')[-1].split('&')[0]
                ajax_page_url = f'{org_url}/ajax_page/get_content_area.cfm?mid={mid}&i_list_number=250&i_page=1&i_sory_by=1'
                tgt = pd.read_html(ajax_page_url, encoding='utf-8')[0]
                tgt['圖書館'], tgt['連結'] = org, url
                tgts.append(tgt)
                table = pd.concat(tgts, axis=0, ignore_index=True)
                table = organize_columns(table)
                return table  # 完成抓取 table
            except:  # 沒有搜尋結果，也沒有進入＂詳細書目頁面＂
                print(f'《{ISBN}》查無此書')
                return  # 什麼都不做，退出此 function

        # 抓取多個＂詳細書目＂的網址
        anchors = driver.find_elements_by_link_text('詳細書目')
        urls = []
        for anchor in anchors:
            urls.append(anchor.get_attribute('href'))

        # 抓取方式：找出 mid 後，進入 ajax pag 抓取 DataFrame
        org_url = org_url.replace('/search.cfm', '')
        tgts = []
        for url in urls:
            mid = url.split('mid=')[-1].split('&')[0]  # 抓取 mid
            ajax_page_url = f'{org_url}/ajax_page/get_content_area.cfm?mid={mid}&i_list_number=250&i_page=1&i_sory_by=1'
            tgt = pd.read_html(ajax_page_url, encoding='utf-8')[0]
            tgt['圖書館'], tgt['連結'] = org, url
            tgts.append(tgt)
        table = organize_columns(table)
        return table  # 完成抓取 table
    except:
        print(f'《{ISBN}》在「{url}」無法爬取')

# 新北市立圖書館 NTPC X(切換成ajax時掛掉)
def NTPC(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_ajax_page_crawler(
        '新北市立圖書館',
        "https://webpac.tphcc.gov.tw/webpac/search.cfm",
        ISBN,
        driver
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# ---------------------被獨立出來的基隆---------------------
def 基隆市公共圖書館(org, org_url, ISBN, driver,wait):
    try:
        # 進入＂搜尋主頁＂
        driver.get(org_url)
        # 等待點擊＂進階查詢＂按鈕，接著點擊
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, '進階檢索'))).click()
        time.sleep(2)  # JavaScript 動畫，強制等待
        # 等待定位＂下拉式選單＂，選擇以 ISBN 方式搜尋
        search_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'as_type_1')))
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
        print(f'《{ISBN}》在「{url}」無法爬取')

# 基隆市公共圖書館 KLCCAB X(無館藏資料時會掛掉)
def KLCCAB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    worksheet.get_all_values()
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        基隆市公共圖書館(
        '基隆市公共圖書館',
        "https://webpac.klccab.gov.tw/webpac/search.cfm",
        ISBN,
        driver,
        wait
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

