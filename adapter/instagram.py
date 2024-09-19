import os
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from adapter.dlpanda import standalone_chrome, chrome_options
from bs4 import BeautifulSoup
from utils import run_log as log

didi = "aHR0cHM6Ly9zbmFwaW5zdGEuYXBwLw=="


def get_ins_info(url):
    driver = webdriver.Remote(
        command_executor=standalone_chrome,
        options=chrome_options
    )
    desc = ""

    try:
        url_decoded = base64.b64decode(didi.encode('utf-8')).decode('utf-8')
        driver.get(url_decoded)
        driver.set_window_size(1920, 973)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "url"))
        )

        driver.find_element(By.ID, "url").click()
        driver.find_element(By.ID, "url").send_keys(url)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-get"))
        )

        driver.find_element(By.CSS_SELECTOR, ".btn-get").click()

        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "media-box"))
        )

        img_links = []
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        boxes = soup.find_all('div', class_='download-bottom')
        for box in boxes:
            a_element = box.find('a')
            if a_element:
                src_value = a_element.get('href')
                img_links.append(src_value)

        if len(img_links) == 1:
            # 获取包含下载链接的 <a> 元素
            download_link_element = boxes[0].find('a', class_='btn download-media flex-center')
            # 获取 <a> 元素中的文本内容
            download_text = download_link_element.text.strip()
            if download_text == "Download Video":
                log.info(f"video: {img_links[0]}, desc: {desc}")
                return img_links[0], desc
        log.info(f"image: {img_links}, desc: {desc}")
        return img_links, desc

    except Exception as e:
        log.error(f"get_ins_info an error occurred: {e}")
        return [], desc

    finally:
        driver.quit()


if __name__ == '__main__':
    url = ""
    get_ins_info(url)
