import datetime
import os
import re
import uuid

# import python_socks
# import socks
from telethon import TelegramClient, events

import util
from adapter import douyin
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
    await event.client.send_message(event.chat_id, '向我发送抖音、Tiktok、推特、ins、微博等视频的分享链接,下载无水印视频,有问题请留言  '
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
        elif 'http' in text:
            # 最后尝试用yt_dlp 下载
            await hand_Yt(event, text)


async def hand_Yt(event, text):
    msg1 = await event.client.send_message(event.chat_id,
                                           '正在下载...')

    msg2 = await event.client.send_message(event.chat_id,
                                           '🤞')
    url = re.findall(pattern, text)[0]
    try:
        pat, title = download(url)
        await msg1.delete()
        await msg2.delete()
        msg3 = await event.reply('下载完成，正在上传...')
        # 发送视频
        img_path = pat.replace('mp4', 'jpg')
        msg = await event.client.send_file(event.chat_id,
                                           pat,
                                           supports_streaming=True,
                                           thumb=img_path if os.path.exists(
                                               img_path) else None,
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
        os.remove(pat)

    await msg3.delete()


def callback(current, total):
    print("\r", '正在发送', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total), end="", flush=True)


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
