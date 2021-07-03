import pandas as pd

# title = "二十一世紀資本論"
# https://opac.lib.ntnu.edu.tw/search*cht/searchtype=i&search=9789869109321
ISBN = 9789869109321

try:
    url = f"https://opac.lib.ntnu.edu.tw/search*cht/i?SEARCH={ISBN}"
    dfs = pd.read_html(url, encoding="utf-8")
    print(dfs[4])
except:
    print("========================================")
    print("「國立臺灣師範大學」圖書館，讀取失敗")
    print("========================================")

try:
    url = f"https://las.sinica.edu.tw/search*cht/a?searchtype=i&searcharg={ISBN}"
    dfs = pd.read_html(url, encoding="utf-8")
    print(dfs[4])
except:
    print("========================================")
    print("「中央研究院」圖書館，讀取失敗")
    print("========================================")

try:
    url = f"https://opac.lib.ncu.edu.tw/search*cht/i?SEARCH={ISBN}"
    dfs = pd.read_html(url, encoding="utf-8")
    print(dfs[6])
except:
    print("========================================")
    print("「國立中央大學」圖書館，館讀取失敗")
    print("========================================")

try:
    url = f"https://ocean.ntou.edu.tw/search*cht/i?SEARCH={ISBN}"
    dfs = pd.read_html(url, encoding="utf-8")
    print(dfs[0])
except:
    print("========================================")
    print("「國立臺灣海洋大學」圖書館，讀取失敗")
    print("========================================")

try:
    url = f"https://library.ym.edu.tw/search*cht/a?searchtype=i&searcharg={ISBN}"
    dfs = pd.read_html(url, encoding="utf-8")
    print(dfs[4])
except:
    print("========================================")
    print("「國立陽明大學」圖書館，讀取失敗")
    print("========================================")

try:
    url = f"https://webpac.pccu.edu.tw/search*cht/?searchtype=i&searcharg={ISBN}"
    dfs = pd.read_html(url, encoding="utf-8")
    print(dfs[7])
except:
    print("========================================")
    print("「中國文化大學」圖書館，讀取失敗")
    print("========================================")

try:
    url = f"https://library.lib.fju.edu.tw/search~S0*cht/?searchtype=i&searcharg={ISBN}"
    dfs = pd.read_html(url, encoding="utf-8")
    print(dfs[7])
except:
    print("========================================")
    print("「輔仁大學」圖書館，讀取失敗")
    print("========================================")

try:
    url = f"https://cylis.lib.cycu.edu.tw/search*cht/~?searchtype=i&searcharg={ISBN}"
    dfs = pd.read_html(url, encoding="utf-8")
    print(dfs[6])
except:
    print("========================================")
    print("「中原大學」圖書館，讀取失敗")
    print("========================================")

try:
    url = f"https://sierra.lib.ntust.edu.tw/search*cht/i?SEARCH={ISBN}"
    dfs = pd.read_html(url, encoding="utf-8")
    print(dfs[6])
except:
    print("========================================")
    print("「國立臺灣科技大學」圖書館，讀取失敗")
    print("========================================")
