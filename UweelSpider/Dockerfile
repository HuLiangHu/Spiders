FROM registry.cn-hangzhou.aliyuncs.com/croton/scrapy


COPY . /home/spiders
WORKDIR /home/spiders

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD python run.py