import datetime
import os
import re
import uuid
import asyncio

# import python_socks
# import socks
from telethon import TelegramClient, events

import util
from adapter.kuaishou import get_kuaishou_info, get_kuaishou_info_via_dlpanda
from adapter.xiaohongshu import get_xiaohongshu_info3
from adapter.instagram import get_ins_info
from adapter.twitter import get_twitter_info
from adapter.yt import download

# ======================需要设置====================================================
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
# =========================需要设置=================================================

# 定义授权用户的用户名列表
authorized_users_str = os.getenv('AUTHORIZED_USERS', '')
AUTHORIZED_USERS = list(map(int, authorized_users_str.split(','))) if authorized_users_str else []

bot = TelegramClient(None, API_ID, API_HASH,
                     # proxy=(python_socks.ProxyType.HTTP, '127.0.0.1', 10809)
                     ).start(
    bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    if AUTHORIZED_USERS:
        user = await event.get_sender()
        if user.id not in AUTHORIZED_USERS:
            return

    await event.client.send_message(event.chat_id,
                                    '向我发送抖音、Tiktok、推特、ins、微博等视频的分享链接,下载无水印视频,有问题请留言,将机器人拉入群组, /dl 链接文字 ,可以在群组中使用  '
                                    'Send me sharing links of Douyin, Tiktok, Twitter, ins, Weibo and other videos, download videos without watermarks, please leave a message if you have any questions')


captionTemplate = '''标题: %s
'''

pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')  # 匹配模式


@bot.on(events.NewMessage)
async def echo_all(event):
    text = event.text

    # extra check sender
    user = await event.get_sender()
    if AUTHORIZED_USERS:
        if user.id not in AUTHORIZED_USERS:
            return

    print(
        "chat_id:", str(event.chat_id),
        "username:", user.username,
        "first_name:", user.first_name,
        "last_name:", user.last_name,
        "access_hash:", user.access_hash,
        "phone:", user.phone,
        "status:", user.status,
        "photo:", user.photo,
        str(datetime.datetime.now()) + ':' + text
    )

    if event.is_private:
        if 'v.douyin' in text or 'tiktok.com' in text:
            await handle_media(event, text, get_kuaishou_info_via_dlpanda)
            return
        elif 'kuaishou' in text:
            await handleKuaiShou(event, text)
            return
        elif 'xhslink' in text:
            await handle_media(event, text, get_xiaohongshu_info3)
            return
        elif 'instagram' in text:
            await handle_media(event, text, get_ins_info)
            return
        elif "x.com" in text or "twitter.com" in text:
            await handle_media(event, text, get_twitter_info)
            return
        elif 'http' in text:
            # 最后尝试用yt_dlp 下载
            await hand_Yt(event, text)
            return
    else:
        if text.startswith('/dl'):
            if 'v.douyin' in text or 'tiktok.com' in text:
                await handle_media(event, text, get_kuaishou_info_via_dlpanda)
                return
            elif 'kuaishou' in text:
                await handleKuaiShou(event, text)
                return
            elif 'xhslink' in text:
                await handle_media(event, text, get_xiaohongshu_info3)
                return
            elif 'instagram' in text:
                await handle_media(event, text, get_ins_info)
                return
            elif "x.com" in text or "twitter.com" in text:
                await handle_media(event, text, get_twitter_info)
                return
            elif 'http' in text:
                # 最后尝试用yt_dlp 下载
                await hand_Yt(event, text)
                return


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
        print("exception hand_Yt", ep)
        await event.reply(str(ep))
        return
    finally:
        # 清理垃圾文件
        if os.path.exists(pat):
            os.remove(pat)
        if exists_img:
            os.remove(img_path)

    await msg3.delete()


async def process_media(event, video_url, desc):
    """处理媒体下载和发送"""
    if isinstance(video_url, list):
        if len(video_url) == 0:
            raise ValueError("没有找到视频URL")  # 触发重试
        else:
            force_document = False
            jpg_files = await util.downImages(video_url)
            jpg_files = [file for file in jpg_files if os.path.exists(file)]  # 过滤存在的文件
            for jpg_file in jpg_files:
                if os.path.getsize(jpg_file) > 10 * 1024 * 1024:
                    force_document = True
                    break

            msg = await event.client.send_file(
                event.chat_id,
                jpg_files,
                force_document=force_document,
                caption=captionTemplate % desc,
                reply_to=event.id,
                parse_mode='html',
                progress_callback=callback
            )
            await bot.forward_messages(CHANNEL_ID, msg)

            for jpg_file in jpg_files:
                os.remove(jpg_file)
    else:
        uuid_str = str(uuid.uuid4())
        filename = uuid_str + '.mp4'
        await util.run(video_url, filename)
        await util.imgCoverFromFile(filename, f'{filename}.jpg')
        msg = await event.client.send_file(
            event.chat_id,
            filename,
            supports_streaming=True,
            thumb=f'{filename}.jpg',
            caption=captionTemplate % desc,
            parse_mode='html',
            reply_to=event.id,
            progress_callback=callback
        )
        os.remove(filename)
        await bot.forward_messages(CHANNEL_ID, msg)


async def handle_media(event, text, platform_info_function):
    urls = re.findall(pattern, text)
    msg1 = await event.client.send_message(event.chat_id, '正在下载...')

    retry_attempts = 3  # 最大重试次数
    for attempt in range(retry_attempts):
        try:
            video_url, desc = platform_info_function(urls[0])
            await process_media(event, video_url, desc)  # 调用抽象出来的处理函数
            break  # 下载成功，跳出循环
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {e}")
            if attempt < retry_attempts - 1:
                await event.client.send_message(event.chat_id, f'下载失败，重试中...（{attempt + 1}/{retry_attempts}）')
                await asyncio.sleep(2)  # 等待2秒后重试
            else:
                await event.reply('下载失败，已重试3次。')

    await msg1.delete()  # 清除“正在下载...”提示


def callback(current, total):
    print("\r", '正在发送', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total), end="", flush=True)


#  title:
#  链接：
#  描述：

print('bot启动....')
bot.run_until_disconnected()
