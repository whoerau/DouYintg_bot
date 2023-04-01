import asyncio

import requests

import util


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

async def main():
    # 测试图文
    video_url, desc =get_kuaishou_info('https://v.douyin.com/AfbBBc1/')
    jpgFiles = await util.downImages(video_url)

if __name__ == '__main__':
    # get_kuaishou_info('https://v.kuaishou.com/EHyg3o')
    asyncio.get_event_loop().run_until_complete(main())


