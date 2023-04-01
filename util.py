import asyncio
import uuid
import aiofiles
import aiohttp
from tenacity import retry, stop_after_attempt, wait_fixed

headers = {
    'accept-language': 'zh-CN,zh;q=0.9',
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}


# 下载视频
@retry(stop=stop_after_attempt(4), wait=wait_fixed(10))
async def run(url, name):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            async with aiofiles.open(name, "wb") as fp:
                while True:
                    chunk = await r.content.read(64 * 1024)
                    if not chunk:
                        break
                    await fp.write(chunk)
                print("\r", '任务文件 ', name, ' 下载成功', end="", flush=True)


async def imgCoverFromFile(input, output):
    # ffmpeg -i 001.jpg -vf 'scale=320:320'  001_1.jpg
    command = ''' ffmpeg -i "%s" -y -vframes 1   "%s" ''' % (
        input, output)
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{command!r} exited with {proc.returncode}]')


async def downImg(session, url, filename, sem):
    async with sem:
        # url = url.replace('-sign', '')
        async with session.get(url, headers=headers) as r:
            if r.status == 403:
                return
            content = await r.content.read()
            async with aiofiles.open(filename, 'wb') as f:
                await f.write(content)
            print("\r", '任务文件 ', filename, ' 下载成功', end="", flush=True)


# 下载图片
async def downImages(urls):
    sem = asyncio.Semaphore(3)  # 控制并发数
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        jpgFiles = []
        # print(urls)
        for url in urls:
            jpgname = str(uuid.uuid4()) + '.jpg'
            jpgFiles.append(jpgname)
            task = asyncio.create_task(downImg(session, url, jpgname, sem))
            tasks.append(task)
        await asyncio.gather(*tasks)
        return jpgFiles
