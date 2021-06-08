import os
from selenium import webdriver

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