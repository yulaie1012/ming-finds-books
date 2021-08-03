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
        '典藏地名稱', '館藏地/館別', '館藏地(已外借/總數)', '館藏地/區域Location', '現行位置'
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
        '狀態', '館藏狀態(月-日-西元年)', '圖書狀況', '現況/異動日', 'Unnamed: 24', '圖書狀況Book Status', '館藏狀況(月-日-西元年)'
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
def wait_for_element_present(driver, element_position, waiting_time=5, by=By.CSS_SELECTOR):
    try:
        element = WebDriverWait(driver, waiting_time).until(
            EC.presence_of_element_located((by, element_position)))
    except:
        return
    else:
        return element

def wait_for_element_clickable(driver, element_position, waiting_time=5, by=By.LINK_TEXT):
    try:
        time.sleep(0.3)
        element = WebDriverWait(driver, waiting_time).until(
            EC.element_to_be_clickable((by, element_position)))
    except:
        return
    else:
        return element

# ------------------------等待網址改變--------------------------
def wait_for_url_changed(driver, old_url, waiting_time=10):
    try:
        WebDriverWait(driver, time).until(EC.url_changes(old_url))
    except:
        return
    else:
        return True

# ------------------------精準定位table-------------------------
def accurately_find_table_and_read_it(driver, table_position, table_index=0):
    try:
        if not wait_for_element_present(driver, table_position):
            print(f'找不到 {table_position}！')
            return
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_innerHTML = soup.select(table_position)[table_index]
        tgt = pd.read_html(str(table_innerHTML), encoding='utf-8')[0]
        # tgt['圖書館'], tgt['連結'] = org, driver.current_url
    except:
        return
    else:
        return tgt

# --------------------等待input出現|ISBN----------------------
def search_ISBN(driver, ISBN, input_position, waiting_time=10, by=By.NAME):
    time.sleep(0.5)
    search_input = WebDriverWait(driver, waiting_time).until(EC.presence_of_element_located((by, input_position)))
    search_input.send_keys(ISBN)
    search_input.send_keys(Keys.ENTER)

# --------------------等待select出現|ISBN----------------------
def select_ISBN_strategy(driver, select_position, option_position, waiting_time=30):
    time.sleep(0.5)
    search_field = WebDriverWait(driver, waiting_time).until(EC.presence_of_element_located((By.NAME, select_position)))
    select = Select(search_field)
    select.select_by_value(option_position)

# ------------------------Primo找書--------------------------
def primo_finding(org, tcn, driver): #primo爬資訊的def ；#tcn = thelist_class_name
	sub_df_lst = []
	time.sleep(10)
	try:
		back = driver.find_element_by_css_selector(".tab-header .back-button.button-with-icon.zero-margin.md-button.md-primoExplore-theme.md-ink-ripple")
	except:
		back = None
	if back != None:
		back.click()

	thelist = driver.find_elements_by_class_name(tcn)
	if tcn == 'md-2-line.md-no-proxy._md': #如果是東吳或銘傳
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
				new_row = [org, where[_].text, a[4].text, a[0].text, now_url]
				sub_df_lst.append(new_row)
				break
			break
	return sub_df_lst

# ------------------------綠點點找書--------------------------
def primo_greendot_finding(org, driver): #primo爬資訊的def
    sub_df_lst = []
    try:
        time.sleep(1)
        num = driver.find_elements_by_class_name('EXLLocationTableColumn1')
        status = driver.find_elements_by_class_name('EXLLocationTableColumn3')
        for i in range(0, len(num)):
            now_url = driver.current_url
            new_row = [org, "圖書館總館", num[i].text, status[i].text, now_url]
            sub_df_lst.append(new_row)
    except:
        pass
    return sub_df_lst

#------------------------按載入更多----------------------------
def click_more_btn(driver):
    try:
        while True:
            more_btn = wait_for_element_clickable(driver, '載入更多')
            if not more_btn:
                return
            more_btn.click()
            time.sleep(2)  # 不得已的強制等待
    except:
        return




# ----------------------------------------載入更多系列----------------------------------------
# webpac_gov_crawler() 
# 宜蘭|桃園|高雄|屏東|花蓮|澎湖|雲科|影視中心
def webpac_gov_crawler(driver, org, org_url, ISBN):
    try:
        table = []
        driver.get(org_url + 'advanceSearch')
        select_ISBN_strategy(driver, 'searchField', 'ISBN')
        search_ISBN(driver, ISBN, 'searchInput')

        # 一筆
        if wait_for_element_present(driver, '.bookplace_list > table', 10):
            click_more_btn(driver)
            tgt = accurately_find_table_and_read_it(driver, '.bookplace_list > table')
            tgt['圖書館'], tgt['連結'] = org, driver.current_url
            table.append(tgt)
        # 多筆
        elif wait_for_element_present(driver, '.data_all .data_quantity2 em', 5):
            # 取得多個連結
            tgt_urls = []
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            anchors = soup.select('.bookdata > h2 > a')
            for anchor in anchors:
                tgt_urls.append(org_url + anchor['href'])
            # 進入不同的連結
            for tgt_url in tgt_urls:
                driver.get(tgt_url)
                if wait_for_element_present(driver, '.bookplace_list > table', 10):
                    click_more_btn(driver)
                    tgt = accurately_find_table_and_read_it(driver, '.bookplace_list > table')
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
        driver,
        '宜蘭縣公共圖書館',
        'https://webpac.ilccb.gov.tw/',
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 桃園市立圖書館 TYPL V
def TYPL(ISBN):
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
        driver,
        '桃園市立圖書館',
        'https://webpac.typl.gov.tw/',
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 高雄市立圖書館 KSML V
def KSML(ISBN):
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
        driver,
        '高雄市立圖書館',
        'https://webpacx.ksml.edu.tw/',
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 屏東縣公共圖書館 PTPL V
def PTPL(ISBN):
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
        driver,
        '屏東縣公共圖書館',
        'https://library.pthg.gov.tw/',
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg





# -----------------------------------------jsp系列-----------------------------------------------------
# webpac_jsp_crawler()
# 佛光|宜大|中華|嘉藥|臺北市|臺藝大|北市大|北醫|北商大|苗栗縣|景文|致理
# 萬能|健行|明新|中國科大|中教大|臺體|東海|靜宜|僑光|彰師|雲林縣
def webpac_jsp_crawler(driver, org, org_url, ISBN):
    try:
        table = []
        
        driver.get(org_url)
        try:
            select_ISBN_strategy(driver, 'search_field', 'ISBN')
        except:
            select_ISBN_strategy(driver, 'search_field', 'STANDARDNO')  # 北科大
        search_ISBN(driver, ISBN, 'search_input')
        
        # 一筆
        if wait_for_element_present(driver, 'div.mainCon'):
            if not wait_for_element_present(driver, 'table.order'):
                print(f'在「{org}」找不到「{ISBN}」')
                return
            tgt = accurately_find_table_and_read_it(driver, 'table.order')
            tgt['圖書館'], tgt['連結'] = org, driver.current_url
            table.append(tgt)
        # 多筆、零筆
        elif wait_for_element_present(driver, 'iframe#leftFrame'):
            iframe = driver.find_element_by_id('leftFrame')
            driver.switch_to.frame(iframe)
            time.sleep(1)  # 切換到 <frame> 需要時間，否則會無法讀取
            
            # 判斷是不是＂零筆＂查詢結果
            if wait_for_element_present(driver, '#totalpage').text == '0':
                print(f'在「{org}」找不到「{ISBN}」')
                return
            
            # ＂多筆＂查詢結果
            tgt_urls = []
            anchors = driver.find_elements(By.LINK_TEXT, '詳細內容')
            if anchors == []:
                anchors = driver.find_elements(By.LINK_TEXT, '內容')
            for anchor in anchors:
                tgt_urls.append(anchor.get_attribute('href'))

            for tgt_url in tgt_urls:
                driver.get(tgt_url)
                # 等待元素出現，如果出現，那麼抓取 DataFrame；如果沒出現，那麼跳出迴圈
                if not wait_for_element_present(driver, 'table.order'):
                    continue  # 暫停＂本次＂迴圈，以下敘述不會執行
                tgt = accurately_find_table_and_read_it(driver, 'table.order')
                tgt['圖書館'], tgt['連結'] = org, driver.current_url
                table.append(tgt)
        table = organize_columns(table)
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        return table

# 佛光大學 FGU V
def FGU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_jsp_crawler(
        driver, 
        '佛光大學',
        "http://libils.fgu.edu.tw/webpacIndex.jsp",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立宜蘭大學 NIU V
def NIU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_jsp_crawler(
        driver, 
        '國立宜蘭大學',
        "https://lib.niu.edu.tw/webpacIndex.jsp",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中華科技大學 CUST V
def CUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_jsp_crawler(
        driver, 
        '中華科技大學',
        "http://192.192.231.232/bookDetail.do?id=260965&nowid=3&resid=188809854",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 嘉南藥理大學 CNU V
def CNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_jsp_crawler(
        driver, 
        '嘉南藥理大學',
        "https://webpac.cnu.edu.tw/webpacIndex.jsp",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺北市立圖書館 TPML V
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
        webpac_jsp_crawler(
        driver,
        '臺北市立圖書館',
        'https://book.tpml.edu.tw/webpac/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺灣藝術大學 NTUA V
def NTUA(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '國立臺灣藝術大學',
        'http://webpac.ntua.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺北市立大學 UTaipei V
def UTaipei(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '臺北市立大學',
        'http://lib.utaipei.edu.tw/webpac/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺北科技大學 NTUT V
def NTUT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '國立臺北科技大學',
        'https://libholding.ntut.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 臺北醫學大學 TMU V
def TMU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '臺北醫學大學',
        'https://libelis.tmu.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺北商業大學 NTUB V
def NTUB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '國立臺北商業大學',
        'http://webpac.ntub.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 苗栗縣立圖書館 Miaoli V
def Miaoli(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '苗栗縣立圖書館',
        'https://webpac.miaoli.gov.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 景文科技大學 JUST V
def JUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '景文科技大學',
        'https://jinwenlib.just.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 致理科技大學 CLUT V
def CLUT(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '致理科技大學',
        'http://hylib.chihlee.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 萬能科技大學 VNU V
def VNU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '萬能科技大學',
        'http://webpac.lib.vnu.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 健行科技大學 UCH V
def UCH(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '健行科技大學',
        'https://library.uch.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 明新科技大學 MUST V
def MUST(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '明新科技大學',
        'https://hylib.lib.must.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 育達科技大學 YDU V
def YDU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '育達科技大學',
        'http://120.106.11.155/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中國科技大學 CUTE V
def CUTE(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '中國科技大學',
        'https://webpac.cute.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺中教育大學 NTCU V
def NTCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '國立臺中教育大學',
        'http://webpac.lib.ntcu.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺灣體育運動大學 NTUS V
def NTUS(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '國立臺灣體育運動大學',
        'https://hylib.ntus.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 東海大學 THU V
def THU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '東海大學',
        'https://webpac.lib.thu.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 靜宜大學 PU V
def PU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '靜宜大學',
        'http://webpac.lib.pu.edu.tw/webpac/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 僑光科技大學 OCU V
def OCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '僑光科技大學',
        'http://lib.webpac.ocu.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立彰化師範大學 NCUE V
def NCUE(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '國立彰化師範大學',
        'https://book.ncue.edu.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg

# 雲林縣公共圖書館 YLCCB V
def YLCCB(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)   

    output.append(
        webpac_jsp_crawler(
        driver,
        '雲林縣公共圖書館',
        'http://library.ylccb.gov.tw/webpacIndex.jsp',
        ISBN
        )
    )   
    driver.close()
    gg = pd.concat(output, axis=0, ignore_index=True).fillna("")
    worksheet.append_rows(gg.values.tolist())
    return gg









# ------------------------------------最簡單的那種------------------------------------------
# easy_crawler()
# 海大|台科大|台師大|中原|逢甲|朝陽|中山|高師
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
        driver, 
        '國立臺灣海洋大學',
        'https://ocean.ntou.edu.tw/search*cht/i?SEARCH=',
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立臺灣科技大學 NTUST V
def NTUST(ISBN):
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
        driver,     
        '國立臺灣科技大學',
        "https://sierra.lib.ntust.edu.tw/search*cht/i?SEARCH=",
        ISBN
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
        driver, 
        '國立臺灣師範大學',
        "https://opac.lib.ntnu.edu.tw/search*cht/i?SEARCH=",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 中原大學 CYCU V
def CYCU(ISBN):
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
        driver, 
        '中原大學',
        "http://cylis.lib.cycu.edu.tw/search*cht/i",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 逢甲大學 FCU V
def FCU(ISBN):
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
        driver, 
        '逢甲大學',
        "https://innopac.lib.fcu.edu.tw/search*cht/i",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 朝陽科技大學 CYUT V
def CYUT(ISBN):
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
        driver, 
        '朝陽科技大學',
        "https://millennium.lib.cyut.edu.tw/search*cht/i",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立中山大學 NSYSU V
def NSYSU(ISBN):
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
        driver, 
        '國立中山大學',
        "https://dec.lib.nsysu.edu.tw/search*cht/i",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立高雄師範大學 NKNU V
def NKNU(ISBN):
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
        driver, 
        '國立高雄師範大學',
        "https://nknulib.nknu.edu.tw/search*cht/i",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 文藻外語大學 WZU V
def WZU(ISBN):
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
        driver, 
        '文藻外語大學',
        "https://libpac.wzu.edu.tw/search*cht/i",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 大仁科技大學 Tajen V
def Tajen(ISBN):
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
        driver, 
        '大仁科技大學',
        "http://lib.tajen.edu.tw/search*cht/i",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立中央大學 NCU V
def NCU(ISBN):
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
        driver, 
        '國立中央大學',
        "https://opac.lib.ncu.edu.tw/search*cht/i",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
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
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_pro_crawler(
        driver, 
        '中央研究院',
        "https://las.sinica.edu.tw/*cht",
        ISBN
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
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_pro_crawler(
        driver,
        '中國文化大學',
        "https://webpac.pccu.edu.tw/*cht",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 輔仁大學 FJU V
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
        webpac_pro_crawler(
        driver, 
        '輔仁大學',
        "https://library.lib.fju.edu.tw/",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立陽明交通大學 NYCU V
def NYCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        webpac_pro_crawler(
        driver, 
        '國立陽明交通大學',
        "https://library.ym.edu.tw/screens/opacmenu_cht_s7.html",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg




# -----------------------------------ajax_page------------------------------------------------
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




# ------------------------------被獨立出來的基隆--------------------------------
def 基隆市公共圖書館(org, org_url, ISBN, driver, wait):
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




# ---------------------------------被獨立出來的國圖----------------------------------------
def 國家圖書館(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)
        select_ISBN_strategy(driver, 'find_code', 'ISBN')
        search_ISBN(driver, ISBN, 'request')

        # 點擊＂書在哪裡(請點選)＂，進入＂詳細書目＂
        tgt_url = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, '書在哪裡(請點選)'))).get_attribute('href')
        driver.get(tgt_url)

        table = accurately_find_table_and_read_it(driver, 'table', -2)
        table['圖書館'], table['連結'] = org, tgt_url
        table = organize_columns(table)
    except:
        print(f'《{ISBN}》在「{org_url}」無法爬取')
        return
    return table

# 國家圖書館 NCL X(有狀況沒有處理到)(9789861371955)
def NCL(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        國家圖書館(
        driver,
        '國家圖書館',
        "https://aleweb.ncl.edu.tw/F",
        ISBN
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg




# ------------------------------------------Primo-----------------------------------------
# primo_crawler()
# 臺大|政大|淡大|東吳
def primo_crawler(org, url_front, ISBN ,url_behind, tcn, driver):
    url = url_front + ISBN + url_behind
    primo_lst = []

    try:
        # 進入《館藏系統》頁面
        driver.get(url)
        time.sleep(8)

        try: #開始爬蟲
            editions = driver.find_elements_by_class_name('item-title') 
            if len(editions) > 1: #如果最外面有兩個版本(默認點進去不會再分版本了啦)(ex.政大 9789861371955)，直接交給下面處理
                pass
            else: #如果最外面只有一個版本，那有可能點進去還有再分，先click進去，再分一個版本跟多個版本的狀況
                time.sleep(5)
                editions[0].click()
                time.sleep(5)
                editions = driver.find_elements_by_class_name('item-title') #這時候是第二層的分版本了！(ex.政大 9789869109321)
                
            try: #先找叉叉確定是不是在最裡層了
                back_check = driver.find_element_by_class_name("md-icon-button.close-button.full-view-navigation.md-button.md-primoExplore-theme.md-ink-ripple")
            except:
                back_check = None
            if back_check == None: #多個版本才要再跑迴圈(找不到叉叉代表不在最裡面，可知不是一個版本)
                for i in range(0, len(editions)): #有幾個版本就跑幾次，不管哪一層版本都適用
                    time.sleep(5)
                    into = editions[i].click()
                    time.sleep(8)
                    primo_lst += primo_finding(org, tcn, driver)
                    table = pd.concat(primo_lst, axis=0, ignore_index=True)
                    try: 
                        back2 = driver.find_element_by_class_name("md-icon-button.close-button.full-view-navigation.md-button.md-primoExplore-theme.md-ink-ripple").click()
                    except:
                        back2 = None

            else: #如果只有一個版本(有叉叉的意思)，那前面已經click過了不能再做
                time.sleep(10)
                primo_lst += primo_finding(org, tcn, driver)
                
        except:
            pass
    except:
        pass
    table = pd.DataFrame(primo_lst)
    table.rename(columns={0: '圖書館', 1: '館藏地', 2: '索書號', 3: '館藏狀態', 4: '連結'}, inplace = True)
    return table

# 國立臺灣大學 NTU X
def NTU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    
    output.append(
        primo_crawler(
        '國立臺灣大學',
        "https://ntu.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
        ISBN,
        "&tab=Everything&search_scope=MyInst_and_CI&vid=886NTU_INST:886NTU_INST&offset=0",
        "layout-align-space-between-center.layout-row.flex-100",
        driver
        )
    )
    
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 國立政治大學 NCCU X
def NCCU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    
    output.append(
        primo_crawler(
        '國立政治大學',
        "https://nccu.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
        ISBN,
        "&tab=Everything&search_scope=MyInst_and_CI&vid=886NCCU_INST:886NCCU_INST",
        "layout-align-space-between-center.layout-row.flex-100",
        driver
        )
    )
    
    driver.close()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg




# ------------------------------------------綠點點----------------------------------------------
# primo_greendot_crawler()
# 長庚|中正
def primo_greendot_crawler(driver, org, url_front, ISBN ,url_behind):
    url = url_front + ISBN + url_behind
    primo_greendot_lst = []

    try:
        driver.get(url)
        try: #只有一個版本
            time.sleep(2)
            place_click = driver.find_element_by_id('exlidResult0-LocationsTab').click()
            sub_df_lst = []
            try:
                time.sleep(5)
                num = driver.find_elements_by_class_name('EXLLocationTableColumn1')
                status = driver.find_elements_by_class_name('EXLLocationTableColumn3')
                for i in range(0, len(num)):
                    now_url = driver.current_url
                    new_row = [org, "圖書館總館", num[i].text, status[i].text, now_url]
                    sub_df_lst.append(new_row)
            except:
                pass
            primo_greendot_lst += sub_df_lst
        except: #有多個版本，所以要點進去再做
            time.sleep(2)
            manyeditions = driver.find_element_by_id('titleLink').click()
            time.sleep(5)
            for i in range(1, 10): #假設有十個版本吧
                try:
                    place_click2 = driver.find_element_by_id('exlidResult' + str(i) + '-LocationsTab').click()
                except:
                    continue
    except:
        pass
    table = pd.DataFrame(primo_greendot_lst)
    table.rename(columns={0: '圖書館', 1: '館藏地', 2: '索書號', 3: '館藏狀態', 4: '連結'}, inplace = True)
    return table

# 長庚大學 CGU
def CGU(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        primo_greendot_crawler(
        driver,
        '長庚大學',
        "https://primo.lib.cgu.edu.tw/primo_library/libweb/action/search.do?fn=search&ct=search&initialSearch=true&mode=Advanced&tab=default_tab&indx=1&dum=true&srt=rank&vid=CGU&frbg=&tb=t&vl%2812508471UI0%29=isbn&vl%2812508471UI0%29=title&vl%2812508471UI0%29=isbn&vl%281UIStartWith0%29=contains&vl%28freeText0%29=",
        ISBN,
        "&vl%28boolOperator0%29=AND&vl%2812508474UI1%29=creator&vl%2812508474UI1%29=title&vl%2812508474UI1%29=creator&vl%281UIStartWith1%29=contains&vl%28freeText1%29=&vl%28boolOperator1%29=AND&vl%2812508470UI2%29=any&vl%2812508470UI2%29=title&vl%2812508470UI2%29=any&vl%281UIStartWith2%29=contains&vl%28freeText2%29=&vl%28boolOperator2%29=AND&vl%2812626940UI3%29=any&vl%2812626940UI3%29=title&vl%2812626940UI3%29=any&vl%281UIStartWith3%29=contains&vl%28freeText3%29=&vl%28boolOperator3%29=AND&vl%28D2240502UI4%29=all_items&vl%2853081356UI5%29=all_items&vl%28D2240500UI6%29=all_items&Submit=%E6%AA%A2%E7%B4%A2"
        )
    )
    
    driver.close()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg



# ----------------------------------------要一直點進去------------------------------------------
# clickclick_crawler()
# 馬偕醫學院|工研院
def clickclick_crawler(driver, org, url, ISBN, xpath_num, xpath_detail, table_place):
    clickclick_lst = []
    ISBN_xpath = "/html/body/table[6]/tbody/tr/td[1]/form/fieldset[1]/select/option[" + xpath_num + "]"
    try:
        driver.get(url)
        time.sleep(8)
        use_ISBN = driver.find_element_by_xpath(ISBN_xpath).click()
        search_input = driver.find_element_by_name("y")
        search_input.send_keys(ISBN)
        gogo = driver.find_element_by_name("Search").click()
        time.sleep(4)
        
        where2 = driver.find_element_by_class_name("brieftit").click()
        time.sleep(2) 
        where3_xpath = "/html/body/table[9]/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/" + xpath_detail
        where3 = driver.find_element_by_xpath(where3_xpath).click()
        time.sleep(10)      
        table = driver.find_element_by_css_selector(table_place)       
        time.sleep(5)
        now_url = driver.current_url
        trlist = table.find_elements_by_tag_name('tr')
        for row in trlist:
            tdlist = row.find_elements_by_tag_name('td')
            for sth in tdlist:
                if org != "工業技術研究院":
                    new_row = [org, tdlist[2].text, tdlist[4].text, tdlist[7].text, now_url]
                else:
                    new_row = [org, tdlist[2].text, tdlist[4].text, tdlist[8].text, now_url]     
                clickclick_lst.append(new_row)
                break       
    except:
        pass
    table = pd.DataFrame(clickclick_lst)
    print(table)
    table.rename(columns={0: '圖書館', 1: '館藏地', 2: '索書號', 3: '館藏狀態', 4: '連結'}, inplace = True)
    return table

# 馬偕醫學院 MMC
def MMC(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        clickclick_crawler(
        driver, 
        '馬偕醫學院',
        "http://aleph.library.mmc.edu.tw/F?func=find-b&adjacent=Y&find_code=WRD&local_base=TOP02&request=&TY=",
        ISBN, 
        "8", 
        "span/a[1]", 
        'body > table:nth-child(16)'
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg

# 工業技術研究院 ITRI
def ITRI(ISBN):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
    gs = gspread.authorize(creds)
    sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
    worksheet = sheet.get_worksheet(0)
    output = []
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver", options=my_options, desired_capabilities=my_capabilities)
    wait = WebDriverWait(driver, 10)
    
    output.append(
        clickclick_crawler(
        driver, 
        '工業技術研究院',
        "http://61.61.255.73/F?func=find-b-0",
        ISBN, 
        "7", 
        "a/img", 
        'body > table:nth-child(17)'
        )
    )
    
    driver.quit()
    gg = organize_columns(pd.concat(output, axis=0, ignore_index=True).fillna(""))
    worksheet.append_rows(gg.values.tolist())
    return gg
