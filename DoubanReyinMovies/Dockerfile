FROM registry.cn-hangzhou.aliyuncs.com/croton/scrapy

WORKDIR /home/spiders
COPY . /home/spiders
RUN dpkg-reconfigure -f noninteractive tzdata
RUN pip install -r requirements.txt
#CMD ["sh"]
CMD   python run.py