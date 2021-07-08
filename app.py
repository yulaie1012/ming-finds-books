# 載入需要的模組
from __future__ import unicode_literals
import os
import time
import json
import flex_template
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import *
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


#----------------用來做縣市對應region字典-----------------
north = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","臺北市"]
center = ["台中市","彰化縣","南投縣","雲林縣","臺中市"]
south = ["嘉義市","台南市","高雄市","屏東縣","臺南市"]
east = ["宜蘭縣","花蓮縣","台東縣","臺東縣"]
n_dict = dict.fromkeys(north, ("北","north"))
c_dict = dict.fromkeys(center, ("中","center"))
s_dict = dict.fromkeys(south, ("南","south"))
e_dict = dict.fromkeys(east, ("東","east"))


app = Flask(__name__)

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi('rtut2oGaCBibk5DTObwKuFgQgD8rC7JazGdF9f68BIP/2lXU+bBWjm3JgHQtvh0iHySthUi2We1XPVlGTMCh9s8Q1IZZL58osZBRvyHz8GXOnp4cd959MMyh/bXZkpaqdOepM0vcrSXXZvHSzcolLQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5fecbae22c9e1492decda139bd70fd70')

# 打個招呼 :)
@app.route("/", methods=['GET'])
def hello():
    return "Hi! Wanna find some InTeREsTInG books?"

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


#----------------設定回覆訊息介面-----------------
@handler.add(MessageEvent, message=TextMessage)
def NTNU_crawling(keyevent):
    #----------------取得userid-----------------
    user_id = event.source.user_id
    if user_id == '':
        user_id = event.source.user_id
    
    #----------------地區-----------------
    TWregion = ["北部","中部","南部","東部"]
    city_name = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","台中市","彰化縣","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣"]
    city_name_dic = {**n_dict, **c_dict, **s_dict, **e_dict}
    city_region_dict = dict(zip(["north","center","south","east"], [north,center,south,east]))
    #----------------選擇縣市介面-----------------
    if event.message.text == "選擇縣市":
        flex_message0 = flex_template.main_panel_flex()
        line_bot_api.reply_message(event.reply_token,flex_message0)
    #----------------不同區域的介面設定-----------------
    elif event.message.text in TWregion:
            #讀需要的json資料
        f_region = open('json_files_for_robot/json_for_app.json', encoding="utf8") 
        data_region = json.load(f_region) 

        for i,v in enumerate(TWregion):
            if event.message.text == v:
                flex_message1 = FlexSendMessage(
                               alt_text= v + '的縣市',
                               contents= data_region[i]
                )

                line_bot_api.reply_message(event.reply_token,flex_message1) 

        f_region.close()


    #----------------爬蟲-----------------    
    ISBN = keyevent.message.text
    urltest = "https://libholding.ntut.edu.tw/webpacIndex.jsp"
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver") 
    driver.get(urltest)
    element = driver.find_element_by_id('search_inputS')
    element.send_keys(ISBN)
    select = Select(driver.find_element_by_id('search_field'))
    select.select_by_value("STANDARDNO")
    search_gogogo = driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[1]/div/div/div[1]/div/div[1]/div/form/table/tbody/tr[2]/td/input[3]').click()

    time.sleep(5)
    output = str()
    table = driver.find_element_by_class_name('order')
    trlist = table.find_elements_by_tag_name('tr')
    for row in trlist:
        tdlist = row.find_elements_by_tag_name('td')
        for sth in tdlist:
            output = tdlist[2].text +" "+ tdlist[8].text
            break
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        line_bot_api.reply_message(
            keyevent.reply_token,
            TextSendMessage(text=output)
        )

if __name__ == "__main__":
    app.run(debug=True)