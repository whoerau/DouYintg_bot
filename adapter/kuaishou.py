import asyncio

import requests

from utils import util

import re, os

from adapter.dlpanda import RS

from lxml import etree

DLPANDA_DOUYIN_TOKEN = os.getenv('DLPANDA_DOUYIN_TOKEN')


def get_kuaishou_info(url):
    res = requests.get('https://api.cooluc.com/?url=' + url)
    json = res.json()
    if 'video' in json:
        video_url = json['video']
        print(video_url)
        desc = json['desc']
        return video_url, desc
    else:
        images = json['images']
        desc = json['desc']
        print(images)
        return images, desc


def get_kuaishou_info_via_dlpanda(url):
    url = f'https://dlpanda.com/zh-CN/?url={url}&token={DLPANDA_DOUYIN_TOKEN}&token51={DLPANDA_DOUYIN_TOKEN}'
    res = RS.get(url).text

    # desc
    selects = etree.HTML(res)
    desc = ""
    result = selects.xpath("/html/body/main/section[1]/div/div/div[2]/div[5]/div/div/div[2]/div[1]/a/h5")
    if result:
        first_element = result[0]
        desc = first_element.text

    # video
    ccc = [r.span() for r in re.finditer('<source src="', res)]
    ddd = [r.span() for r in re.finditer('" type="video/mp4"', res)]
    video_links = []

    for i in range(len(ccc)):
        link = res[ccc[i][1]:ddd[i][0]].find('https')
        if link == -1:
            links = f'https:{res[ccc[i][1]:ddd[i][0]]}'
        else:
            links = res[ccc[i][1]:ddd[i][0]]

        links = links.replace(';', '&')
        video_links.append(links)

    if len(video_links) == 1:
        print(video_links, desc)
        return video_links[0], desc

    # image
    aaa = [r.span() for r in re.finditer('<img alt="" src="', res)]
    bbb = [r.span() for r in re.finditer('" width="100%"', res)]
    img_links = []

    for i in range(len(aaa)):
        link = res[aaa[i][1]:bbb[i][0]].find('https')
        if link == -1:
            links = f'https:{res[aaa[i][1]:bbb[i][0]]}'
        else:
            links = res[aaa[i][1]:bbb[i][0]]

        links = links.replace(';', '&')
        img_links.append(links)

    print(img_links, desc)
    return img_links, desc


async def main():
    # 测试图文
    video_url, desc = get_kuaishou_info_via_dlpanda('https://v.douyin.com/i2nGuy7U/')
    jpgFiles = await util.downImages(video_url)

    # video_url, desc = get_kuaishou_info_via_dlpanda('https://v.douyin.com/i2nnAGJC')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
