#!/usr/bin/env python
# coding: utf-8

# # 環境設置

# ## 載入套件
# - selenium、pandas、requests、bs4、time

# In[1]:


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


# ## 設定 driver 的參數：options、desired_capabilities

# In[2]:


if __name__ == '__main__':
    my_options = Options()
    my_options.add_argument('--incognito')  # 開啟無痕模式
    # my_options.add_argument('--start-maximized')  # 視窗最大化
    # my_options.add_argument('--headless')  # 不開啟實體瀏覽器
    my_capabilities = DesiredCapabilities.CHROME
    my_capabilities['pageLoadStrategy'] = 'eager'  # 頁面加載策略：HTML 解析成 DOM


# # 自定義函式

# ## organize_columns(df1)
# - 處理欄位：圖書館、館藏地（c2）、索書號（c3）、館藏狀態（c4）、連結
# - 如果 df1 是裝著 DataFrame 的 list，則就合併它們；否則（df1 是 DataFrame），就接著執行以下敘述。
# - 丟掉垃圾欄位，整理成要呈現的表格
# - 新增必要欄位（圖書館、連結）
# - 填滿 NaN（用 ffill 的 方式）

# In[3]:


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


# ## set_excel(df, directory) 暫停
# - 待

# In[4]:


def set_excel(df, directory):
    # B｢圖書館｣、C「館藏地」、D「索書號」、E「館藏狀態」、F「連結」
    pandas.io.formats.excel.header_style = None  # 標題格式清除
    writer = pd.ExcelWriter(directory)
    df.to_excel(writer, sheet_name="搜尋結果")

    workbook1 = writer.book
    worksheets = writer.sheets
    worksheet1 = worksheets["搜尋結果"]

    # 測試
    cell_format = workbook1.add_format({
        "font_name": "微軟正黑體",
        "font_size": 16,
        "align": "left",
        #         "border": 80,
    })
    worksheet1.set_column("B:F", 40, cell_format)

    # 設定單元格的寬度
    #     worksheet1.set_column("B:F", 35)

    writer.save()
    print("爬取完成")


# ## wait_for_element_present(driver, element_position, waiting_time=5, by=By.CSS_SELECTOR)
# - 用法：
#     - 等待 element 出現，每間隔 0.5 秒定位一次，直到 5 秒。如果定位 element 成功，回傳 element；否則，回傳 None。
# - 參數：
#     - driver
#     - element_position：元素位置，預設 CSS selector
#     - waiting_time：等待時間，預設 5 秒
#     - by：定位方式，預設 By.CSS_SELECTOR

# In[5]:


def wait_for_element_present(driver, element_position, waiting_time=5, by=By.CSS_SELECTOR):
    try:
        element = WebDriverWait(driver, waiting_time).until(
            EC.presence_of_element_located((by, element_position)))
    except:
        return
    else:
        return element


# ## wait_for_element_clickable(driver, element_position, waiting_time=5, by=By.LINK_TEXT)
# - 同上

# In[6]:


def wait_for_element_clickable(driver, element_position, waiting_time=5, by=By.LINK_TEXT):
    try:
        time.sleep(0.3)
        element = WebDriverWait(driver, waiting_time).until(
            EC.element_to_be_clickable((by, element_position)))
    except:
        return
    else:
        return element


# ## wait_for_url_changed(driver, old_url, waiting_time=10)
# - 用法：
#     - 等待網址改變（輸入的網址和現在的網址進行比較），每間隔 0.5 秒檢查一次，直到 10 秒。如果網址有改變，回傳 True；否則，回傳 None。
# - 參數：
#     - driver
#     - old_url：舊網址
#     - waiting_time：等待時間，預設 10 秒

# In[7]:


def wait_for_url_changed(driver, old_url, waiting_time=10):
    try:
        WebDriverWait(driver, waiting_time).until(EC.url_changes(old_url))
    except:
        return
    else:
        return True


# ## accurately_find_table_and_read_it(driver, table_position, table_index=0)
# - 用法：
#     - 精準定位 table 並讀取成 pd.DataFrame。如果定位 table 成功，回傳 table；否則，回傳 None。
#     - 為 table 增加＂圖書館＂和＂連結＂的欄位。
# - 參數：
#     - table_position：table 位置，預設 CSS selector

# In[8]:


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


# ## select_ISBN_strategy(driver, select_position, option_position, waiting_time=30, by=By.NAME)
# - 用法：
#     - 等待 select 出現，並選擇以 ISBN 方式搜尋
# - 參數：
#     - driver
#     - select_position：select 位置，預設 name
#     - option_position：option 位置，預設 value
#     - waiting_time：等待時間，預設 30 秒
#     - by：預設 By.NAME

# In[9]:


def select_ISBN_strategy(driver, select_position, option_position, waiting_time=30, by=By.NAME):
    time.sleep(0.5)
    search_field = WebDriverWait(driver, waiting_time).until(EC.presence_of_element_located((by, select_position)))
    select = Select(search_field)
    select.select_by_value(option_position)


# ## search_ISBN(driver, ISBN, input_position, waiting_time=10, by=By.NAME)
# - 用法：
#     - 等待 input 出現，輸入 ISBN 並按下 ENTER
# - 參數：
#     - ISBN：ISBN
#     - input_position：input 位置，預設 name
#     - waiting_time：等待時間，預設 10 秒
#     - by：預設 By.NAME

# In[10]:


def search_ISBN(driver, ISBN, input_position, waiting_time=10, by=By.NAME):
    time.sleep(0.5)
    search_input = WebDriverWait(driver, waiting_time).until(EC.presence_of_element_located((by, input_position)))
    search_input.send_keys(ISBN)
    search_input.send_keys(Keys.ENTER)


# # 已完成的爬蟲程式

# ## <mark>完成</mark>webpac_gov_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/02
# - 『函式完成度』：極高

# ### 函式說明
# 
# - 『運作的原理』：
# - 『適用的機構』：[宜蘭縣公共圖書館](https://webpac.ilccb.gov.tw/)、[桃園市立圖書館](https://webpac.typl.gov.tw/)、[高雄市立圖書館](https://webpacx.ksml.edu.tw/)、[屏東縣公共圖書館](https://library.pthg.gov.tw/)、[花蓮縣公共圖書館](https://center.hccc.gov.tw/)、[澎湖縣公共圖書館](https://webpac.phlib.nat.gov.tw/)、[國立雲林科技大學](https://www.libwebpac.yuntech.edu.tw/)、[國家電影及視聽文化中心](https://lib.tfi.org.tw/)
# - 『能處理狀況』：判斷搜尋結果有沒有超過一筆、只有一筆搜尋結果有沒有跳轉、[多筆](https://webpac.typl.gov.tw/search?searchField=ISBN&searchInput=986729193X)、找不到書、[不斷的點擊＂載入更多＂](https://webpac.ilccb.gov.tw/bookDetail/419482?qs=%7B%5Eurl3%2C%2Fsearch4%2Cquery%5E%3A%7B%5Ephonetic3%2C04%2CqueryType3%2C04%2C%2Cs23%2CISBN4%2C%2Cs13%2C9789573317241%5E%7D%7D)
# - 『下一步優化』：

# ### 函式本體

# In[11]:


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


# In[12]:


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


# ## <mark>完成</mark>webpac_jsp_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/02
# - 『函式完成度』：極高

# ### 函式說明
# - 『運作的原理』：
#     - 使用 selenium 進行搜索。
#     - 大量使用 wait 機制，來應對加載過慢的網頁（例：[佛光大學](http://libils.fgu.edu.tw/webpacIndex.jsp)）
#     - 當搜尋結果只有一筆時，有些網站會直接進入＂書目資料＂（例：[國立宜蘭大學](https://lib.niu.edu.tw/webpacIndex.jsp)）
#         - 還是會停留在＂搜尋結果＂頁面，但大部分會看不到，網址仍會改變，所以無法用網址判定
#     - 當搜尋結果有多筆時，會要切換到 iframe 爬取。
#     - 有些＂書目資料＂會有沒有表格的情況（例：[中華科大](http://192.192.231.232/bookDetail.do?id=260965&nowid=3&resid=188809854)）
# - 『適用的機構』：[臺北市立圖書館](https://book.tpml.edu.tw/webpac/webpacIndex.jsp)、[國立宜蘭大學](https://lib.niu.edu.tw/webpacIndex.jsp)、[佛光大學](http://libils.fgu.edu.tw/webpacIndex.jsp)、[嘉南藥理大學](https://webpac.cnu.edu.tw/webpacIndex.jsp)、……
# - 『能處理狀況』：[一筆](http://webpac.meiho.edu.tw/bookDetail.do?id=194508)、[無](http://webpac.meiho.edu.tw/bookSearchList.do?searchtype=simplesearch&search_field=ISBN&search_input=97895733172411&searchsymbol=hyLibCore.webpac.search.common_symbol&execodehidden=true&execode=&ebook=)、[多筆](http://webpac.meiho.edu.tw/bookSearchList.do?searchtype=simplesearch&execodeHidden=true&execode=&search_field=ISBN&search_input=9789573317241&searchsymbol=hyLibCore.webpac.search.common_symbol&resid=189006169&nowpage=1#searchtype=simplesearch&execodeHidden=true&execode=&search_field=ISBN&search_input=9789573317241&searchsymbol=hyLibCore.webpac.search.common_symbol&resid=189006169&nowpage=1)、[無表格](http://192.192.231.232/bookDetail.do?id=260965&nowid=3&resid=188809854)
# - 『下一步優化』：
#     - 統一 search_input.submit() 和 search_input.send_keys(Keys.ENTER)？

# ### 函式本體

# In[13]:


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


# ## <mark>完成</mark>easy_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/02
# - 『函式完成度』：極高

# ### 函式說明
# - 『運作的原理』：待輸入
# - 『適用的機構』：[國立臺灣師範大學](https://opac.lib.ntnu.edu.tw/search*cht/i)、[國立臺灣科技大學](https://sierra.lib.ntust.edu.tw/search*cht/i)、[國立臺灣海洋大學](https://ocean.ntou.edu.tw/search*cht/i)、[中原大學](http://cylis.lib.cycu.edu.tw/search*cht/i)、[逢甲大學](https://innopac.lib.fcu.edu.tw/search*cht/i)、[朝陽科技大學](https://millennium.lib.cyut.edu.tw/search*cht/i)、[國立中山大學](https://dec.lib.nsysu.edu.tw/search*cht/i)、[國立高雄師範大學](https://nknulib.nknu.edu.tw/search*cht/i)、[文藻外語大學](https://libpac.wzu.edu.tw/search*cht/i)、[大仁科技大學](http://lib.tajen.edu.tw/search*cht/i)、[國立中央大學](https://opac.lib.ncu.edu.tw/search*cht/i)
# - 『能處理狀況』：一筆、無
# - 『下一步優化』：
#     - 待輸入
#     - 待輸入

# ### 函式本體

# In[14]:


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


# ## <mark>完成</mark>webpac_pro_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/02
# - 『函式完成度』：極高

# ### 函式說明
# - 『運作的原理』：待輸入
# - 『適用的機構』：[中央研究院](https://las.sinica.edu.tw/*cht)、[中國文化大學](https://webpac.pccu.edu.tw/*cht)、[輔仁大學](https://library.lib.fju.edu.tw/)、[國立陽明交通大學](https://library.ym.edu.tw/screens/opacmenu_cht_s7.html)
# - 『能處理狀況』：一筆、無
# - 『下一步優化』：
#     - 待輸入
#     - 待輸入

# ### 函式本體

# In[15]:


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


# ## <mark>完成</mark>webpac_ajax_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/02
# - 『函式完成度』：極高

# ### 函式說明
# - 『運作的原理』：使用 selenium 進行搜索，進入＂書目資料＂頁面後，從該網址分析並得到 mid，在由此進入 ajax_page。
# - 『適用的機構』：[新北市立圖書館](https://webpac.tphcc.gov.tw/webpac/search.cfm)、[高雄市立空中大學](https://webpac.ouk.edu.tw/webpac/search.cfm)、[國立屏東大學](https://webpac.nptu.edu.tw/webpac/search.cfm)
# - 『能處理狀況』：判斷搜尋結果有沒有超過一筆、只有一筆搜尋結果有沒有跳轉、找不到書
# - 『下一步優化』：當搜尋無結果時，可以直接結束。

# ### 函式本體

# In[16]:


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
        elif wait_for_element_present(driver, 'div.book-detail'):  # 高雄市立空中大學、國立屏東大學才會遇到跳轉
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


# ## <mark>完成</mark>webpac_aspx_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/03
# - 『函式完成度』：高

# ### 函式說明
# - 『運作的原理』：一直切 iframe
# - 『適用的機構』：[樹德科技大學](https://webpac.stu.edu.tw/webopac/)、[台灣首府大學](http://120.114.1.19/webopac/Jycx.aspx?dc=1&fc=1&n=7)、[崑山科技大學](https://weblis.lib.ksu.edu.tw/webopac/)、、、
# - 『能處理狀況』：一筆、多筆、無
# - 『下一步優化』：
#     - 無法取得＂書目資料＂的網址，用的是 JavaScript 語法
#     - ugly code

# ### 函式本體

# In[17]:


def webpac_aspx_crawler(driver, org, org_url, ISBN):
    try:
        table = []

        driver.get(org_url)

        time.sleep(1.5)
        iframe = wait_for_element_present(driver, 'default', by=By.NAME)
        driver.switch_to.frame(iframe)
        select_ISBN_strategy(driver, 'ctl00$ContentPlaceHolder1$ListBox1', 'Info000076')
        search_ISBN(driver, ISBN, 'ctl00$ContentPlaceHolder1$TextBox1')
        driver.switch_to.default_content()
        
        i = 0
        while True:
            time.sleep(1.5)
            iframe = wait_for_element_present(driver, 'default', by=By.NAME)
            driver.switch_to.frame(iframe)
            try:
                wait_for_element_present(driver, f'//*[@id="ctl00_ContentPlaceHolder1_dg_ctl0{i+2}_lbtgcd2"]', by=By.XPATH).click()
            except:
                break
            driver.switch_to.default_content()

            time.sleep(1.5)
            iframe = wait_for_element_present(driver, 'default', by=By.NAME)
            driver.switch_to.frame(iframe)
            tgt = accurately_find_table_and_read_it(driver, '#ctl00_ContentPlaceHolder1_dg')
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


# In[18]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_aspx_crawler(
#     driver=driver,
#     org='弘光科技大學',
#     org_url='https://webpac.hk.edu.tw/webopac/',
#     ISBN='9789869109321'
# )


# ## <mark>完成</mark>uhtbin_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/03
# - 『函式完成度』：高

# ### 函式說明
# - 『運作的原理』：待輸入
# - 『適用的機構』：[國立臺北護理健康大學](http://140.131.94.8/uhtbin/webcat)、[大同大學](http://140.129.23.14/uhtbin/webcat)、[國立體育大學](http://192.83.181.243/uhtbin/webcat)
# - 『能處理狀況』：一筆、無
# - 『下一步優化』：
#     - 待輸入
#     - 待輸入

# ### 函式本體

# In[19]:


def uhtbin_crawler(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)
        try:
            select_ISBN_strategy(driver, 'srchfield1', 'GENERAL^SUBJECT^GENERAL^^所有欄位')
        except:
            select_ISBN_strategy(driver, 'srchfield1', '020^SUBJECT^SERIES^Title Processing^ISBN')
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


# In[20]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# uhtbin_crawler(
#     driver=driver,
#     org='大同大學',
#     org_url='http://140.129.23.14/uhtbin/webcat',
#     ISBN='9789861371955'
# )


# ## <mark>完成</mark>toread_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/05
# - 『函式完成度』：高、爆複雜

# ### 函式說明
# - 『運作的原理』：待輸入
# - 『適用的機構』：[彰化縣圖書館](https://library.toread.bocach.gov.tw/toread/opac)、toread 系統
# - 『能處理狀況』：一筆、無、多筆、[翻頁](https://library.toread.bocach.gov.tw/toread/opac/bibliographic_view?NewBookMode=false&id=341724&mps=10&q=986729193X+OR+9789867291936&start=0&view=CONTENT)
# - 『下一步優化』：
#     - 待輸入

# ### 函式本體

# In[21]:


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
                    tgt = accurately_find_table_and_read_it(driver, 'table.gridTable')
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


# In[22]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# toread_crawler(
#     driver=driver,
#     org='高雄醫學大學',
#     org_url='https://toread.kmu.edu.tw/toread/opac',
#     ISBN='9789861371955'
# )


# ## <mark>完成</mark>連江縣公共圖書館(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/03
# - 『函式完成度』：極高

# ### 函式說明
# - 『運作的原理』：待輸入
# - 『適用的機構』：[連江縣公共圖書館](http://210.63.206.76/Webpac2/msearch.dll/)、[開南大學](http://www.lib.knu.edu.tw/Webpac2/msearch.dll/)
# - 『能處理狀況』：一筆、無
# - 『下一步優化』：
#     - 開南大學搜尋哈利波特會有多個情況

# ### 函式本體

# In[23]:


def 連江縣公共圖書館(driver, org, org_url, ISBN):
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


# # 自我獨立的爬蟲程式

# ## <mark>完成</mark>國家圖書館(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/02
# - 『函式完成度』：極高

# ### 函式說明
# - 『運作的原理』：使用 Selenium
# - 『適用的機構』：[國家圖書館](https://aleweb.ncl.edu.tw/F)
# - 『能處理狀況』：找不到、一筆、[無表格內容](https://aleweb.ncl.edu.tw/F/MPXYG72FRS6Q4T31JTU5GKITQSE7B3ASA51D88R8BSTBT6T6E5-03970?func=item-global&doc_library=TOP02&doc_number=003632992&year=&volume=&sub_library=)
# - 『下一步優化』：
#     - 9789861371955
#     - 目前尚未遇到多筆情況
#     - 不知道可以和什麼機構的系統合併在一起？

# ### 函式本體

# In[24]:


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


# ## <mark>完成</mark>世新大學(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/03
# - 『函式完成度』：極高

# ### 函式說明
# - 『運作的原理』：待輸入
# - 『適用的機構』：[世新大學](https://koha.shu.edu.tw/)
# - 『能處理狀況』：一筆、無
# - 『下一步優化』：
#     - 待輸入
#     - 待輸入

# ### 函式本體

# In[25]:


def 世新大學(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)
        search_ISBN(driver, ISBN, 'request')

        table = accurately_find_table_and_read_it(driver, '#holdingst')
        table['圖書館'], table['連結'] = org, driver.current_url
        table = organize_columns(table)
    except Exception as e:
        print(f'在「{org}」找不到「{ISBN}」')
        return
    else:
        return table


# In[26]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# 世新大學(
#     driver=driver,
#     org='世新大學',
#     org_url='https://koha.shu.edu.tw/',
#     ISBN='9789573317241'
# )


# ## 國立臺灣博物館

# In[27]:


# ISBN = 9789865321703  # 少男少女見學中 : 日本時代修學旅行開箱
# org_url = 'https://lib.moc.gov.tw/F'

# my_options = Options()
# my_options.add_argument("--incognito")  # 開啟無痕模式
# # my_options.add_argument("--headless")  # 不開啟實體瀏覽器
# driver = webdriver.Chrome(options=my_options)
# driver.get("")

# time.sleep(1)  # 為了等待網頁加載
# select = Select(driver.find_element_by_name("x"))
# select.select_by_visible_text(u"ISBN")

# search_input = driver.find_element_by_name("y")
# search_input.send_keys(ISBN)
# # search_input.submit()  # 不知道為什麼無法 submit()？
# submit_input = driver.find_element_by_name("Search")
# submit_input.click()

# click = driver.find_element_by_xpath("/html/body/table[9]/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/a")
# click.click()

# html_text = driver.page_source
# dfs = pd.read_html(html_text, encoding="utf-8")
# df_ntm = dfs[11]
# df_ntm


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# # 靖妤的爬蟲程式

# ## <mark>完成</mark>webpac_two_cralwer(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/05
# - 『編輯者』：靖妤、仕瑋
# - 『運用的機構』：[國立臺北藝術大學](http://203.64.5.158/webpac/)、[國立勤益科技大學](http://140.128.95.172/webpac/)、[義守大學](http://webpac.isu.edu.tw/webpac/)、[中山醫學大學](http://140.128.138.208/webpac/)

# ### 函式本體

# In[41]:


def webpac_two_cralwer(driver, org, org_url, ISBN):
    try:
        tgt_url = f'{org_url}search/?q={ISBN}&field=isn&op=AND&type='
        driver.get(tgt_url)
        
        wait_for_element_clickable(driver, '/html/body/div/div[1]/div[2]/div/div/div[2]/div[3]/div[1]/div[3]/div/ul/li/div/div[2]/h3/a', waiting_time=15, by=By.XPATH).click()
        
        table = accurately_find_table_and_read_it(driver, '#LocalHolding > table')
        table['圖書館'], table['連結'] = org, driver.current_url
        
        # 特殊狀況：國家衛生研究院
        if 'http://webpac.nhri.edu.tw/webpac/' in org_url:
            table.rename(columns={'館藏狀態': 'wow', '狀態／到期日': '館藏狀態'}, inplace=True)
        
        table = organize_columns(table)
    except:
        print(f'在「{org}」找不到「{ISBN}」')
        return
    else:
        return table


# In[42]:


driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
webpac_two_cralwer(
    driver=driver,
    org='國家衛生研究院',
    org_url='http://webpac.nhri.edu.tw/webpac/',
    ISBN='9789861371955'
)


# In[30]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_two_cralwer(
#     driver=driver,
#     org='國立臺北藝術大學',
#     org_url='http://203.64.5.158/webpac/',
#     ISBN='9789861371955'
# )


# ## <mark>完成</mark>台北海洋科技大學(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/03
# - 『編輯者』：靖妤
# - 『運用的機構』：[台北海洋科技大學](http://140.129.253.4/webopac7/sim_data2.php?pagerows=15&orderby=BRN&pageno=1&bn=986729193X)

# In[31]:


def 台北海洋科技大學(driver, org, org_url, ISBN):
    try:
        df_lst = []
        org_url = org_url + ISBN
        driver.get(org_url)
        result = driver.find_element_by_id("qresult-content")
        trlist = result.find_elements_by_tag_name('tr')
        for row in range(2, len(trlist)):
            css = "#qresult-content > tbody > tr:nth-child(" + str(row) + ") > td:nth-child(3) > a"
            into = driver.find_element_by_css_selector(css).click()
            time.sleep(2)
            html_text = driver.page_source
            dfs = pd.read_html(html_text, encoding="utf-8")
            df_tumt = dfs[6]
            df_tumt.rename(columns={1: "館藏地", 3: "索書號", 4: "館藏狀態"}, inplace=True)
            df_tumt.drop([0], inplace=True)
            df_tumt["圖書館"], df_tumt["連結"] = "台北海洋科技大學", driver.current_url
            df_tumt = organize_columns(df_tumt)
            df_lst.append(df_tumt)
            back = driver.find_element_by_css_selector("#table1 > tbody > tr > td:nth-child(1) > a:nth-child(3)").click()
        table = pd.concat(df_lst, axis=0, ignore_index=True)
    except Exception as e:
            print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
            return
    else:
        return table


# In[32]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# 台北海洋科技大學(
#     driver=driver,
#     org='台北海洋科技大學',
#     org_url='http://140.129.253.4/webopac7/sim_data2.php?pageno=1&pagerows=15&orderby=BRN&ti=&au=&se=&su=&pr=&mt=&mt2=&yrs=&yre=&nn=&lc=&bn=',
#     ISBN='986729193X'
# )


# ## <font color='red'>進行中</font>primo_crawler(driver, org, url_front, ISBN ,url_behind , tcn)

# - 『最後編輯』：2021/08/03
# - 『編輯者』：靖妤
# - 『運用的機構』：[國立臺灣大學](https://ntu.primo.exlibrisgroup.com/discovery/search?sortby=rank&vid=886NTU_INST:886NTU_INST&lang=zh-tw)

# In[33]:


#台大、政大、淡江、東吳、然後銘傳沒有索書碼QQ(要另外進去但我懶🙄)
def primo_finding(driver, org, tcn): #primo爬資訊的def ；#tcn = thelist_class_name
    sub_df_lst = []
    time.sleep(5)
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


# In[34]:


def primo_crawler(driver, org, url_front, ISBN ,url_behind, tcn):
    table = []
    
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
                    time.sleep(10)
                    primo_lst += primo_finding(org, tcn, driver)
                    table = pd.concat(primo_lst, axis=0, ignore_index=True)
                    try: 
                        back2 = driver.find_element_by_class_name("md-icon-button.close-button.full-view-navigation.md-button.md-primoExplore-theme.md-ink-ripple").click()
                    except:
                        back2 = None

            else: #如果只有一個版本(有叉叉的意思)，那前面已經click過了不能再做
                time.sleep(12)
                primo_lst += primo_finding(driver, org, tcn)
                table = pd.DataFrame(primo_lst)
                table.rename(columns={0: '圖書館', 1: '館藏地', 2: '索書號', 3: '館藏狀態', 4: '連結'}, inplace=True)
        except:
            pass
    except:
        pass
    return table


# In[35]:


# # 待測試
# driver = webdriver.Chrome()
# table = primo_crawler(
#     driver=driver,
#     org='國立臺灣大學',
#     url_front='https://ntu.primo.exlibrisgroup.com/discovery/search?query=any,contains,',
#     ISBN='9789573317241',
#     url_behind='&tab=Everything&search_scope=MyInst_and_CI&vid=886NTU_INST:886NTU_INST&offset=0',
#     tcn='layout-align-space-between-center.layout-row.flex-100'
# )
# table


# In[ ]:





# In[ ]:





# In[36]:


# primo_crawler(
#     driver=driver,
#     org='國立政治大學',
#     url_front='https://nccu.primo.exlibrisgroup.com/discovery/search?query=any,contains,',
#     ISBN=ISBN,
#     url_behind='&tab=Everything&search_scope=MyInst_and_CI&vid=886NCCU_INST:886NCCU_INST',
#     tcn='layout-align-space-between-center.layout-row.flex-100'
# )
# primo_crawler(
#     driver=driver,
#     org="銘傳大學",
#     url_front="https://uco-mcu.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
#     ISBN=ISBN,
#     url_behind="&tab=Everything&search_scope=MyInst_and_CI&vid=886UCO_MCU:886MCU_INST&lang=zh-tw&offset=0",
#     tcn="md-2-line.md-no-proxy._md"
# )
# primo_crawler(
#     driver=driver,
#     org="東吳大學",
#     url_front="https://uco-scu.primo.exlibrisgroup.com/discovery/search?query=any,contains,",
#     ISBN=ISBN,
#     url_behind"&tab=Everything&search_scope=MyInst_and_CI&vid=886UCO_SCU:886SCU_INST&lang=zh-tw&offset=0",
#     tcn="md-2-line.md-no-proxy._md"
# )


# In[ ]:





# In[ ]:





# ## <font color='red'>進行中</font>台中科技大學

# In[ ]:





# In[ ]:





# In[ ]:





# # 這網頁也太爛了吧……

# ## <font color='red'>待維修</font>基隆市公共圖書館(driver, org, org_url, ISBN) 很奇怪
# - 『最後編輯』：
# - 『函式完成度』：中

# ### 函式說明
# - 『運作的原理』：使用 Selenium
# - 『適用的機構』：[基隆市公共圖書館](https://webpac.klccab.gov.tw/webpac/search.cfm)
# - 『能處理狀況』：一筆、無
# - 『下一步優化』：
#     - 網站載入過慢，且 wait 方式不適用於此，只能使用大量的 time.sleep()

# ### 函式本體

# In[37]:


# def 基隆市公共圖書館(driver, org, org_url, ISBN):
#     try:
#         driver.get(org_url)
#         wait_for_element_clickable(driver, '進階檢索').click()  # 點擊＂進階檢索＂
#         time.sleep(2)  # JavaScript 動畫，強制等待
#         select_ISBN_strategy(driver, 'as_type_1', 'i')
#         search_ISBN(driver, ISBN, 'as_keyword_1')

#         time.sleep(8)  # 基隆的系統太詭異了，強制等待
#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         results = len(soup.find_all("div", "list_box"))
#         if results < 2:
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located(
#                     (By.CSS_SELECTOR, "table.list.list_border")))
#             time.sleep(2)
#             table = pd.read_html(driver.page_source)[0]
#         else:
#             table = []
#             for li in soup.find_all("div", "list_box"):
#                 url_temp = "https://webpac.klccab.gov.tw/webpac/" + li.find(
#                     "a", "btn")["href"]
#                 driver.get(url_temp)
#                 wait.until(
#                     EC.presence_of_element_located(
#                         (By.CSS_SELECTOR, "table.list.list_border")))
#                 time.sleep(2)
#                 table.append(
#                     pd.read_html(driver.page_source, encoding="utf-8")[0])
#             table = pd.concat(table, axis=0, ignore_index=True)
#         table['圖書館'], table['連結'] = org, driver.current_url
#         table = organize_columns(table)
#         return table
#     except:
#         print(f'《{ISBN}》在「{url}」無法爬取')


# In[38]:


# def 基隆市公共圖書館(driver, org, org_url, ISBN):
#     table = []

#     driver.get(org_url)
#     search_ISBN(driver, ISBN, 'ss_keyword')

#     time.sleep(8)  # 基隆的系統太詭異了，強制等待

#     if wait_for_element_present(driver, '.list_border'):  # 一筆
#         tgt = accurately_find_table_and_read_it(driver, '.list_border')
#         tgt['圖書館'], tgt['連結'] = org, driver.current_url
#         table.append(tgt)
#     elif wait_for_element_clickable(driver, '詳細書目'):  # 多筆
#         tgt_urls = []
#         anchors = driver.find_elements_by_link_text('詳細書目')
#         for anchor in anchors:
#             tgt_urls.append(anchor.get_attribute('href'))

#         for tgt_url in tgt_urls:
#             driver.get(tgt_url)

#             if not wait_for_element_present(driver, '.list_border'):
#                 continue
#             tgt = accurately_find_table_and_read_it(driver, '.list_border')
#             tgt['圖書館'], tgt['連結'] = org, driver.current_url
#             table.append(tgt)
#     table = organize_columns(table)
#     return table

