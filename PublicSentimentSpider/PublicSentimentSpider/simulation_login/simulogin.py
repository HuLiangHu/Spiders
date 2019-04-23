import requests
from scrapy.selector import Selector
from .yuncaptcha import loginin
import logging  # 引入logging模块
logging.basicConfig(level=logging.NOTSET)  # 设置日志级别
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Referer':'https://accounts.douban.com/login?alias=&redir=https%3A%2F%2Fwww.douban.com%2F&source=index_nav&error=1001'
}

session = requests.Session()
session.headers.update(headers)

url = 'https://accounts.douban.com/login'


def login(username,password):     #模拟登入函数
    caprcha_id,caprcha_link = get_captcha(url)          #把get_captcha函数返回的值
    if caprcha_id:          #如果有caprcha_id,就执行解析caprcha_link网页信息，并把图片保存下来打开
        img_html = session.get(caprcha_link)
        with open('caprcha.jpg','wb') as f:
            f.write(img_html.content)

        # try:
        #     im = Image.open('caprcha.jpg')
        #     im.show()
        #     im.close()
        # except:
        #     print('打开错误')
        caprcha =input('input caprcha:')
        #caprcha = loginin() #识别验证码
        # print(caprcha)
    data = {                    #需要传去的数据
        'source':'index_nav',
        'redir':'https://www.douban.com',
        'form_email':username,
        'form_password':password,
        'login':'登录',
    }
    if caprcha_id:          #如果需要验证码就把下面的两个数据加入到data里面
        data['captcha-id'] = caprcha_id
        data['captcha-solution'] = caprcha
    html = session.post(url,data=data,headers=headers)
    if 'Huluuu' in html.text:
        logging.info('login success')
        item = {}
        for i in session.cookies:
            item[i.name] = i.value

        return item
    else:
        logging.info('login fail')
        #login(username,password)



def get_captcha(url):       #解析登入界面，获取caprcha_id和caprcha_link
    html = requests.get(url)
    selector =Selector(html)
    caprcha_link = selector.xpath('//img[@id="captcha_image"]/@src').extract_first()
    caprcha_id = selector.xpath('//input[@name="captcha-id"]/@value').extract_first()
    return caprcha_id,caprcha_link




