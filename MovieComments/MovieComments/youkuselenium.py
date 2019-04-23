# # -*- coding: utf-8 -*-
# # __author__ = hul
# # __date__ = 2018/9/27 下午11:08
# # -*- coding: utf-8 -*-
# # __author__ = hul
# # __date__ = 2018/9/27 下午5:16
#
# import csv
# import selenium
# from lxml import etree
# import json
# from datetime import datetime
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver import ActionChains
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium import webdriver
# import time
#
# from selenium.webdriver.support.wait import WebDriverWait
# chrome_options = webdriver.ChromeOptions()
# # 使用headless无界面浏览器模式
# # chrome_options.add_argument('--headless')
# # chrome_options.add_argument('--disable-gpu')
# # broswer = webdriver.Chrome(chrome_options=chrome_options)
# prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_options.add_experimental_option("prefs", prefs) #禁止加载图片
# broswer =webdriver.Chrome(chrome_options=chrome_options)
# broswer =webdriver.Chrome()
# wait = WebDriverWait(broswer, 10)
#
#
# def get_api(url):
#     broswer.get(url)
#     num = 35 # 第一集
#     parse_info(broswer,num)
#
# def parse_info(broswer,num):
#
#     # target = broswer.find_element_by_xpath('//*[@id="videoCommentlist"]/div[1]/div/ul[1]/li[2]/a')
#     # broswer.execute_script("arguments[0].scrollIntoView();", target)  # 拖动到可见的元素去
#     js = "var q=document.documentElement.scrollTop=10000"
#     broswer.execute_script(js)
#     comments = wait.until(
#                 EC.presence_of_all_elements_located((By.XPATH,
#                                             '//div[@class="comment-text"]'))
#             )
#     comment_times =broswer.find_elements_by_xpath('//span[@class="comment-timestamp"]')
#     authors = broswer.find_elements_by_xpath('//div[@class="comment-user-info"]/a[1]')
#     item = {}
#     for author,comment,comment_time in zip(authors,comments,comment_times):
#         item['author'] = author.text
#         item['comment'] =comment.text
#         item['comment_time'] =comment_time.text
#         item['ctime'] = str(datetime.now())
#         item['title'] = str('第'+str(num)+'集')
#         #print('*' * 20, '第', num, '集')
#         print(item)
#         save_csv('橙红年代youku-1015.csv',item)
#
#     for i in range(1,4):
#         broswer.execute_script('window.scrollTo(0, document.body.scrollHeight)')
#         ActionChains(broswer).key_down(Keys.DOWN).perform()
#         time.sleep(1)
#         next_page = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="videoCommentlist"]/div[1]/div/ul[1]/li[2]/a')))
#         if next_page:
#             break
#     try:
#         try:
#             next_page = broswer.find_element_by_xpath('//*[@id="videoCommentlist"]/div[4]/div/ul[1]/li[2]/a')
#             parse_next_page(broswer, num, next_page)
#         except:
#             next_page = broswer.find_element_by_xpath('//*[@id="videoCommentlist"]/div[3]/div/ul[1]/li[2]/a')
#             parse_next_page(broswer, num, next_page)
#
#     except Exception as e:
#         print(e,'*'*100)
#         num = num + 1
#         parse_next_video(broswer,num)
#
# def parse_next_page(broswer,num,next_page):
#     # time.sleep(2)
#     try:
#         next_page.click()
#         parse_info(broswer,num)
#
#     except Exception as e:
#         print('点击下一集','&'*100)
#         num = num + 1
#         parse_next_video(broswer,num)
#
# def parse_next_video(broswer,num):
#
#     """
#     点击下一集
#     :param broswer:
#     :return:
#     """
#     js = "var q=document.documentElement.scrollTop=0"
#     broswer.execute_script(js)
#
#     if int(num/30) <= 1:
#         next_video = broswer.find_element_by_xpath('//*[@id="listitem_page1"]/div[{}]/a'.format(num))
#         time.sleep(1)
#         next_video.click()
#         print('*'*20,'第',num,'集')
#         parse_info(broswer,num)
#     elif int(num/30) <= 2:
#
#         broswer.find_element_by_xpath('//*[@id="bpmodule-playpage-anthology"]/div[1]/dt/span[2]').click()#切换集数
#         if num%30 !=0:
#             next_video = broswer.find_element_by_xpath('//*[@id="listitem_page2"]/div[{}]/a'.format(num % 30))
#         else:
#             next_video = broswer.find_element_by_xpath('//*[@id="listitem_page2"]/div[30]/a')
#         next_video.click()
#         print('*' * 20, '第', num, '集')
#         parse_info(broswer, num)
#     else:
#         broswer.find_element_by_xpath('//*[@id="bpmodule-playpage-anthology"]/div[1]/dt/span[3]').click()#切换集数
#         if num%30 !=0:
#             next_video = broswer.find_element_by_xpath('//*[@id="listitem_page2"]/div[{}]/a'.format(num % 30))
#         else:
#             next_video = broswer.find_element_by_xpath('//*[@id="listitem_page2"]/div[30]/a')
#         next_video.click()
#         print('*' * 20, '第', num, '集')
#         parse_info(broswer, num)
#
#
# def save_csv(filename,data):
#     with open(filename, 'a',newline='', errors='ignore',encoding='utf-8') as f:
#         writer =csv.writer(f)
#         writer.writerow(data.values())
#
# if __name__ == '__main__':
#     #第一集链接
#     #url ='https://v.youku.com/v_show/id_XMzgyNzQxNTkxNg==.html?spm=a2h0j.11185381.listitem_page1.5~A&&s=efbfbdefbfbd6813efbf'
#     url ='https://v.youku.com/v_show/id_XMzgyNzQ3OTkzNg==.html?spm=a2h0k.11417342.soresults.dselectbutton&s=5f3577efbfbdefbfbd75'#橙红年代
#     url ='https://v.youku.com/v_show/id_XMzg0OTkyNTA2MA==.html?spm=a2h0j.11185381.listitem_page2.5!5~A&&s=5f3577efbfbdefbfbd75'
#
#     get_api(url)
#
#
