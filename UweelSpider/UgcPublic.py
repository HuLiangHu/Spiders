import random

import pymysql
import requests
import json
import os

#图片下载到本地，上传到服务器，拿到服务器返回的链接地址
class Publish(object):

    """
    circleName:圈子名称
    title:文章标题
    content:文章内容
    article_type:文章大类(SHORT_TEXT：短文，LONG_TEXT：长文)
    definite_type:文章具体类型(PICTURE:图片，VIDEO：视频，TEXT：文字，ARTICLE：文章)
    img_url:图片URL
    video_cover:视频封面
    videl_url:视频url
    long_text_cover:长文封面
    long_text_summary:长文摘要
    """
    def __init__(self,wid,userId,uuid,username,
                 circleName,circleId,title,content,article_type,definite_type,
                 img_url=None,video_cover=None,video_url=None,long_text_cover=None,long_text_summary=None):
        self.wid=wid
        self.userId = userId
        self.uuid = uuid
        self.username = username
        self.publishAPI = os.environ.get('publish')  #'http://172.16.1.112:7001/api/in/v1/ugc/publishEdit'
        if self.publishAPI is None:
            self.publishAPI = 'http://172.16.1.112:7001/api/in/v1/ugc/publishEdit'
        self.circleName = circleName
        self.article_type = article_type
        self.circleId = circleId
        self.title = title
        self.content = content
        self.img_url = img_url
        self.video_cover =video_cover
        self.video_url = video_url
        self.definite_type = definite_type
        self.long_text_cover = long_text_cover
        self.long_text_summary = long_text_summary
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.data = {
            "circleInfos": [
                {
                    "circleId": circleId,
                    "circleNmae": self.circleName,
                    "userInCircleLevel": 1
                }
            ],
        "userId": self.userId,
            "uuid": self.uuid,
            "username": self.username,
            "headPortraitUuid": "",
            "userLevel": 1,
            "ugcTypeEnum": self.article_type,
            "definiteUGCTypeEnum": self.definite_type,
            "content": self.content,
            "title": self.title,
            "forward": True,
            "share": True,
            "commentate": True,
            "fabulous": True,
            "startTime": 0,
            "endTime": 0,
            "stick": 0,
            "digest": 0,
            "sourceId": "",
            "sourceType": 0,
            "ugcId": "",
            "ugcEditId": ""
        }

    def publish(self):
        if self.data['ugcTypeEnum'] == 'SHORT_TEXT':
            img_list=[]
            if self.img_url:
                for img_url in self.img_url.split(','):
                    img_list.append(
                        {
                            "type": 1,
                            "fileUuid": img_url
                        }
                    )
                self.data["fileInfoModel"] = img_list

            elif self.video_url:
                self.data["fileInfoModel"] = [
                    {
                        "coverHoto": self.video_cover,
                        "type": 2,
                        "fileUuid": self.video_url
                    }
                ]
        else:
            self.data['overPic']={
                "coverHoto": self.long_text_cover,
                "fileUuid": self.long_text_cover,
                "type": 1 #---1 图片，2 视频 3音频 ，非必须
            }
            self.data['contentSynopsis'] =self.long_text_summary
            self.data['definiteUGCTypeEnum'] ='ARTICLE'

        print(self.data)
        response = requests.post(self.publishAPI, data=json.dumps(self.data), headers=self.headers)
        if json.loads(response.text)['success'] ==True:
            query ='UPDATE uweel_content SET flag=1 WHERE wid={}'.format(info[1])
            cursor.execute(query)
            conn.commit()
if __name__ == '__main__':
    conn = pymysql.connect(
        user='huliang',
        passwd='CIf2kdnvY9E57vW1',
        db='uweel_spider',
        host='192.168.2.10',
        charset="utf8",
        use_unicode=True
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM uweel_content WHERE flag is null")
    infos = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM `uweel_users`")
    userInfos = cursor.fetchall()
    userInfo = random.choice(userInfos)

    """ 
    wid:微博id             1
    circleName:圈子名称     2
    title:文章标题          3
    content:文章内容        4
    article_type:文章大类(SHORT_TEXT：短文，LONG_TEXT：长文)         8
    definite_type:文章具体类型(PICTURE:图片，VIDEO：视频，TEXT：文字，ARTICLE：文章)    9
    img_url:图片URL       5
    video_cover:视频封面   6
    videl_url:视频url     7
    long_text_cover:长文封面  10
    long_text_summary:长文摘要 11
    circleId:12
    """

    """
  circleName,circleId,title,content,article_type,definite_type,
  img_url=None,video_cover=None,video_url=None,long_text_cover=None,long_text_summary=None
    """
    for info in infos:
        circleId =1102
        Publish(userInfo[0],userInfo[1],userInfo[2],
                info[1],info[2],circleId,info[3],info[4],
                info[8],info[9],info[5],info[6],
                info[7],info[10],info[11]
               ).publish()