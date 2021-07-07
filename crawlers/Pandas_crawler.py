# all-in-one
def temp_crawler(org, position, url):
    try:
        # 組合成書的網址
        url = url + ISBN
        # 載入 html，如果發生 HTTPError，那麼就使用 requests.get(url, verify=False)
        try:
            dfs = pd.read_html(url, encoding="utf-8")
        except HTTPError:
            # 設定 verify=False，以解決 SSLError
            resp = requests.get(url, verify=False)
            dfs = pd.read_html(resp.text, encoding="utf-8")
        # 定位表格
        tgt = dfs[position]

#         tgt.insert(0, "連結", [url for i in range(tgt.shape[0])])
        tgt.insert(0, "圖書館", [org for i in range(tgt.shape[0])])
        return tgt
    except:
        print(f"「{url}」無法爬取！")
