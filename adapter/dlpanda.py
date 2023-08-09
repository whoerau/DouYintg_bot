import requests
import os
from selenium import webdriver

DLPANDA_XHS_TOKEN = os.getenv('DLPANDA_XHS_TOKEN')

RS = requests.Session()
RS.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
})
RS.cookies.update({
    'dl_token': DLPANDA_XHS_TOKEN
})

standalone_chrome = os.getenv('STAND_ALONE_CHROME')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--incognito')