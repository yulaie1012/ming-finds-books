#各大學和超連結版+輸出list+館藏狀態不變版2021.6.7

from selenium import webdriver # 先下載 webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver") 
driver.get("https://metacat.ntu.edu.tw/") # 更改網址以前往不同網頁

ISBN = input()
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
        if 'ntu.primo' in web: #台大系統
            time.sleep(10)
            try:
                back = driver.find_element_by_css_selector(".tab-header .back-button.button-with-icon.zero-margin.md-button.md-primoExplore-theme.md-ink-ripple")
            except:
                back = None
            if back != None:
                back.click()
            time.sleep(5)
            thelist = driver.find_elements_by_class_name("layout-align-space-between-center.layout-row.flex-100")
            for row in thelist:
                plist = row.find_elements_by_tag_name("p")
                where = row.find_elements_by_tag_name("h3")
                i = len(where)
                for sth in plist:
                    a = sth.find_elements_by_tag_name("span")
                    for _ in range(i): 
                        print('台灣大學', where[_].text, a[0].text, a[2].text, w, end = "\n")
                        break
                    break

        elif 'ntnu' in web: #師大系統
            trlist = driver.find_elements_by_class_name('bibItemsEntry')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                print('臺灣師範大學', tdlist[0].text, tdlist[3].text, w, end = "\n")

        elif 'nccu' in web: #政大系統
            time.sleep(5)
            try:
                back = driver.find_element_by_css_selector(".tab-header .back-button.button-with-icon.zero-margin.md-button.md-primoExplore-theme.md-ink-ripple")
            except:
                back = None
            if back != None:
                back.click()
            thelist = driver.find_elements_by_class_name("md-2-line.md-no-proxy._md")
            for row in thelist:
                plist = row.find_elements_by_tag_name("p")
                where = row.find_elements_by_tag_name("h3")
                i = len(where)
                for sth in plist:
                    a = sth.find_elements_by_tag_name("span")
                    for _ in range(i): 
                        print('政治大學', where[_].text, a[0].text, a[2].text, w, end = "\n")
                        break
                    break

        elif 'ntust' in web: #台科大系統
            trlist = driver.find_elements_by_class_name('bibItemsEntry')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                print('臺灣科技大學', tdlist[0].text, tdlist[5].text, w, end = "\n")

        elif 'ym' in web: #陽明系統
            trlist = driver.find_elements_by_class_name('bibItemsEntry')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                print('陽明大學', tdlist[0].text, tdlist[3].text, w, end = "\n")

        elif 'ntou' in web: #海大系統
            trlist = driver.find_elements_by_class_name('bibItemsEntry')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                print('海洋科技大學', tdlist[0].text, tdlist[3].text, w, end = "\n")

        elif 'ntcu' in web: #交大系統
            time.sleep(5)
            try:
                back = driver.find_element_by_css_selector(".tab-header .back-button.button-with-icon.zero-margin.md-button.md-primoExplore-theme.md-ink-ripple")
            except:
                back = None
            if back != None:
                back.click()
            thelist = driver.find_elements_by_class_name("tab-content-header.margin-bottom-small.margin-left-medium.layout-align-space-between-end.layout-row")
            for row in thelist:
                plist = row.find_elements_by_tag_name("p")
                where = row.find_elements_by_tag_name("h4")
                i = len(where)
                for sth in plist:
                    a = sth.find_elements_by_tag_name("span")
                    for _ in range(i): 
                        print('交通大學', where[_].text, a[0].text, a[2].text, w, end = "\n")
                        break
                    break



        elif 'ncu' in web: #中央系統
            trlist = driver.find_elements_by_class_name('bibItemsEntry')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                print('中央大學', tdlist[0].text, tdlist[3].text, w, end = "\n")

        elif 'ncl' in web: #國圖系統
            where = driver.find_element_by_link_text("書在哪裡(請點選)").click()
            time.sleep(2)
            tdlist = driver.find_elements_by_class_name('td1')
            print('國家圖書館', tdlist[1].text, tdlist[6].text, w, end = "\n")  

        elif 'las.sinica' in web: #中研院系統
            trlist = driver.find_elements_by_class_name('bibItemsEntry')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                print('中央研究院',tdlist[0].text, tdlist[2].text, w, end = "\n")

        elif 'ntpu' in web: #北大系統
            table = driver.find_element_by_class_name("book_location")
            trlist = table.find_elements_by_class_name('odd')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                for sth in tdlist:
                    print('台北大學', tdlist[2].text, w, end = "\n")
                    break

        elif '203.64.5.158' in web: #台北藝術大學系統
            where = driver.find_element_by_xpath("/html/body/div/div[1]/div[2]/div/div/div[2]/div[3]/div[1]/div[3]/div/ul/li/div/div[2]/h3/a").click()
            time.sleep(2)
            table = driver.find_element_by_class_name('table.table-bordered')
            trlist = table.find_elements_by_tag_name('tr')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                for sth in tdlist:
                    print('台北藝術大學', tdlist[0].text, tdlist[5].text, w, end = "\n")
                    break

        elif '140.131.94.8' in web: #護理健康大學系統
            table = driver.find_element_by_xpath("/html/body/div[4]/div[1]/form[1]/div[2]/div[1]/ul[3]/li[1]/ul[3]/li[2]/table")
            trlist = table.find_elements_by_tag_name('tr')
            for _ in trlist:
                tdlist = driver.find_elements_by_class_name('holdingslist')
                print('台北護理健康大學', tdlist[3].text, w, end = "\n")
                break

        elif 'ntut' in web: #北科系統
            table = driver.find_element_by_class_name('order')
            trlist = table.find_elements_by_tag_name('tr')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                for sth in tdlist:
                    print('台北科技大學', tdlist[2].text, tdlist[8].text, w, end = "\n")
                    break    

        elif 'ntl' in web: #國台圖系統
            time.sleep(8)
            where = driver.find_element_by_xpath("/html/body/table[8]/tbody/tr[1]/td[2]/a").click()
            time.sleep(10)
            tdlist = driver.find_elements_by_class_name('td1')
            print('國立台灣圖書館', tdlist[8].text, tdlist[9].text, tdlist[15].text, w, end = "\n") 

        elif 'itrilib' in web: #工研院系統
            where = driver.find_element_by_xpath("/html/body/table[8]/tbody/tr[1]/td[2]/a").click()
            time.sleep(2)
            tdlist = driver.find_elements_by_class_name('td1')
            print('工業研究院', tdlist[9].text, tdlist[10].text, tdlist[12].text, w, end = "\n")

        elif 'nhri' in web: #國衛院系統
            where = driver.find_element_by_xpath('/html/body/table[8]/tbody/tr[1]/td[2]/a').click()
            time.sleep(2)
            tdlist = driver.find_elements_by_class_name('td1')
            print('國家衛生研究院', tdlist[6].text, tdlist[7].text, tdlist[13].text, w, end = "\n")

        elif 'webpac.pccu' in web: #中國文化大學系統
            trlist = driver.find_elements_by_class_name('bibItemsEntry')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                print('中國文化大學', tdlist[0].text, tdlist[3].text, w, end = "\n")

        elif 'shu' in web: #世新系統       
            where = driver.find_element_by_link_text("世新圖書館").click()
            table = driver.find_element_by_xpath("/html/body/p[2]/table[1]")
            trlist = table.find_elements_by_tag_name('tr')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                for sth in tdlist:
                    print('世新大學', tdlist[1].text, tdlist[3].text, w, end = "\n")
                    break

        elif 'uco-network' in web: #淡江系統
            time.sleep(5)
            try:
                back = driver.find_element_by_css_selector(".tab-header .back-button.button-with-icon.zero-margin.md-button.md-primoExplore-theme.md-ink-ripple")
            except:
                back = None
            if back != None:
                back.click()
            thelist = driver.find_elements_by_class_name("neutralized-button.layout-full-width.layout-display-flex.md-button.md-ink-ripple.layout-row")
            for row in thelist:
                plist = row.find_elements_by_tag_name("p")
                where = row.find_elements_by_tag_name("h3")
                i = len(where)
                for sth in plist:
                    a = sth.find_elements_by_tag_name("span")
                    for _ in range(i): 
                        print('淡江大學', where[_].text, a[0].text, a[2].text, w, end = "\n")
                        break
                    break

        elif 'fju' in web: #輔仁大學系統
            trlist = driver.find_elements_by_class_name('bibItemsEntry')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                print('輔仁大學', tdlist[0].text, tdlist[3].text, w, end = "\n")

        elif 'mcu' in web: #銘傳系統
            time.sleep(5)
            try:
                back = driver.find_element_by_css_selector(".tab-header .back-button.button-with-icon.zero-margin.md-button.md-primoExplore-theme.md-ink-ripple")
            except:
                back = None
            if back != None:
                back.click()
            thelist = driver.find_elements_by_class_name("md-2-line.md-no-proxy._md")
            for row in thelist[:-2]:
                plist = row.find_elements_by_tag_name("p")
                where = row.find_elements_by_tag_name("h3")
                i = len(where)
                for sth in plist:
                    a = sth.find_elements_by_tag_name("span")
                    for _ in range(1): 
                        print('銘傳大學', where[_].text, a[0].text, w, end = "\n")
                        break
                    break

        elif 'scu' in web: #東吳系統
            time.sleep(5)
            try:
                back = driver.find_element_by_css_selector(".tab-header .back-button.button-with-icon.zero-margin.md-button.md-primoExplore-theme.md-ink-ripple")
            except:
                back = None
            if back != None:
                back.click()
            thelist = driver.find_elements_by_class_name("md-2-line.md-no-proxy._md")
            for row in thelist[:-2]:
                plist = row.find_elements_by_tag_name("p")
                where = row.find_elements_by_tag_name("h3")
                i = len(where)
                for sth in plist:
                    a = sth.find_elements_by_tag_name("span")
                    for _ in range(1): 
                        print('東吳大學', where[_].text, a[0].text, w, end = "\n")
                        break
                    break 

        elif 'cylis' in web: #中原大學系統
            trlist = driver.find_elements_by_class_name('bibItemsEntry')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                print('中原大學', tdlist[0].text, tdlist[3].text, w, end = "\n")

        elif 'tmu' in web: #北醫系統
            table = driver.find_element_by_class_name('order')
            trlist = table.find_elements_by_tag_name('tr')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                for sth in tdlist:
                    print('台北醫學大學', tdlist[2].text, tdlist[5].text, w, end = "\n")
                    break

        elif 'moc' in web: #台博館系統
            where = driver.find_element_by_link_text("書在哪裡 ? (請點我)").click()
            table = driver.find_element_by_xpath("/html/body/table[9]")
            trlist = table.find_elements_by_tag_name('tr')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                for sth in tdlist:
                    print('國立台灣博物館', tdlist[2].text, tdlist[3].text, tdlist[7].text, w, end = "\n")
                    break

        elif 'jinwen' in web: #景文科大系統
            table = driver.find_element_by_class_name('order')
            trlist = table.find_elements_by_tag_name('tr')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                for sth in tdlist:
                    print('景文科技大學', tdlist[2].text, tdlist[5].text, w, end = "\n")
                    break

        elif 'mmc' in web: #馬偕醫護系統
            where = driver.find_element_by_xpath("/html/body/table[8]/tbody/tr[1]/td[2]/span/a[1]").click()
            time.sleep(2)
            tdlist = driver.find_elements_by_class_name('td1')
            print('馬偕醫護管理專科學校', tdlist[7].text, tdlist[12].text, w, end = "\n")

        elif 'tfi' in web: #視聽文化中心系統
            table = driver.find_element_by_xpath("/html/body/div/div[1]/div/div/div/div[2]/div/div[2]/div[3]/div/div[4]")
            trlist = table.find_elements_by_tag_name('tr')
            for row in trlist:
                tdlist = row.find_elements_by_tag_name('td')
                for sth in tdlist:
                    print('國家視聽文化中心', tdlist[1].text, tdlist[4].text, w, end = "\n")
                    break   

driver.close()