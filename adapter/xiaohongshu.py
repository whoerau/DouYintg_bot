import asyncio

import util

import re

from lxml import etree

from adapter.dlpanda import RS


def get_xiaohongshu_info(url):
    url = f'https://dlpanda.com/zh-CN/xhs?url={url}'
    rsp = RS.get(url)
    res = rsp.text
    print("dlpanda rsp", rsp.status_code)

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


async def main():
    # 测试图文
    image_url = get_xiaohongshu_info('http://xhslink.com/oooooooo')
    # jpgFiles = await util.downImages(image_url)
    #
    # 测试视频
    # video_url, desc = get_xiaohongshu_info('http://xhslink.com/luCsdt')


if __name__ == '__main__':
    # get_kuaishou_info('https://v.kuaishou.com/EHyg3o')
    asyncio.get_event_loop().run_until_complete(main())
