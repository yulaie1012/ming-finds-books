from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import pandas as pd
import requests
from bs4 import BeautifulSoup

ISBN = 9789869109321

driver = webdriver.Chrome()
driver.get("https://webpac.lib.nthu.edu.tw/F/")

select = Select(driver.find_element_by_name("x"))
select.select_by_visible_text(u"ISSN / ISBN")
