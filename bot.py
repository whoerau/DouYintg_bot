import datetime
import os
import re
import uuid
# import socks
from telethon import TelegramClient, events, Button

import douyin
import util
from scraper import Scraper

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = TelegramClient(None, API_ID, API_HASH,
                     # proxy=(socks.HTTP, '127.0.0.1', 10809)
                     ).start(
    bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    await event.client.send_message(event.chat_id, '向我发送抖音或者Tiktok的分享链接,下载无水印视频或图片,有问题请留言  '
                                                   'Send me the share link of Douyin or Tiktok, download the video or picture without watermark, please leave a message if you have any questions')


captionTemplate = '''标题: %s
昵称: %s
抖音号： %s
'''

buttons = [

]

pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')  # 匹配模式


@bot.on(events.NewMessage)
async def echo_all(event):
    text = event.text
    print(str(datetime.datetime.now()) + ':' + text)

    if 'v.douyin' in text:
        await handleDouYin(event, text)
    elif 'tiktok' in text:
        await handTiktok(event, text)
    else:
        await  event.client.send_message(event.chat_id,
                                         '请输入正确的链接')


# 进度回调
def callback(current, total):
    print("\r", '正在发送', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total), end="", flush=True)


async def handTiktok(event, text):
    urls = re.findall(pattern, text)
    scraper = Scraper()
    tiktok_date = await scraper.tiktok(urls[0])
    if tiktok_date.get('status') == 'success' and tiktok_date.get('url_type') == 'video':
        nwm_video_url = tiktok_date.get('nwm_video_url')
        video_aweme_id = tiktok_date.get('video_aweme_id')
        video_title = tiktok_date.get('video_title')
        print('无水印地址：', nwm_video_url)
        filename = video_aweme_id + '.mp4'
        await util.run(nwm_video_url, filename)
        # 发送视频
        await event.client.send_file(event.chat_id,
                                     filename,
                                     supports_streaming=True,
                                     # thumb=cover,
                                     caption=video_title,
                                     reply_to=event.id,
                                     buttons=buttons
                                     # progress_callback=callback
                                     )
        os.remove(filename)
    if tiktok_date.get('status') == 'success' and tiktok_date.get('url_type') == 'album':
        album_list = tiktok_date.get('album_list')
        album_title = tiktok_date.get('album_title')
        jpgFiles = await util.downImages(album_list)
        await event.client.send_file(event.chat_id,
                                     jpgFiles,
                                     caption=album_title,
                                     reply_to=event.id,
                                     buttons=buttons
                                     )

        for jpgFile in jpgFiles:
            os.remove(jpgFile)


async def handleDouYin(event, text):
    urls = re.findall(pattern,
                      text)
    msg1 = await event.client.send_message(event.chat_id,
                                           '正在下载...', buttons=buttons)

    msg2 = await event.client.send_message(event.chat_id,
                                           '🤞')
    info = await douyin.getDouYinInfo(urls[0])
    if isinstance(info[0], list):
        jpgFiles = await util.downImages(info[0])
        await event.client.send_file(event.chat_id,
                                     jpgFiles,
                                     caption=captionTemplate % (
                                         info[3], '#' + info[1], '#' + info[2]),
                                     reply_to=event.id,
                                     progress_callback=callback
                                     )

        for jpgFile in jpgFiles:
            os.remove(jpgFile)

    else:
        uuidstr = str(uuid.uuid4())
        filename = uuidstr + '.mp4'
        cover = uuidstr + '.jpg'
        # 下载视频
        await util.run(info[0], filename)
        # 下载封面
        await util.run(info[4], cover)

        # 发送视频
        await event.client.send_file(event.chat_id,
                                     filename,
                                     supports_streaming=True,
                                     thumb=cover,
                                     caption=captionTemplate % (
                                         info[3], '#' + info[1], '#' + info[2]),
                                     reply_to=event.id,
                                     progress_callback=callback
                                     )
        os.remove(filename)
        os.remove(cover)
    await msg1.delete()
    await msg2.delete()


#  title:
#  链接：
#  描述：

print('bot启动....')
bot.run_until_disconnected()
