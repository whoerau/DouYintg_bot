import requests


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


if __name__ == '__main__':
    # get_kuaishou_info('https://v.kuaishou.com/EHyg3o')

    # 测试图文
    get_kuaishou_info('https://v.douyin.com/SF8pAKL/')
