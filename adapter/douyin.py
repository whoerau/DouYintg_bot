import asyncio

import aiohttp


class Douyin:
    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66"
        }

    async def get_douyin_info(self, url):
        share_url = url
        async with aiohttp.ClientSession() as session:
            async with session.get(share_url, headers=self.headers) as r:
                url = r.url
                # 请求真实地址
                url = f'https://www.iesdouyin.com/aweme/v1/web/aweme/detail/?aweme_id={url.parts[3]}&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333&words=FXXK_U_ByteDance'
                async with session.get(url, headers=self.headers) as r:
                    json = await r.json()
                    list_ = json['aweme_detail']
                    nickname = list_['author']['nickname']
                    unique_id = list_['author']['unique_id']
                    if unique_id == '':
                        unique_id = list_['author']['short_id']
                    desc = list_['desc']
                    print(nickname, unique_id, desc)
                    # 图片
                    if list_['images'] is not None:
                        list = []
                        for val in list_['images']:
                            list.append(val['url_list'][0])
                        return list, nickname, unique_id, desc
                    else:
                        download_url = list_['video']['play_addr']['url_list'][0].replace('wm', '')
                        # 最后一个参数是视频封面
                        return download_url, nickname, unique_id, desc, \
                            list_['video']['cover']['url_list'][
                                0]


if __name__ == '__main__':
    dou = Douyin()
    asyncio.get_event_loop().run_until_complete(dou.get_douyin_info('https://v.douyin.com/hgGSAep/'))
# asyncio.get_event_loop().run_until_complete(getDouYinInfo('https://v.douyin.com/69KYYQ9/'))
# asyncio.get_event_loop().run_until_complete(getDouYinInfo('https://v.douyin.com/69wuFuu/'))
