FROM registry.cn-hangzhou.aliyuncs.com/croton/scrapy


COPY . /home/spiders
WORKDIR /home/spiders
RUN pip install -r requirements.txt

CMD python run_spiders.py