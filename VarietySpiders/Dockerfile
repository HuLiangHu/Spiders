
FROM registry.cn-hangzhou.aliyuncs.com/croton/scrapy

WORKDIR /home/spiders
COPY . /home/spiders
RUN pip install -r requirements.txt
RUN  crontab /home/spiders/crontabfile
#安装rsyslog
RUN apt-get -y install rsyslog

#复制crontabfile到/etc/crontab
RUN cp /home/spiders/crontabfile /etc/crontab
RUN touch /var/log/cron.log

#将run.sh设置为可执行
RUN chmod +x /home/spiders/run.sh
WORKDIR /home/spiders
CMD ["bash","/home/spiders/run.sh"]