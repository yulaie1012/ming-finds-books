# 載入需要的模組
from __future__ import unicode_literals
import os
import time
import json
import math
import flex_template
from flask import Flask, request, abort
#---------------------------------------
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import *
#---------------------------------------
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # 設定 driver 的行為
from selenium.webdriver.support.ui import Select  # 選擇＂下拉式選單＂
from selenium.webdriver.common.keys import Keys  # 鍵盤操作
from selenium.common.exceptions import NoSuchElementException, TimeoutException  # 載入常見錯誤
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # 更改載入策略
from selenium.webdriver.support.ui import WebDriverWait  # 等待機制
from selenium.webdriver.support import expected_conditions as EC  # 預期事件
from selenium.webdriver.common.by import By  # 找尋元素的方法
#---------------------------------------
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
import gspread
import gspread_dataframe as gd
#---------------------------------------
import import_ipynb
import toread
import INSTs
from toread import toread, toread_crawlers, NTC, HWU, NDHU
from INSTs import organize_columns, wait_for_element_present, wait_for_url_changed, accurately_find_table_and_read_it, \
    search_ISBN, click_more_btn, 臺北市立圖書館, TPML, webpac_jsp_crawler, FGU, select_ISBN_strategy, NTOU, \
    easy_crawler, YM, NTNU, NTUST, PCCU, FJU, SINICA, changed_crawler, webpac_ajax_page_crawler, NTPC, KLCCAB, \
    基隆市公共圖書館, webpac_gov_crawler, ILCCB, wait_for_element_clickable, NIU, 國家圖書館, NCL, \
    primo_crawler, NTU

scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
gs = gspread.authorize(creds)
sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
worksheet = sheet.get_worksheet(0)


#----------------用來做縣市對應region字典-----------------
north = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","臺北市", "連江縣"]
center = ["台中市","彰化縣","南投縣","雲林縣","臺中市", "金門縣"]
south = ["嘉義市","台南市","高雄市","屏東縣","臺南市", "澎湖縣"]
east = ["宜蘭縣","花蓮縣","台東縣","臺東縣"]
n_dict = dict.fromkeys(north, ("北","north"))
c_dict = dict.fromkeys(center, ("中","center"))
s_dict = dict.fromkeys(south, ("南","south"))
e_dict = dict.fromkeys(east, ("東","east"))

app = Flask(__name__)

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi('rtut2oGaCBibk5DTObwKuFgQgD8rC7JazGdF9f68BIP/2lXU+bBWjm3JgHQtvh0iHySthUi2We1XPVlGTMCh9s8Q1IZZL58osZBRvyHz8GXOnp4cd959MMyh/bXZkpaqdOepM0vcrSXXZvHSzcolLQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5fecbae22c9e1492decda139bd70fd70')
parser = WebhookParser('5fecbae22c9e1492decda139bd70fd70')

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
def test1(event):
    #----------------取得userid-----------------
    user_id = event.source.user_id
    if user_id == '':
        user_id = event.source.user_id  
    #----------------地區-----------------
    TWregion = ["北部","中部","南部","東部"]
    city_name = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","台中市","彰化縣","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣", "金門縣, 連江縣, 澎湖縣"]
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
    else: 
        worksheet.clear()
        str_input = event.message.text.split(' ')
        ISBN = str_input[0]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit?usp=sharing")
        )

        NTCs = ["ntc", "NTC", "國立臺東專科學校", "臺東專科學校", "東專", "台東專科學校", "國立台東專科學校"]
        HWUs = ["hwu","HWU", "醒吾科技大學", "醒吾科大", "醒吾"]
        TPMLs = ["tpml","TPML", "臺北市立圖書館", "台北市立圖書館", "北市圖"]
        FGUs = ["fgu","FGU", "佛光大學", "佛光", "佛大"]
        NDHUs = ["ndhu","NDHU", "國立東華大學", "東華大學","東華"]
        NTOUs = ["ntou","NTOU", "國立臺灣海洋大學", "國立台灣海洋大學", "海大", "海洋大學"]
        YMs = ["ym","YM", "國立陽明大學","陽明大學", "陽明"]
        NTNUs = ["ntnu","NTNU", "國立臺灣師範大學","國立台灣師範大學","臺灣師範大學","台灣師範大學","台師大","臺師大"]
        NTUSTs = ["ntust","NTUST", "國立臺灣科技大學", "國立台灣科技大學","臺灣科技大學", "台灣科技大學", "台科大","臺科大"]
        PCCUs = ["pccu","PCCU", "中國文化大學", "文化大學","文化", "文大"]
        FJUs = ["fju", "FJU", "輔仁大學", "輔仁", "輔大"]
        SINICAs = ["sinica","SINICA", "中央研究院", "中研院"]
        NTPCs = ["ntpc","NTPC", "新北市立圖書館", "新北市圖","新北市圖書館"]
        KLCCABs = ["klccab","KLCCAB","kllib","KLLIB","基隆市公共圖書館","基隆市圖","基隆市圖書館", "基隆圖書館"]
        ILCCBs = ["ilccb","ILCCB","宜蘭縣公共圖書館","宜蘭縣圖書館","宜蘭圖書館" "宜蘭縣圖","宜圖"]
        NIUs = ["niu","NIU", "國立宜蘭大學", "宜蘭大學", "宜大", "宜蘭大"]
        NCLs = ["ncl","NCL", "國家圖書館", "國圖"]
        NTUs = ["ntu","NTU", "國立臺灣大學", "國立台灣大學", "臺灣大學", "台灣大學", "臺大", "台大"]

        for i in range(1, len(str_input)):
            if str_input[i] in NTCs: # 國立臺東專科學校              
                NTC(ISBN)
            elif str_input[i] in HWUs: # 醒吾科技大學
                HWU(ISBN)    
            elif str_input[i] in TPMLs: # 臺北市立圖書館
                TPML(ISBN)                           
            elif str_input[i] in FGUs: # 佛光大學
                FGU(ISBN) 
            elif str_input[i] in NTOUs: # 國立臺灣海洋大學
                NTOU(ISBN)                 
            elif str_input[i] in YMs: # 國立陽明大學
                YM(ISBN)  
            elif str_input[i] in NTNUs: # 國立臺灣師範大學
                NTNU(ISBN)  
            elif str_input[i] in NTUSTs: # 國立臺灣科技大學
                NTUST(ISBN)
            elif str_input[i] in PCCUs: # 中國文化大學
                PCCU(ISBN)                 
            elif str_input[i] in FJUs: # 輔仁大學
                FJU(ISBN)  
            elif str_input[i] in SINICAs: # 中央研究院
                SINICA(ISBN) 
            elif str_input[i] in NTPCs: # 新北市立圖書館
                NTPC(ISBN) 
            elif str_input[i] in KLCCABs: # 基隆市公共圖書館
                KLCCAB(ISBN)
            elif str_input[i] in ILCCBs: # 宜蘭縣公共圖書館
                ILCCB(ISBN)
            elif str_input[i] in NIUs: # 國立宜蘭大學
                NIU(ISBN)
            elif str_input[i] in NCLs: # 國家圖書館
                NCL(ISBN)
            elif str_input[i] in NTUs: # 國立臺灣大學
                NTU(ISBN)

            else:
                print("nono")
            

    

if __name__ == "__main__":
    app.run(debug=True)