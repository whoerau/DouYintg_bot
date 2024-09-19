import base64
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from adapter.dlpanda import standalone_chrome, chrome_options
from bs4 import BeautifulSoup
from utils import run_log as log

titi = "aHR0cHM6Ly9zc3N0d2l0dGVyLmNvbS8="


def get_twitter_info(url):
    driver = webdriver.Remote(
        command_executor=standalone_chrome,
        options=chrome_options
    )
    desc = ""
    media_link = ""

    try:
        url_decoded = base64.b64decode(titi.encode('utf-8')).decode('utf-8')
        driver.get(url_decoded)
        driver.set_window_size(1920, 973)

        # Wait for the main_page_text element to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "main_page_text")))

        driver.find_element(By.ID, "main_page_text").click()
        driver.find_element(By.ID, "main_page_text").send_keys(url)

        # Wait for the submit button to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit")))

        driver.find_element(By.ID, "submit").click()

        # Wait for the result_overlay to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "result_overlay")))

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        result_overlay = soup.find('div', class_='result_overlay')
        if result_overlay:
            # 查找所有带有 'download_link' 类的 a 标签
            video_links = result_overlay.find_all('a', class_='download_link')

            # 处理每一个 a 标签，解析 href 或 onclick 中的链接
            parsed_links = []
            for link in video_links:
                href = link.get('href')

                if href == "#":
                    # 提取 onclick 中的 URL (假设结构类似 downloadX('url'))
                    onclick = link.get('onclick')
                    match = re.search(r"downloadX\('(.+?)'\)", onclick)
                    if match:
                        parsed_links.append((link, match.group(1)))  # 保留完整的 a 标签和链接
                else:
                    # href 中存在直接的链接
                    parsed_links.append((link, href))

            # 查找最高分辨率的链接
            best_resolution_link = max(
                parsed_links,
                key=lambda item: int(item[0].text.split('x')[1]) if 'x' in item[0].text else 0,
                default=None
            )

            # 如果找到了最高分辨率的链接
            if best_resolution_link:
                link_tag, media_link = best_resolution_link
                best_resolution = int(link_tag.text.split('x')[1])  # 提取分辨率的高度部分
                log.info(f"Best resolution video: {media_link}, resolution: {best_resolution}")
            else:
                log.info("No video link found with a valid resolution")

        else:
            log.info("result overlay not found. Check if the page structure has changed.")

    except Exception as e:
        log.error(f"get_twitter_info an error occurred: {e}")

    finally:
        driver.quit()

    return media_link, desc


if __name__ == '__main__':
    url = "https://x.com/guoguo1039/status/1834829937666122061?s=46"
    # url = "https://x.com/yarays/status/1784089243662553271?s=46"
    get_twitter_info(url)
