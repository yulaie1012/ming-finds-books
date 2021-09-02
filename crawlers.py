#!/usr/bin/env python
# coding: utf-8

# # 環境設置

# ## 載入套件
# - selenium、pandas、requests、bs4、time

# In[3]:


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
import requests
from bs4 import BeautifulSoup
import time  # 強制等待
import inspect


# ## 設定 driver 的參數：options、desired_capabilities

# In[2]:


my_options = Options()
my_options.add_argument('--incognito')  # 開啟無痕模式
# my_options.add_argument('--start-maximized')  # 視窗最大化
my_options.add_argument('--headless')  # 不開啟實體瀏覽器
my_capabilities = DesiredCapabilities.CHROME
my_capabilities['pageLoadStrategy'] = 'eager'  # 頁面加載策略：HTML 解析成 DOM

def get_chrome():
    return webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)


# In[3]:


ORG_TO_URL = {
  "臺北市立圖書館": "https://book.tpml.edu.tw/webpac/webpacIndex.jsp",
  "新竹市圖書館": "https://webpac.hcml.gov.tw/webpacIndex.jsp",
  "新竹縣公共圖書館": "https://book.hchcc.gov.tw/webpacIndex.jsp",
  "國立宜蘭大學": "https://lib.niu.edu.tw/webpacIndex.jsp",
  "佛光大學": "http://libils.fgu.edu.tw/webpacIndex.jsp",
  "經國管理暨健康學院": "http://203.64.136.248/webpacIndex.jsp",
  "臺北醫學大學": "https://libelis.tmu.edu.tw/webpacIndex.jsp",
  "國立臺灣藝術大學": "http://webpac.ntua.edu.tw/webpacIndex.jsp",
  "中國科技大學": "https://webpac.cute.edu.tw/webpacIndex.jsp",
  "臺北市立大學": "http://lib.utaipei.edu.tw/webpac/webpacIndex.jsp",
  "國立臺北商業大學": "http://webpac.ntub.edu.tw/webpacIndex.jsp",
  "中華科技大學": "http://192.192.231.232/webpacIndex.jsp",
  "臺北基督學院": "http://webpac.cct.edu.tw/webpacIndex.jsp",
  "宏國德霖科技大學": "http://210.60.142.23/webpacIndex.jsp",
  "景文科技大學": "https://jinwenlib.just.edu.tw/webpacIndex.jsp",
  "致理科技大學": "http://hylib.chihlee.edu.tw/webpacIndex.jsp",
  "萬能科技大學": "http://webpac.lib.vnu.edu.tw/webpacIndex.jsp",
  "健行科技大學": "https://library.uch.edu.tw/webpacIndex.jsp",
  "明新科技大學": "https://hylib.lib.must.edu.tw/webpacIndex.jsp",
  "國立空中大學": "https://hyweblib.nou.edu.tw/webpac/webpacIndex.jsp",
  "苗栗縣公共圖書館": "https://webpac.miaoli.gov.tw/webpacIndex.jsp",
  "育達科技大學": "http://120.106.11.155/webpacIndex.jsp",
  "仁德醫護管理專科學校": "http://libopac.jente.edu.tw/webpacIndex.jsp",
  "國立臺中教育大學": "http://webpac.lib.ntcu.edu.tw/webpacIndex.jsp",
  "國立臺灣體育運動大學": "https://hylib.ntus.edu.tw/webpacIndex.jsp",
  "東海大學": "https://webpac.lib.thu.edu.tw/webpacIndex.jsp",
  "靜宜大學": "http://webpac.lib.pu.edu.tw/webpac/webpacIndex.jsp",
  "僑光科技大學": "http://lib.webpac.ocu.edu.tw/webpacIndex.jsp",
  "國立彰化師範大學": "https://book.ncue.edu.tw/webpacIndex.jsp",
  "雲林縣公共圖書館": "http://library.ylccb.gov.tw/webpacIndex.jsp",
  "嘉義縣圖書館": "https://www.cycab.gov.tw/webpacIndex.jsp",
  "嘉義市政府文化局": "http://library.cabcy.gov.tw/webpacIndex.jsp",
  "南華大學": "http://hylib.nhu.edu.tw//webpacIndex.jsp",
  "嘉南藥理大學": "http://webpac.cnu.edu.tw/webpacIndex.jsp",
  "遠東科技大學": "http://hy.lib.feu.edu.tw/webpacIndex.jsp",
  "正修科技大學": "https://webpac2.csu.edu.tw/webpacIndex.jsp",
  "美和科技大學": "http://webpac.meiho.edu.tw/webpacIndex.jsp",
  "國立臺東大學": "http://hylib.lib.nttu.edu.tw/webpac/webpacIndex.jsp",
  "國立金門大學": "https://lib.nqu.edu.tw/webpacIndex.jsp",
  "金門縣圖書館": "https://library.kmccc.edu.tw/webpacIndex.jsp",
  "臺東縣圖書館": "http://library.ccl.ttct.edu.tw/webpacIndex.jsp",
  "國立臺北科技大學": "https://libholding.ntut.edu.tw/webpacIndex.jsp",
}


# In[4]:


column2 = {
    '分館/專室', '館藏地/室', '館藏室', '館藏地/館藏室', '館藏地', '典藏館', '館藏位置', '館藏地/區域',
    '典藏地名稱', '館藏地/館別', '館藏地(已外借/總數)', '館藏地/區域Location', '現行位置', '典藏地點', '典藏區域',
    '書架位置'
}
column3 = {'索書號', '索書號/期刊合訂本卷期', '索書號 / 部冊號', '索書號Call No.', '索書號(卷期)'}
column4 = {
    '館藏位置(到期日期僅為期限，不代表上架日期)', '狀態/到期日', '目前狀態 / 到期日', '館藏狀態', '處理狀態',
    '狀態 (說明)', '館藏現況 說明', '目前狀態/預計歸還日期', '圖書狀況 / 到期日', '調閱說明', '借閱狀態', '狀態',
    '館藏狀態(月-日-西元年)', '圖書狀況', '現況/異動日', 'Unnamed: 24', '圖書狀況Book Status',
    '館藏狀況(月-日-西元年)', '現況', '處理狀態 (狀態說明)', '狀態／到期日'
}


# # 自定義函式

# ## organize_columns(df_list)
# - 處理欄位：圖書館、館藏地（c2）、索書號（c3）、館藏狀態（c4）、連結
# - 如果 df1 是裝著 DataFrame 的 list，則就合併它們；否則（df1 是 DataFrame），就接著執行以下敘述。
# - 丟掉垃圾欄位，整理成要呈現的表格
# - 新增必要欄位（圖書館、連結）
# - 填滿 NaN（用 ffill 的 方式）

# In[5]:


def organize_columns(df_list):
    print(df_list)
    try:
        df1 = pd.concat(df_list, axis=0, ignore_index=True)
    except:
        df1 = df_list.reset_index(drop=True)
    
    df1_columns = set(df1.columns)

    df1['column2'] = ''
    for c in column2 & df1_columns:
        df1['column2'] += df1[c]

    df1['column3'] = ''
    for c in column3 & df1_columns:
        df1['column3'] += df1[c]

    df1['column4'] = ''
    for c in column4 & df1_columns:
        df1['column4'] += df1[c]

    # 直接生成另一個 DataFrame
    df2 = pd.DataFrame()
    df2['圖書館'] = df1['圖書館']
    df2['館藏地'] = df1['column2']
    df2['索書號'] = df1['column3']
    df2['館藏狀態'] = df1['column4']
    df2['連結'] = df1['連結']

    # 遇到值為 NaN時，將前一列的值填補進來
    df2.fillna(method="ffill", axis=0, inplace=True)

    return df2


# ## DEFINED FUNCTIONS

# In[4]:


def plot_horizontal_line():
    print('='*50)

def alert_execution_report(function):
    plot_horizontal_line()
    print(f'EXECUTE {function.__name__} FUNCTION!')

def alert_exception_report(function, exception):
    print(f'STOP {function.__name__} FUNCTION, MESSAGE: "{exception}"'.replace('\n', ''))
    plot_horizontal_line()

def alert_completion_report(function):
    print(f'COMPLETE {function.__name__} FUNCTION')
    plot_horizontal_line()

def node_off(waiting_time=0.5):
    time.sleep(waiting_time)

def wait_for_element_present(driver, element_position, waiting_time=5, by=By.CSS_SELECTOR):
    function = wait_for_element_present
    alert_execution_report(function)
    try:
        node_off()
        element = WebDriverWait(driver, waiting_time).until(EC.presence_of_element_located((by, element_position)))
    except Exception as e:
        alert_exception_report(function, e)
        return False
    else:
        alert_completion_report(function)
        return element

def wait_for_elements_present(driver, elements_position, waiting_time=5, by=By.CSS_SELECTOR):
    function = wait_for_elements_present
    alert_execution_report(function)
    try:
        node_off()
        elements = WebDriverWait(driver, waiting_time).until(EC.presence_of_all_elements_located((by, elements_position)))
    except Exception as e:
        alert_exception_report(function, e)
        return False
    else:
        alert_completion_report(function)
        return elements

def wait_for_element_clickable(driver, element_position, waiting_time=5, by=By.LINK_TEXT):
    function = wait_for_element_clickable
    alert_execution_report(function)
    try:
        node_off()
        element = WebDriverWait(driver, waiting_time).until(EC.element_to_be_clickable((by, element_position)))
    except Exception as e:
        alert_exception_report(function, e)
        return False
    else:
        alert_completion_report(function)
        return element

def accurately_find_table_and_read_it(driver, table_position, table_index=0):
    function = accurately_find_table_and_read_it
    alert_execution_report(function)
    try:
        if not wait_for_element_present(driver, table_position):
            alert_exception_report(function, 'not found table')
            return
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_innerHTML = soup.select(table_position)[table_index]
        tgt = pd.read_html(str(table_innerHTML), encoding='utf-8')[0]
        # tgt['圖書館'], tgt['連結'] = org, driver.current_url
    except Exception as e:
        alert_exception_report(function, e)
        return
    else:
        alert_completion_report(function)
        return tgt

def select_ISBN_strategy(driver, select_position, option_position, waiting_time=30, by=By.NAME):
    function = select_ISBN_strategy
    alert_execution_report(function)
    try:
        search_field = WebDriverWait(driver, waiting_time).until(EC.presence_of_element_located((by, select_position)))
        select = Select(search_field)
        node_off()
        select.select_by_value(option_position)
    except Exception as e:
        alert_completion_report(function)
        return

def search_ISBN(driver, ISBN, input_position, waiting_time=10, by=By.NAME):
    function = search_ISBN
    alert_execution_report(function)
    try:
        search_input = WebDriverWait(driver, waiting_time).until(EC.presence_of_element_located((by, input_position)))
        search_input.send_keys(ISBN)
        node_off()
        search_input.send_keys(Keys.ENTER)
        alert_completion_report(function)
    except Exception as e:
        alert_exception_report(function, e)
        return

def get_all_tgt_urls(driver):
    tgt_urls = []

    anchors = driver.find_elements(By.LINK_TEXT, '詳細內容')
    if anchors == []:
        anchors = driver.find_elements(By.LINK_TEXT, '內容')
    for anchor in anchors:
        tgt_urls.append(anchor.get_attribute('href'))

    return tgt_urls


# # 已完成的爬蟲程式

# In[7]:


def get_all_arguments(function):
    return [locals()[arg] for arg in inspect.getargspec(function).args]


# ## <mark>完成</mark>webpac_jsp_crawler(driver, org, ISBN)
# - 『最後編輯』：2021/09/01
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

# In[8]:


def webpac_jsp_crawler(driver, org, org_url, ISBN):
    function = webpac_jsp_crawler
    alert_execution_report(function)
    try:
        table = []
        
        driver.get(org_url)
        try:
            select_ISBN_strategy(driver, 'search_field', 'ISBN')
        except:
            select_ISBN_strategy(driver, 'search_field', 'STANDARDNO')  # 北科大
        search_ISBN(driver, ISBN, 'search_input')
        
        # 一筆
        if wait_for_element_present(driver, 'table.order'):
            i = 0
            while True:
                try:
                    tgt = accurately_find_table_and_read_it(driver, 'table.order')
                    tgt['圖書館'], tgt['連結'] = org, driver.current_url
                    table.append(tgt)

                    wait_for_element_clickable(driver, str(2+i), 2).click()
                    i += 1
                    time.sleep(0.5)
                except:
                    break
        # 多筆、零筆
        elif wait_for_element_present(driver, 'iframe#leftFrame'):
            iframe = driver.find_element_by_id('leftFrame')
            driver.switch_to.frame(iframe)
            time.sleep(1.5)  # 切換到 <frame> 需要時間，否則會無法讀取
            
            # 判斷是不是＂零筆＂查詢結果
            if wait_for_element_present(driver, '#totalpage').text == '0':
                alert_exception_report(function, 'not found book')
                return
            
            # ＂多筆＂查詢結果
            tgt_urls = get_all_tgt_urls(driver)

            for tgt_url in tgt_urls:
                driver.get(tgt_url)
                # 等待元素出現，如果出現，那麼抓取 DataFrame；如果沒出現，那麼跳出迴圈
                if wait_for_element_present(driver, 'table.order'):
                    i = 0
                    while True:
                        try:
                            tgt = accurately_find_table_and_read_it(driver, 'table.order')
                            tgt['圖書館'], tgt['連結'] = org, driver.current_url
                            table.append(tgt)

                            wait_for_element_clickable(driver, str(2+i), 2).click()
                            i += 1
                            time.sleep(0.5)
                        except:
                            break
                else:
                    continue
        table = organize_columns(table)
    except Exception as e:
        alert_exception_report(function, e)
        return
    else:
        alert_completion_report(function)
        return table


# ### 函式測試

# In[9]:


# driver = get_chrome()
# webpac_jsp_crawler(
#     driver=driver, 
#     org='佛光大學',
#     org_url='http://libils.fgu.edu.tw/webpacIndex.jsp',
#     ISBN='9789573317241'
# )


# In[10]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_jsp_crawler(
#     driver=driver, 
#     org='國立空中大學', 
#     org_url='https://hyweblib.nou.edu.tw/webpac/webpacIndex.jsp', 
#     ISBN='9789573317241'
# )


# In[11]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_jsp_crawler(
#     driver=driver, 
#     org='育達科技大學', 
#     org_url='https://hyweblib.nou.edu.tw/webpac/webpacIndex.jsp', 
#     ISBN='9789573317241'
# )


# In[12]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_jsp_crawler(
#     driver=driver, 
#     org='國立金門大學', 
#     org_url='https://lib.nqu.edu.tw/webpacIndex.jsp', 
#     ISBN='9789573317241'
# )


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

# In[13]:


def click_more_btn(driver):
    function = wait_for_elements_present
    alert_execution_report(function)
    try:
        while True:
            more_btn = wait_for_element_clickable(driver, '載入更多')
            if not more_btn:
                return
            more_btn.click()
            time.sleep(2)  # 不得已的強制等待
    except:
        return


# In[14]:


def webpac_gov_crawler(driver, org, org_url, ISBN):
    function = webpac_gov_crawler
    alert_execution_report(function)
    try:
        table = []

        driver.get(org_url + 'advanceSearch')
        select_ISBN_strategy(driver, 'searchField', 'ISBN')
        search_ISBN(driver, ISBN, 'searchInput')

        # 一筆
        if wait_for_element_present(driver, '.bookplace_list > table', 10):
            print(f'「webpac_gov_crawler({org})」，只有一筆搜尋結果')
            click_more_btn(driver)
            
            tgt = accurately_find_table_and_read_it(driver, '.bookplace_list > table')
            tgt['圖書館'], tgt['連結'] = org, driver.current_url
            table.append(tgt)
            print('抓取 table 成功')
        # 多筆
        elif wait_for_element_present(driver, '.data_all .data_quantity2 em', 5):
            print(f'「webpac_gov_crawler({org})」，有多筆搜尋結果')
            # 取得多個連結
            tgt_urls = []
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            anchors = soup.select('.bookdata > h2 > a')
            for anchor in anchors:
                tgt_urls.append(org_url + anchor['href'])
            
            # 進入不同的連結
            i = 1
            for tgt_url in tgt_urls:
                driver.get(tgt_url)
                print(f'進入第 {i} 個頁面')
                
                if wait_for_element_present(driver, '.bookplace_list > table', 10):
                    click_more_btn(driver)
                    tgt = accurately_find_table_and_read_it(driver, '.bookplace_list > table')
                    tgt['圖書館'], tgt['連結'] = org, driver.current_url
                    table.append(tgt)
                    print('抓取 table 成功')
                i += 1
            print('for 迴圈結束')
        # 無
        else:
            print(f'「webpac_gov_crawler({org})」，找不到「{ISBN}」')
            return
    except Exception as e:
        print(f'「webpac_gov_crawler({org})」，搜尋「{ISBN}」時，發生錯誤：「{e}」！')
        return
    else:
        return organize_columns(table)


# In[15]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_gov_crawler(
#     driver=driver,
#     org='國立雲林科技大學',
#     org_url='https://www.libwebpac.yuntech.edu.tw/',
#     ISBN='9789861371955'
# )


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

# In[16]:


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


# In[17]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# easy_crawler(
#     driver=driver,
#     org='國立臺灣師範大學',
#     org_url='https://opac.lib.ntnu.edu.tw/search*cht/i',
#     ISBN='9789573317241'
# )


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

# In[18]:


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

# In[19]:


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

# In[20]:


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


# In[21]:


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

# In[22]:


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


# In[23]:


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

# In[24]:


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


# In[25]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# toread_crawler(
#     driver=driver,
#     org='高雄醫學大學',
#     org_url='https://toread.kmu.edu.tw/toread/opac',
#     ISBN='9789861371955'
# )


# ## <mark>完成</mark>webpac_cfm_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/12
# - 『函式完成度』：高

# ### 函式說明
# 
# - 『運作的原理』：待輸入
# - 『適用的機構』：search_cfm 結尾
# - 『能處理狀況』：
#     - 多頁表格：[臺中市立圖書館](https://ipac.library.taichung.gov.tw/webpac/search.cfm?m=ss&k0=986729193X&t0=k&c0=and)、
#     - [臺南市立圖書館](https://lib.tnml.tn.edu.tw/webpac/search.cfm)：
#         - [無資料](https://lib.tnml.tn.edu.tw/webpac/search.cfm?m=ss&k0=986729193XX&t0=k&c0=and)
#         - [一筆資料，直接進入＂詳細書目＂](https://lib.tnml.tn.edu.tw/webpac/search.cfm?m=ss&k0=9570825685&t0=k&c0=and)
#         - [＂書目資料＂裡中的表格換頁](https://lib.tnml.tn.edu.tw/webpac/content.cfm?mid=611585&m=ss&k0=986729193X&t0=k&c0=and&si=&content&list_num=10&current_page=1&mt=&at=&sj=&py=&pr=&it=&lr=&lg=&si=1&contentlistcurrent_page=3&contentlist_num=10&lc=0&ye=&vo=&item_status_v=)
#         - [多筆資料](https://lib.tnml.tn.edu.tw/webpac/search.cfm?m=ss&k0=986729193X&t0=k&c0=and)
# - 『下一步優化』：
#     - 基隆市公共圖書館：[只有一筆書目時，會直接進入＂詳細書目＂](https://webpac.klccab.gov.tw/webpac/search.cfm?m=ss&k0=986729193X&t0=k&c0=and)
#     - 國立臺北大學：和其他機構的 class name 不同，是 table.book_location，而不是 table.list_border。

# In[26]:


def crawl_all_tables_on_page(driver, table_position, org, url_pattern):
    table = []
    
    i = 0
    while True:
        try:
            tgt = accurately_find_table_and_read_it(driver, table_position)
            tgt['圖書館'], tgt['連結'] = org, url_pattern
            table.append(tgt)

            wait_for_element_clickable(driver, str(2+i), 2).click()
            i += 1
        except:
            break
    
    return table


# In[27]:


def get_all_tgt_urls(driver, link_text):
    tgt_urls = []

    anchors = driver.find_elements_by_link_text(link_text)
    for anchor in anchors:
        tgt_urls.append(anchor.get_attribute('href'))
    
    return tgt_urls


# In[28]:


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
            table += crawl_all_tables_on_page(driver, table_position, org, driver.current_url)
        
        # Case2. 是否 driver 在＂查詢結果＂的頁面？且有搜尋結果。
        elif wait_for_element_present(driver, 'div#list'):
            tgt_urls = get_all_tgt_urls(driver, '詳細書目')

            for tgt_url in tgt_urls:
                driver.get(tgt_url)
                
                # 是否 driver 在＂書目資料＂的頁面？
                if wait_for_element_present(driver, 'div.info_box'):
                    table += crawl_all_tables_on_page(driver, table_position, org, driver.current_url)
        
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


# In[ ]:





# In[29]:


# # 一筆「二十一世紀資本論」，測試成功
# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_cfm_crawler(
#     driver=driver,
#     org='中國醫藥大學',
#     org_url='http://weblis.cmu.edu.tw/webpac/search.cfm',
#     ISBN='9789869109321'
# )


# In[30]:


# # 兩筆「蘋果橘子經濟學」，測試成功
# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_cfm_crawler(
#     driver=driver,
#     org='臺中市立圖書館',
#     org_url='https://ipac.library.taichung.gov.tw/webpac/search.cfm',
#     ISBN='986729193X'
# )


# In[31]:


# # 三筆「蘋果橘子經濟學」，測試成功
# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_cfm_crawler(
#     driver=driver,
#     org='臺南市圖書館',
#     org_url='https://lib.tnml.tn.edu.tw/webpac/search.cfm',
#     ISBN='986729193X'
# )


# In[32]:


# # 未解決校區問題
# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_cfm_crawler(
#     driver=driver,
#     org='國立臺北大學',
#     org_url='http://webpac.lib.ntpu.edu.tw/search.cfm',
#     ISBN='9789861371955'
# )


# In[33]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_cfm_crawler(
#     driver=driver,
#     org='基隆市公共圖書館',
#     org_url='https://webpac.klccab.gov.tw/webpac/search.cfm',
#     ISBN='9789861371955'
# )


# In[ ]:





# In[ ]:





# ## <mark>完成</mark>sirsidynix_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/14
# - 『函式完成度』：

# ### 函式說明
# - 『適用的機構』：[國立臺中科技大學](https://ntit.ent.sirsidynix.net/client/zh_TW/NUTC)、[南投縣圖書館](https://nccc.ent.sirsi.net/client/zh_TW/main)、[國立臺南藝術大學](https://tnnua.ent.sirsi.net/client/zh_TW/tnnua/?)

# In[34]:


def sirsidynix_crawler(driver, org, org_url, ISBN):
    try:
        table = []

        driver.get(org_url)
        select_ISBN_strategy(driver, 'restrictionDropDown', 'false|||ISBN|||ISBN（國際標準書號）')
        search_ISBN(driver, ISBN, 'q')

        # ＂書目資料＂
        if wait_for_element_present(driver, 'div.detailItems'):
            time.sleep(0.5)

            tgt = accurately_find_table_and_read_it(driver, 'table.detailItemTable')

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

                    tgt = accurately_find_table_and_read_it(driver, 'table.detailItemTable', -1)

                    if 'ntit' in org_url:
                        tgt['館藏地'] = tgt['圖書館'].str.rsplit('-', expand=True)[2]
                    elif 'tnnua' in org_url:
                        tgt['館藏地'] = tgt['狀態'].str.rsplit('-', expand=True)[1]
                        
                    tgt['圖書館'], tgt['連結'] = org, driver.current_url
                    table.append(tgt)

                    try:
                        wait_for_elements_present(driver, '.nextArrowRight')[-1].click()
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


# In[35]:


# # 一筆，測試成功
# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# sirsidynix_crawler(
#     driver=driver,
#     org='國立臺中科技大學',
#     org_url='https://ntit.ent.sirsidynix.net/client/zh_TW/NUTC',
#     ISBN='9789868879348'
# )


# In[36]:


# # 兩筆＂二十一世紀資本論＂，測試成功
# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# sirsidynix_crawler(
#     driver=driver,
#     org='國立臺中科技大學',
#     org_url='https://ntit.ent.sirsidynix.net/client/zh_TW/NUTC',
#     ISBN='9789869109321'
# )


# In[37]:


# # 五筆＂神秘的魔法師＂，測試成功
# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# sirsidynix_crawler(
#     driver=driver,
#     org='南投縣圖書館',
#     org_url='https://nccc.ent.sirsi.net/client/zh_TW/main',
#     ISBN='9789573317241'
# )


# In[38]:


# # 一筆＂神秘的魔法師＂，測試成功
# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# sirsidynix_crawler(
#     driver=driver,
#     org='國立臺南藝術大學',
#     org_url='https://tnnua.ent.sirsi.net/client/zh_TW/tnnua/?',
#     ISBN='9789573317241'
# )


# ## <mark>完成</mark>moc_thm_crawler(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/14
# - 『函式完成度』：

# In[39]:


def moc_thm_crawler(driver, org, org_url, ISBN):
    try:
        driver.get(org_url)

        select_ISBN_strategy(driver, 'find_code', 'ISBN')
        search_ISBN(driver, ISBN, 'request')

        try:
            wait_for_element_present(driver, '/html/body/form/table[1]/tbody/tr[8]/td[3]/a', by=By.XPATH).click()
        except:
            print(f'在「{org}」找不到「{ISBN}」')
            return
        wait_for_element_present(driver, '/html/body/table[9]/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/a', by=By.XPATH).click()

        table = accurately_find_table_and_read_it(driver, 'table', -2)
        table['圖書館'], table['連結'] = org, driver.current_url
    except Exception as e:
        print(f'在「{org}」搜尋「{ISBN}」時，發生錯誤，錯誤訊息為：「{e}」！')
        return
    else:
        table = organize_columns(table)
        return table


# In[40]:


# # 一筆，成功
# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# moc_thm_crawler(
#     driver=driver,
#     org='國立臺灣歷史博物館',
#     org_url='https://lib.moc.gov.tw/F?func=find-d-0&local_base=THM01',
#     ISBN='9789866702709'
# )


# In[41]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# moc_thm_crawler(
#     driver=driver,
#     org='國立臺灣文學館',
#     org_url='https://lib.moc.gov.tw/F?func=find-d-0&local_base=THM02',
#     ISBN='9789866702709'
# )


# In[42]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# moc_thm_crawler(
#     driver=driver,
#     org='國立臺灣史前文化博物館',
#     org_url='https://lib.moc.gov.tw/F?func=find-d-0&local_base=THM04',
#     ISBN='9789576387166'
# )


# In[ ]:





# In[43]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# moc_thm_crawler(
#     driver=driver,
#     org='國立傳統藝術中心',
#     org_url='https://lib.moc.gov.tw/F?func=find-b-0&local_base=MCA05',
#     ISBN='9789860252323'
# )


# In[ ]:





# In[ ]:





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

# In[44]:


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

# In[45]:


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

# In[46]:


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


# In[47]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# 世新大學(
#     driver=driver,
#     org='世新大學',
#     org_url='https://koha.shu.edu.tw/',
#     ISBN='9789573317241'
# )


# ## <mark>完成</mark>敏實科技大學(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/14
# - 『函式完成度』：高

# In[48]:


def 敏實科技大學(driver, org, org_url, ISBN):
    try:
        table = []

        driver.get(org_url)
        search_ISBN(driver, ISBN, 'DB.IN1')

        if wait_for_element_present(driver, 'span.sm9'):
            search_result_message = BeautifulSoup(driver.page_source, 'html.parser').find_all('span', 'sm9')[-2].text
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


# In[49]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# 敏實科技大學(
#     driver=driver,
#     org='敏實科技大學',
#     org_url='http://120.105.200.52/xsearch-b.html',
#     ISBN='9789861371955'
# )


# # 靖妤的爬蟲程式

# ## <mark>完成</mark>webpac_two_cralwer(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/05
# - 『編輯者』：靖妤、仕瑋
# - 『運用的機構』：[國立臺北藝術大學](http://203.64.5.158/webpac/)、[國立勤益科技大學](http://140.128.95.172/webpac/)、[義守大學](http://webpac.isu.edu.tw/webpac/)、[中山醫學大學](http://140.128.138.208/webpac/)

# ### 函式本體

# In[50]:


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


# In[51]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_two_cralwer(
#     driver=driver,
#     org='義守大學',
#     org_url='https://webpac.isu.edu.tw/webpac/',
#     ISBN='9789861371955'
# )


# In[52]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# webpac_two_cralwer(
#     driver=driver,
#     org='國立臺北藝術大學',
#     org_url='http://203.64.5.158/webpac/',
#     ISBN='986729193X'
# )


# ## <mark>完成</mark>台北海洋科技大學(driver, org, org_url, ISBN)
# - 『最後編輯』：2021/08/03
# - 『編輯者』：靖妤
# - 『運用的機構』：[台北海洋科技大學](http://140.129.253.4/webopac7/sim_data2.php?pagerows=15&orderby=BRN&pageno=1&bn=986729193X)

# ### Unable to coerce to Series

# In[53]:


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


# In[54]:


# driver = webdriver.Chrome(options=my_options, desired_capabilities=my_capabilities)
# 台北海洋科技大學(
#     driver=driver,
#     org='台北海洋科技大學',
#     org_url='http://140.129.253.4/webopac7/sim_data2.php?pageno=1&pagerows=15&orderby=BRN&ti=&au=&se=&su=&pr=&mt=&mt2=&yrs=&yre=&nn=&lc=&bn=',
#     ISBN='986729193X'
# )

