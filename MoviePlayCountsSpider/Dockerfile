FROM registry.cn-hangzhou.aliyuncs.com/croton/scrapy

COPY . /home/spiders
WORKDIR /home/spiders

RUN apk add nodejs
RUN apk add npm

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD python run_spider.py
