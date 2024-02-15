import json
from adapter.dlpanda import RS
from bs4 import BeautifulSoup


def get_chigua_info(url):
    video_url = ""
    desc = ""
    try:
        # 打开页面
        response = RS.get(url)

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        div = soup.find('div', class_='dplayer')
        if div:
            data_config = div['data-config']
            config = json.loads(data_config)
            video_url = config.get('video', {}).get('url')

        print("video_url", video_url)
        return video_url, desc

    except Exception as e:
        print(f"get_chigua_info an error occurred: {e}")
        return video_url, desc


if __name__ == '__main__':
    url = ""
    get_chigua_info(url)
