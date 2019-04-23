from dateutil import tz,parser
from weibo.items import WeiboStatus,WeiboUser
import logging
import re
def str_to_utc(strDate):
    """Returns date in UTC w/o tzinfo"""
    date = parser.parse(strDate)
    dateobj = date.astimezone(tz.gettz('UTC')).replace(tzinfo=None) if date.tzinfo else date
    return dateobj.isoformat()

def parse_weiboitems(status):
    """Return Weibo and WeiboUser"""
    statusItem = WeiboStatus()
    statusItem['id'] = status['id'] 
    statusItem['text'] = status['text']
    #item['created_at'] = repost['created_at']
    
    statusItem['source'] = re.sub(r'</?\w+[^>]*>','',status['source'])
    statusItem['reposts_count'] = status['reposts_count']
    statusItem['comments_count'] = status['comments_count']
    statusItem['attitudes_count'] = status['attitudes_count']
    statusItem['user_id'] = status['user']['id']
    if('pid' in status):
        statusItem['reposts_status_id'] = status['pid']
    else:
        statusItem['reposts_status_id'] = None 
    statusItem['created_at'] = str_to_utc(status['created_at'])
    statusItem['thumbnail_pic'] = status['thumbnail_pic'] if 'thumbnail_pic' in status else None
    statusItem['bmiddle_pic'] = status['bmiddle_pic'] if 'bmiddle_pic' in status else None
    statusItem['original_pic'] = status['original_pic'] if 'original_pic' in status else None
    statusItem['pic_ids'] = status['pic_ids'] if 'pic_ids' in status else None
    try:
        if 'geo' in status and    status['geo'] is  not None and status['geo']['type']=='Point':
            try:
                statusItem['geo']= ",".join(map(str, status['geo']['coordinates']))
            except:
                logging.error(status['geo'])
    except Exception as e:
        logging.error(e)
    userItem = WeiboUser()
    userItem['id'] = status['user']['id']
    userItem['_sys_collection'] = 'weibo_users'
    userItem['screen_name'] = status['user']['screen_name']
    userItem['profile_url'] = status['user']['profile_url']
    userItem['gender'] = status['user']['gender']
    #userItem['birthday'] = repost['user']['birthday']
    userItem['statuses_count'] = status['user']['statuses_count']
    userItem['friends_count'] = status['user']['friends_count']
    userItem['followers_count'] = status['user']['followers_count']
    userItem['verified'] = status['user']['verified']
    #userItem['vip'] = status['user']['vip']
    #userItem['tags'] = status['user']['tags']
    userItem['avatar_large'] = status['user']['avatar_large']
    userItem['province'] = status['user']['province']
    userItem['city'] = status['user']['city']
    userItem['verified_reason'] = status['user']['verified_reason']
    createdtime = str_to_utc(status['user']['created_at']) 
    userItem['created_at'] = createdtime  
    userItem['address'] = status['user']['location']  
    return statusItem,userItem