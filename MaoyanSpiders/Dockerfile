FROM registry.cn-hangzhou.aliyuncs.com/croton/scrapy
 
RUN apt-get update && \
	apt-get install -y  tesseract-ocr libjpeg-dev libfreetype6-dev

# RUN curl https://bootstrap.pypa.io/get-pip.py | python 

WORKDIR /home/spiders
COPY . /home/spiders
RUN pip install -r requirements.txt

#CMD ["sh"]
CMD [ "python", "run.py" ]