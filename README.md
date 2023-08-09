# DouYintg_bot

简单的无水印抖音、Toktik视频图文异步下载电报机器人

2022/12/26 增加 yt_dlp 配合aria2 ,支持更多视频解析（支持的网站：https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md ）

2022/07/09 优化抖音号可点击复制功能、自动转发群组功能

### docker运行

#### 安装 docker

```
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh --mirror Aliyun&&systemctl enable docker&&systemctl start docker

```

#### 安装docker-compose

```yaml
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose &&chmod +x /usr/local/bin/docker-compose
```

### 配置

创建目录 /douyin

```yaml
mkdir /douyin
```

### 编辑docker-compose.yml

```angular2html

API_ID: 2222222222222
API_HASH: 22222
BOT_TOKEN: 5161622943:AAEQwISVYsatw_5UcC6MIs8GtmrlokdYeyY

DLPANDA_XSH_TOKEN: panda_xhs
DLPANDA_DOUYIN_TOKEN: panda_douyin
STAND_ALONE_CHROME: http://192.168.1.1:4444/wd/hub
```

### 启动项目

```yaml
docker-compose up 
```

### 测试

1. 直接发送链接给机器人
2. 拉取机器人到群 /dl 文字链接 ,测试下载



查看日志

```
docker logs -f douyintgbot
```











