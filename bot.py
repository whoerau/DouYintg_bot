import datetime
import os
import re
import uuid

# import python_socks
# import socks
from telethon import TelegramClient, events, Button

from adapter import douyin
import util
from adapter.scraper import Scraper

# ======================需要设置====================================================
# API_ID = 21153848  # 需要设置
# API_HASH = 'bdcad7af6ab62608af2527b4cee20bcd'  # 需要设置
# BOT_TOKEN = '5913788955:AAEIP7M18RhAhSz2t2kCZDm31CxH19HJQFA'  # 机器人 token @BotFather 获取，需要设置
# CHANNEL_ID = -1001869610242  # 需要转发的频道id,以频道身份发言 并转发给 @get_id_bot 获取
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
# =========================需要设置=================================================


bot = TelegramClient(None, API_ID, API_HASH,
                     # proxy=(python_socks.ProxyType.HTTP, '127.0.0.1', 10809)
                     ).start(
    bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    await event.client.send_message(event.chat_id, '向我发送抖音或者Tiktok的分享链接,下载无水印视频或图片,有问题请留言  '
                                                   'Send me the share link of Douyin or Tiktok, download the video or picture without watermark, please leave a message if you have any questions')


captionTemplate = '''标题: %s
'''

captionTemplateTiktok = '''标题: %s
tiktok昵称: <code>%s</code>
'''

pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')  # 匹配模式


@bot.on(events.NewMessage)
async def echo_all(event):
    text = event.text

    if event.is_private:
        if 'v.douyin' in text:
            print(str(datetime.datetime.now()) + ':' + text)
            await handleDouYin(event, text)
        elif 'tiktok' in text:
            print(str(datetime.datetime.now()) + ':' + text)
            await handTiktok(event, text)


# 进度回调
def callback(current, total):
    print("\r", '正在发送', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total), end="", flush=True)


async def handTiktok(event, text):
    msg1 = await event.client.send_message(event.chat_id,
                                           '正在下载...')

    msg2 = await event.client.send_message(event.chat_id,
                                           '🤞')
    urls = re.findall(pattern, text)
    scraper = Scraper()
    tiktok_id = await scraper.get_tiktok_video_id(urls[0])
    print("正在测试异步获取TikTok视频数据方法...")
    tiktok_date = await scraper.hybrid_parsing(tiktok_id)

    if tiktok_date['status'] == 'success' and tiktok_date['type'] == 'video':
        nwm_video_url = tiktok_date['video_data']['nwm_video_url']
        aweme_id = tiktok_date['aweme_id']
        desc = tiktok_date['desc']
        video_author_nickname = tiktok_date['author']
        print('无水印地址：', nwm_video_url)
        filename = aweme_id + '.mp4'
        await util.run(nwm_video_url, filename)
        # 发送视频
        msg = await event.client.send_file(event.chat_id,
                                           filename,
                                           supports_streaming=True,
                                           # thumb=cover,
                                           caption=captionTemplateTiktok % (desc, video_author_nickname),
                                           reply_to=event.id,
                                           # buttons=buttons,
                                           parse_mode='html',
                                           # progress_callback=callback
                                           )
        await bot.forward_messages(CHANNEL_ID, msg)
        os.remove(filename)
    if tiktok_date.get('status') == 'success' and tiktok_date.get('url_type') == 'album':
        album_list = tiktok_date.get('album_list')
        album_title = tiktok_date.get('album_title')
        jpgFiles = await util.downImages(album_list)
        msg = await event.client.send_file(event.chat_id,
                                           jpgFiles,
                                           caption=album_title,
                                           reply_to=event.id,
                                           # buttons=buttons,
                                           parse_mode='html',
                                           )
        await bot.forward_messages(CHANNEL_ID, msg)
        for jpgFile in jpgFiles:
            os.remove(jpgFile)
    await msg1.delete()
    await msg2.delete()


async def handleDouYin(event, text):
    urls = re.findall(pattern,
                      text)
    msg1 = await event.client.send_message(event.chat_id,
                                           '正在下载...')

    msg2 = await event.client.send_message(event.chat_id,
                                           '🤞')

    do = douyin.Douyin()
    info = await do.get_douyin_info(urls[0])
    if isinstance(info[0], list):
        jpgFiles = await util.downImages(info[0])
        msg = await event.client.send_file(event.chat_id,
                                           jpgFiles,
                                           caption=captionTemplate % (
                                               info[3]),
                                           reply_to=event.id,
                                           parse_mode='html',
                                           progress_callback=callback
                                           )
        await bot.forward_messages(CHANNEL_ID, msg)

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
        msg = await event.client.send_file(event.chat_id,
                                           filename,
                                           supports_streaming=True,
                                           thumb=cover,
                                           caption=captionTemplate % (
                                               info[3]),
                                           parse_mode='html',
                                           reply_to=event.id,
                                           progress_callback=callback
                                           )
        await bot.forward_messages(CHANNEL_ID, msg)
        os.remove(filename)
        os.remove(cover)
    await msg1.delete()
    await msg2.delete()


#  title:
#  链接：
#  描述：

print('bot启动....')
bot.run_until_disconnected()
