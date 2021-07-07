# 龍華科大
from selenium import webdriver # 先下載 webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

df_lst = []
ISBN = '986729193X'
driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver")
url = "https://webpac.lhu.edu.tw/webpac/search.cfm?m=ss&k0=" + ISBN + "&t0=k&c0=and&s0=0&w=0&si=&list_num=10&current_page=1&mt=&at=&sj=&py=&it=&lr=&lg=&si=1"
driver.get(url)
time.sleep(5)

for i in range(3, 6): #假設最多三個版本
    try:
        edition = driver.find_element_by_xpath('/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div[' + str(i) + ']/div[1]/ul/li[3]/a').click()
        time.sleep(4)
        table = driver.find_element_by_xpath('/html/body/div[4]/div[2]/div[1]/div[2]/div/div[1]/div[3]/div[2]/div/div[1]/table')
        trlist = table.find_elements_by_tag_name('tr')
        for row in trlist:
            tdlist = row.find_elements_by_tag_name('td')
            for sth in tdlist:
                new_row = ["龍華科大", tdlist[1].text, tdlist[2].text, tdlist[3].text, url]
                df_lst.append(new_row)
                break
        backtolist = driver.find_element_by_link_text("回檢索結果").click()
        time.sleep(1)
    except:
        pass
print(df_lst)