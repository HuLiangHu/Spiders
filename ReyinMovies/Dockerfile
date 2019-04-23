FROM registry.cn-hangzhou.aliyuncs.com/croton/scrapy
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

COPY . /home/spiders
WORKDIR /home/spiders

RUN apk add nodejs
RUN apk add npm

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python run.py