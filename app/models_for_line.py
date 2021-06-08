# 處理觸發事件
import os
from app import handler, line_bot_api
from linebot.models import MessageEvent, TextMessage, TextSendMessage



def get_chrome():
    op = webdriver.ChromeOptions()
    op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    op.add_argument("--headless")
    op.add_argument("--disable-dev-shm-usage")
    op.add_argument("--no-sandbox")

    '''
    # avoid detection 好孩子先不要 ^.<
    op.add_argument('--disable-infobars')
    op.add_experimental_option('useAutomationExtension', False)
    op.add_experimental_option("excludeSwitches", ["enable-automation"])
    '''

    return webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=op)

def findbooks(event):
    from selenium import webdriver
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    import time
    
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver")
    driver.get("https://metacat.ntu.edu.tw/") # 更改網址以前往不同網頁

    ISBN = event
    element = driver.find_element_by_name('simpleSearchText')
    element.send_keys(ISBN)
    select = Select(driver.find_element_by_id('simpleType'))
    select.select_by_value("ISBN")

    # 把不要的勾掉
    choose_btn = driver.find_element_by_link_text("機構單位篩選").click()
    time.sleep(1)

    btn_mid = driver.find_element_by_id('library1').click()
    btn_south = driver.find_element_by_id('library2').click()
    btn_east = driver.find_element_by_id('library3').click()

    no_hsc = driver.find_element_by_id('hsc').click() # 新生醫專
    no_tust = driver.find_element_by_id('tust').click() # 大華科大
    no_must = driver.find_element_by_id('must').click() # 明新科大
    no_taitheo = driver.find_element_by_id('taitheo').click() # 台灣神學研究學院
    no_dila = driver.find_element_by_id('dila').click() # 法鼓文理學院
    no_yzu = driver.find_element_by_id('yzu').click() # 元智大學
    no_niu = driver.find_element_by_id('niu').click() # 宜蘭大學
    no_lhu = driver.find_element_by_id('lhu').click() # 龍華科大
    no_oit = driver.find_element_by_id('oit').click() # 亞東技術學院
    no_ntuvvAlma = driver.find_element_by_id('ntuvvAlma').click() # 原住民圖資中心

    save_opt = driver.find_element_by_id("saveOptions").click() # 儲存已選選項
    driver.switch_to_alert().accept() # 點選彈出裡面的確定按鈕
    close = driver.find_element_by_class_name("close").click() # 按叉叉

    search_gogogo = driver.find_element_by_id('simpleSearchButton').click()
    time.sleep(70)

    # 有"顯示更多"就按下去
    more = driver.find_elements_by_name('collapseLink')
    for i in range(len(more)):
        more[i].click()
        time.sleep(1)

    # 每頁顯示 100 項搜尋結果
    try:
        show = Select(driver.find_element_by_name("resultTable_length"))
        show.select_by_value("100")
    except:
        show = None
        

    #爬 Metacat
    if show != None:    
        name = []
        books = driver.find_elements_by_class_name('institution-list')
        for i in range(len(books)):
            name.append(books[i].text)

        URL = []
        www = driver.find_elements_by_class_name('institution-list')
        for i in range(len(www)):
            website = www[i].get_attribute('href')
            if website != None:
                URL.append(website)
            else:
                www[i].click()
                www2 = driver.find_elements_by_class_name('institution-list')
                URL.append(www2[-1].get_attribute('href'))
                ActionChains(driver).move_by_offset(150, 200).click().perform()
                ActionChains(driver).move_by_offset(-150, -200).perform()

        for w in URL:
            web = str(w)
            driver.get(web)
            time.sleep(8)


            if 'ntnu' in web: #師大系統
                trlist = driver.find_elements_by_class_name('bibItemsEntry')
                for row in trlist:
                    tdlist = row.find_elements_by_tag_name('td')
                    result = ('臺灣師範大學', tdlist[0].text, tdlist[3].text, w)
 
    driver.close()
    return(result)

@handler.add(MessageEvent, message=TextMessage)
def out(event):
    line_bot_api.reply_message(
        event.reply_token, 

        TextSendMessage(text=findbooks(event).massage.text)
    )

"""
# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=event.message.text)
    )
      
# Phoebe愛唱歌
@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        pretty_note = '♫♪♬'
        pretty_text = ''
        
        for i in event.message.text:
        
            pretty_text += i
            pretty_text += random.choice(pretty_note)
    
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=pretty_text)
        )
"""        