import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from adapter.dlpanda import standalone_chrome, chrome_options
from bs4 import BeautifulSoup

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
            video_links = result_overlay.find_all('a', class_='dl-button')
            # filter href is None
            video_links = [link for link in video_links if link.get('href') is not None]
            best_resolution_link = max(
                video_links,
                key=lambda link: int(link.text.split('x')[1]),
                default=None
            )

            if best_resolution_link:
                media_link = best_resolution_link['href']
                best_resolution = int(best_resolution_link.text.split('x')[1])
                print("best_resolution video :", media_link, best_resolution)
            else:
                print("No video link found")

            # script = result_overlay.find('script', string=lambda text: text and "hdInfoLink" in text)
            # if script:
            #     media_link = script.string.split('hdInfoLink = "')[1].split('"')[0]
            #     print("media_link", media_link)
            # else:
            #     print("hdInfoLink not found in script content")

        else:
            print("result overlay not found. Check if the page structure has changed.")

    except Exception as e:
        print(f"get_twitter_info an error occurred: {e}")

    finally:
        driver.quit()

    return media_link, desc


if __name__ == '__main__':
    url = "https://x.com/paofumeizhi/status/1794044925094613331?s=46"
    # url = "https://x.com/yarays/status/1784089243662553271?s=46"
    get_twitter_info(url)
