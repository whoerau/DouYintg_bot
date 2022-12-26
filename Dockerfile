#pip install pipreqs
#pipreqs requirements.txt
# docker build -t jwstar/douyintgbot .
FROM python:3.10.7-slim-buster
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install  gcc ffmpeg aria2
COPY . /app
RUN pip3 --no-cache-dir install --user -r /app/requirements.txt
WORKDIR /app
# -u print打印出来
CMD ["python3", "-u", "bot.py"]
