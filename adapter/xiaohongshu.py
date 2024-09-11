import asyncio
import re, json
import traceback

from lxml import etree
from adapter.dlpanda import RS
from adapter.dlpanda import FLARESOLVERR, XIAOHONGSHU_API
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from adapter.dlpanda import standalone_chrome, chrome_options
from bs4 import BeautifulSoup


def get_xiaohongshu_via_flare_solver(url):
    flare_solverr = FLARESOLVERR
    payload = json.dumps({
        "cmd": "request.get",
        "url": url,
        "maxTimeout": 60000
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = RS.post(flare_solverr, headers=headers, data=payload)
    print("response from FLARESOLVERR", response.json())
    res = response.json()['solution']['response']

    return res


def get_xiaohongshu_info(url):
    url = f'https://dlpanda.com/zh-CN/xhs?url={url}'
    # rsp = RS.get(url)
    # res = rsp.text
    res = get_xiaohongshu_via_flare_solver(url)

    # desc
    selects = etree.HTML(res)
    desc = ""
    result = selects.xpath("/html/body/main/section[1]/div/div/div[2]/div[4]/div/div/div[2]/div[1]/a/h5")
    if result:
        first_element = result[0]
        desc = first_element.text

    # video
    ccc = [r.span() for r in re.finditer('<source id="video_source" src="', res)]
    ddd = [r.span() for r in re.finditer('" type="video/mp4"', res)]
    video_links = []

    for i in range(len(ccc)):
        link = res[ccc[i][1]:ddd[i][0]].find('https')
        if link == -1:
            links = f'https:{res[ccc[i][1]:ddd[i][0]]}'
        else:
            links = res[ccc[i][1]:ddd[i][0]]
        video_links.append(links)

    if len(video_links) == 1:
        print(video_links, desc)
        return video_links[0], desc

    # image
    '''res 里面包含了网页的全部信息，如果想要获取文案内容，或者是标题内容，请自行提取，此处不做该内容的提取，本文只提取图片内容'''
    aaa = [r.span() for r in re.finditer('<img class="replaceable" alt src="', res)]
    bbb = [r.span() for r in re.finditer('" data-back-src', res)]
    img_links = []

    for i in range(len(aaa)):
        link = res[aaa[i][1]:bbb[i][0]].find('https')
        if link == -1:
            links = f'https:{res[aaa[i][1]:bbb[i][0]]}'
        else:
            links = res[aaa[i][1]:bbb[i][0]]
        img_links.append(links)
    print('desc', desc, 'img_links', img_links)

    return img_links, desc


# def get_xiaohongshu_info2(url):
#     driver = webdriver.Remote(
#         command_executor=standalone_chrome,
#         options=chrome_options
#     )
#     desc = ""
#
#     try:
#         driver.get(url)
#         driver.set_window_size(1920, 973)
#
#         WebDriverWait(driver, 10).until(
#             EC.visibility_of_all_elements_located((By.ID, "noteContainer"))
#         )
#
#         html = driver.page_source
#         # print(html)
#         soup = BeautifulSoup(html, 'html.parser')
#         note_container = soup.find(id='noteContainer')
#
#         # get desc
#         interaction_container = note_container.find(class_='interaction-container')
#         detail_title = interaction_container.find(id='detail-title').text.strip()
#         detail_desc = interaction_container.find(id='detail-desc').text.strip()
#         desc = f"{detail_title}\n{detail_desc}"
#
#         # Extract all image sources within the container
#         image_links = []
#         slider_container = note_container.find(class_='slider-container')
#         if slider_container:
#             image_tags = slider_container.find_all('img')
#             image_links = [img.get('src') for img in image_tags]
#
#         if len(image_links) == 0:
#             video_container = note_container.find(class_='video-player-media media-container')
#             video_tag = video_container.find('video')
#             video_url = video_tag.get('src').lstrip('blob:') if video_tag else None
#
#             image_links.append(video_url)
#
#         print("image:", image_links, "desc:", desc)
#         return image_links, desc
#
#     except Exception as e:
#         print(f"get_ins_info an error occurred: {e}")
#         traceback.print_exc()
#         return [], desc
#
#     finally:
#         driver.quit()


def get_xiaohongshu_info3(url):
    img_links = []
    desc = ""

    server = XIAOHONGSHU_API
    data = {
        "url": url,
        "download": False,
    }
    response = RS.post(server, json=data)
    rsp = response.json()

    data = rsp.get('data')
    if data:
        desc = data.get('作品标题', '')
        media_url = data.get('下载地址', [])
        if data.get('作品类型', '') == '视频':
            print("video:", media_url[0], "desc:", desc)
            return media_url[0], desc
        else:
            img_links = media_url

    print("image:", img_links, "desc:", desc)
    return img_links, desc


async def main():
    # 测试图文
    image_url = get_xiaohongshu_info3('http://xhslink.com/a/UH6PLLyVNMDV')
    # jpgFiles = await util.downImages(image_url)
    #
    # 测试视频
    # video_url, desc = get_xiaohongshu_info('http://xhslink.com/luCsdt')


if __name__ == '__main__':
    # get_kuaishou_info('https://v.kuaishou.com/EHyg3o')
    asyncio.get_event_loop().run_until_complete(main())
