import datetime
import os
import re
import uuid
import asyncio

# import python_socks
# import socks
from telethon import TelegramClient, events

from adapter.kuaishou import get_kuaishou_info, get_kuaishou_info_via_dlpanda
from adapter.xiaohongshu import get_xiaohongshu_info3
from adapter.instagram import get_ins_info
from adapter.twitter import get_twitter_info
from adapter.yt import download
from utils import run_log as log, util

# ======================需要设置====================================================
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
CHANNEL_GROUP_ID = int(os.getenv('CHANNEL_GROUP_ID'))
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

    log.info(
        f"chat_id: {event.chat_id}, username: {user.username}, first_name: {user.first_name}, last_name: {user.last_name}, access_hash: {user.access_hash}, phone: {user.phone}, status: {user.status}, photo: {user.photo}, {datetime.datetime.now()}:{text}")

    if event.is_private:
        if 'v.douyin' in text or 'tiktok.com' in text:
            await handle_media(event, text, get_kuaishou_info_via_dlpanda)
            return
        elif 'kuaishou' in text:
            await handleKuaiShou(event, text)
            return
        elif 'xhslink' in text or 'xiaohongshu.com' in text:
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
            elif 'xhslink' in text or 'xiaohongshu.com' in text:
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
        log.error("exception hand_Yt", ep)
        await event.reply(str(ep))
        return
    finally:
        # 清理垃圾文件
        if os.path.exists(pat):
            os.remove(pat)
        if exists_img:
            os.remove(img_path)

    await msg3.delete()


async def process_media(event, video_url, desc, extra_with_doc):
    # from telethon.tl.types import InputChannel
    # from telethon.tl.functions.channels import GetFullChannelRequest
    # # 获取频道的实体对象
    # channel_entity = await event.client.get_entity(CHANNEL_ID)
    # # 使用获取到的实体对象创建 InputChannel 对象
    # input_channel = InputChannel(channel_entity.id, channel_entity.access_hash)
    # # 获取频道的完整信息
    # full_channel = await event.client(GetFullChannelRequest(input_channel))
    #
    # # 打印频道信息
    # print("频道信息:", full_channel.to_dict())

    """处理媒体下载和发送"""
    if isinstance(video_url, list):
        if len(video_url) == 0:
            raise ValueError("没有找到视频URL")  # 触发重试
        else:
            jpg_files = []  # 存储小于 10 MB 的文件
            doc_files = []  # 存储大于 10 MB 的文件

            try:
                # 下载图片文件
                downloaded_files = await util.downImages(video_url)
                downloaded_files = [file for file in downloaded_files if os.path.exists(file)]  # 过滤存在的文件
            except Exception as e:
                raise ValueError(f"下载图片时出错: {e}")

            # 文件大小分类
            for file in downloaded_files:
                if os.path.getsize(file) < 10 * 1024 * 1024:
                    jpg_files.append(file)  # 小于 10 MB
                else:
                    doc_files.append(file)

            jpg_msg = None  # 保存发送消息的对象
            doc_msg = None  # 保存发送文档消息的对象
            download_msg = None  # 保存发送下载消息的对象

            # 发送图片文件
            if jpg_files:
                try:
                    jpg_msg = await event.client.send_file(
                        event.chat_id,
                        jpg_files,
                        force_document=False,  # 以图片形式发送
                        caption=captionTemplate % desc,
                        reply_to=event.id,
                        parse_mode='html',
                        progress_callback=callback
                    )
                except Exception as e:
                    raise RuntimeError(f"发送图片时出错: {e}")

            # 发送文档文件
            try:
                if extra_with_doc and downloaded_files:
                    download_msg = await event.client.send_file(
                        event.chat_id,
                        downloaded_files,
                        force_document=True,
                        caption=captionTemplate % desc,
                        reply_to=event.id,
                        parse_mode='html',
                        progress_callback=callback
                    )
                elif doc_files:
                    doc_msg = await event.client.send_file(
                        event.chat_id,
                        doc_files,
                        force_document=True,
                        caption=captionTemplate % desc,
                        reply_to=event.id,
                        parse_mode='html',
                        progress_callback=callback
                    )
            except Exception as e:
                raise RuntimeError(f"发送文档时出错: {e}")

            # 转发到目标频道
            try:
                forwarded_msg = None
                if jpg_msg:
                    # 如果存在jpg_msg消息对象，先转发jpg组
                    forwarded_msg = await bot.forward_messages(CHANNEL_ID, jpg_msg)
                    # 检查forwarded_msg是否为列表
                    if isinstance(forwarded_msg, list):
                        # 取第一个消息进行评论
                        forwarded_msg = forwarded_msg[0]

                if download_msg or doc_msg:
                    await bot.forward_messages(
                        CHANNEL_ID,
                        download_msg if download_msg else doc_msg,  # 直接转发已发送的文档消息，不作为评论
                    )

                # """
                # 目前 bot 无法进行 commit_to, 暂时无法实现作为评论发送到目标频道
                # """
                # if jpg_files and extra_with_doc and downloaded_files:
                #     # 如果存在jpg组，doc_files 和 downloaded_files 作为评论发送到目标频道
                #     await event.client.send_message(
                #         CHANNEL_ID,
                #         captionTemplate % desc,
                #         file=downloaded_files,
                #         force_document=True,
                #         comment_to=forwarded_msg if forwarded_msg else None,  # 评论转发消息
                #         parse_mode='html'
                #     )
                # elif jpg_files and doc_files:
                #     await event.client.send_message(
                #         CHANNEL_ID,
                #         captionTemplate % desc,
                #         file=doc_files,
                #         force_document=True,
                #         comment_to=forwarded_msg if forwarded_msg else None,  # 评论转发消息
                #         parse_mode='html'
                #     )
                # else:
                #     # 如果没有jpg组，直接转发之前发送的doc_files或downloaded_files，不作为评论，直接转发
                #     if download_msg or doc_msg:
                #         await bot.forward_messages(
                #             CHANNEL_ID,
                #             download_msg if download_msg else doc_msg,  # 直接转发已发送的文档消息，不作为评论
                #         )
            except Exception as e:
                raise RuntimeError(f"转发文件时出错: {e}")

            # 删除发送后的文件
            for file in downloaded_files:
                try:
                    os.remove(file)  # 直接删除文件
                except OSError as e:
                    raise RuntimeError(f"删除文件时出错: {e}")

    else:
        uuid_str = str(uuid.uuid4())
        filename = f'{uuid_str}.mp4'

        try:
            # 下载视频
            await util.run(video_url, filename)
            await util.imgCoverFromFile(filename, f'{filename}.jpg')  # 生成封面
        except Exception as e:
            raise RuntimeError(f"下载或生成封面时出错: {e}")

        # 发送视频文件
        try:
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
            forwarded_msg = await bot.forward_messages(CHANNEL_ID, msg)
        except Exception as e:
            raise RuntimeError(f"发送视频时出错: {e}")

        # 删除发送后的文件
        try:
            os.remove(filename)  # 删除视频文件
        except OSError as e:
            raise RuntimeError(f"删除视频文件时出错: {e}")


async def handle_media(event, text, platform_info_function):
    urls = re.findall(pattern, text)
    msg1 = await event.client.send_message(event.chat_id, '正在下载...')

    retry_attempts = 10  # 最大重试次数
    retry_messages = []  # 用于存储重试消息的列表

    for attempt in range(retry_attempts):
        try:
            video_url, desc = platform_info_function(urls[0])
            extra_with_doc = platform_info_function == get_xiaohongshu_info3
            await process_media(event, video_url, desc, extra_with_doc)  # 调用抽象出来的处理函数
            # 下载成功，删除所有重试消息
            for msg in retry_messages:
                await msg.delete()
            break  # 跳出循环
        except ValueError as e:
            log.info(f"第 {attempt + 1} 次尝试失败: {e}")
            if attempt < retry_attempts - 1:
                retry_msg = await event.client.send_message(event.chat_id,
                                                            f'解析失败，重试中...（{attempt + 1}/{retry_attempts}）')
                retry_messages.append(retry_msg)  # 将重试消息存储在列表中
                await asyncio.sleep(attempt + 1)  # 等待时间从 1 秒到 5 秒依次递增
            else:
                for msg in retry_messages:
                    await msg.delete()
                await event.reply('解析失败，已重试10次')
        except Exception as e:
            for msg in retry_messages:
                await msg.delete()
            await event.reply(f'下载失败: {e}')
            break

    await msg1.delete()  # 清除“正在下载...”提示


def callback(current, total):
    # print("\r", '正在发送', current, 'out of', total,
    #       'bytes: {:.2%}'.format(current / total), end="", flush=True)
    log.debug('正在发送 %d out of %d bytes: %.2f%%', current, total, (current / total) * 100)


#  title:
#  链接：
#  描述：

log.info('bot启动....')
bot.run_until_disconnected()
