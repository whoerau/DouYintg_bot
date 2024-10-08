from os import path

from yt_dlp import YoutubeDL
from utils import run_log as log

ydl_optssx = {
    'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "geo_bypass": True,
    "nocheckcertificate": True,
    'quiet': True,
    'no_warnings': True,
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-s', '16', '-j', '16', '-k', '1M'],
    'writethumbnail': True,
    'postprocessors': [{
        'format': 'jpg',
        'key': 'FFmpegThumbnailsConvertor',
        'when': 'before_dl'
    }],
    # 'skip_download': True
}


def download(url: str):
    ydl = YoutubeDL(ydl_optssx)

    info = ydl.extract_info(url, download=False)
    # print(info['title'])
    error_code = ydl.download(url)

    log.info(f'一些视频下载失败' if error_code
             else '视频下载完成')

    return path.join("downloads", f"{info['id']}.{info['ext']}"), info['title']


if __name__ == '__main__':

    try:
        pat, title = download('https://cn.pornhub.com/view_video.php?viewkey=651ee30037a36')
        log.info(f"video: {pat}, desc: {title}")
    except Exception as ep:
        log.error(ep)
