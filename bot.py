import datetime
import os
import re
import uuid

# import python_socks
# import socks
from telethon import TelegramClient, events

import util
from adapter.kuaishou import get_kuaishou_info
from adapter.yt import download

# ======================需要设置====================================================
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
    await event.client.send_message(event.chat_id,
                                    '向我发送抖音、Tiktok、推特、ins、微博等视频的分享链接,下载无水印视频,有问题请留言,将机器人拉入群组, /dl 链接文字 ,可以在群组中使用  '
                                    'Send me sharing links of Douyin, Tiktok, Twitter, ins, Weibo and other videos, download videos without watermarks, please leave a message if you have any questions')


captionTemplate = '''标题: %s
'''

pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')  # 匹配模式


@bot.on(events.NewMessage)
async def echo_all(event):
    text = event.text

    if event.is_private:
        print(str(datetime.datetime.now()) + ':' + text)
        if 'v.douyin' in text:
            await handleDouYin(event, text)
        elif 'kuaishou' in text:
            await handleKuaiShou(event, text)
            return
        elif 'http' in text:
            # 最后尝试用yt_dlp 下载
            await hand_Yt(event, text)
    else:
        if text.startswith('/dl'):
            print(str(datetime.datetime.now()) + ':' + text)
            if 'v.douyin' in text:
                await handleDouYin(event, text)
            elif 'kuaishou' in text:
                await handleKuaiShou(event, text)
                return
            elif 'http' in text:
                # 最后尝试用yt_dlp 下载
                await hand_Yt(event, text)


async def handleKuaiShou(event, text):
    msg1 = await event.client.send_message(event.chat_id,
                                           '正在下载...')

    url = re.findall(pattern, text)[0]

    video_url, desc = get_kuaishou_info(url)

    uuidstr = str(uuid.uuid4())
    filename = uuidstr + '.mp4'

    # 下载视频
    await util.run(video_url, filename)

    await util.imgCoverFromFile(filename, f'{filename}.jpg')
    # 发送视频
    msg = await event.client.send_file(event.chat_id,
                                       filename,
                                       supports_streaming=True,
                                       thumb=f'{filename}.jpg',
                                       caption=captionTemplate % (
                                           desc),
                                       parse_mode='html',
                                       reply_to=event.id,
                                       progress_callback=callback
                                       )
    await bot.forward_messages(CHANNEL_ID, msg)
    if os.path.exists(filename):
        os.remove(filename)
    await msg1.delete()


async def hand_Yt(event, text):
    msg1 = await event.client.send_message(event.chat_id,
                                           '正在下载...')

    url = re.findall(pattern, text)[0]
    try:
        pat, title = download(url)
        await msg1.delete()
        msg3 = await event.reply('下载完成，正在上传...')
        # 发送视频
        img_path = pat.replace('mp4', 'jpg')
        exists_img = os.path.exists(img_path)
        msg = await event.client.send_file(event.chat_id,
                                           pat,
                                           supports_streaming=True,
                                           thumb=img_path if exists_img else None,
                                           caption=title,
                                           reply_to=event.id,
                                           # buttons=buttons,
                                           parse_mode='html',
                                           # progress_callback=callback
                                           )
        await bot.forward_messages(CHANNEL_ID, msg)

    except Exception as ep:
        print(ep)
        await event.reply(ep.msg)
        return
    finally:
        # 清理垃圾文件
        if os.path.exists(pat):
            os.remove(pat)
        if exists_img:
            os.remove(img_path)

    await msg3.delete()


def callback(current, total):
    print("\r", '正在发送', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total), end="", flush=True)


async def handleDouYin(event, text):
    urls = re.findall(pattern,
                      text)
    msg1 = await event.client.send_message(event.chat_id,
                                           '正在下载...')

    video_url, desc = get_kuaishou_info(urls[0])
    if isinstance(video_url, list):
        jpgFiles = await util.downImages(video_url)
        msg = await event.client.send_file(event.chat_id,
                                           jpgFiles,
                                           caption=captionTemplate % (
                                               desc),
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
        await util.run(video_url, filename)
        await util.imgCoverFromFile(filename, f'{filename}.jpg')
        # 发送视频
        msg = await event.client.send_file(event.chat_id,
                                           filename,
                                           supports_streaming=True,
                                           thumb=f'{filename}.jpg',
                                           caption=captionTemplate % (
                                               desc),
                                           parse_mode='html',
                                           reply_to=event.id,
                                           progress_callback=callback
                                           )
        os.remove(filename)
        await bot.forward_messages(CHANNEL_ID, msg)

    await msg1.delete()


#  title:
#  链接：
#  描述：

print('bot启动....')
bot.run_until_disconnected()
