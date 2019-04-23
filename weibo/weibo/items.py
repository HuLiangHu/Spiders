#-*- coding: utf-8 -*-

from scrapy.item import Item, Field


class Retweetmap(Item):
    uid = Field()
    profile_image_url=Field()
    screen_name = Field()
    statusid = Field()
    sourceid = Field()
    task_statusid = Field()
    def to_dict(self):
        d = {}
        for k, v in self.items(): 
            d[k] = v 
        return d

class WeiboItem(Item):
    created_at = Field()
    #created_at_obj = Field()
    id = Field() # 16位微博ID
    mid = Field() # 16位微博ID 
    idstr = Field() # 字符串型的微博ID
    text = Field()
    task_keys = Field()
    #####
    #sentiments = Field()
    #sentiments_text = Field()
    clear_text = Field() 
    #words_list = Field() 
    #####
    profile_url = Field()
    source = Field()
    url = Field()
    #favorited = Field()
    #truncated = Field()
    #in_reply_to_status_id = Field()
    #in_reply_to_user_id = Field()
    #in_reply_to_screen_name = Field()
    
    #thumbnail_pic = Field()
    #bmiddle_pic = Field()
    #original_pic = Field() 
    #geo = Field()
    #user = Field()  # just uid
    user_id = Field()
    user_name = Field()
    #retweeted_status = Field() # just mid
    pid = Field()
    reposts_count = Field()
    comments_count = Field()
    attitudes_count = Field()
    '''
    mlevel = Field()
    visible = Field()
    ad = Field() # 微博流内的推广微博ID
    #  预留字段，不写入数据
    urls = Field()
    hashtags = Field()
    emotions = Field()
    at_users = Field()
    repost_users = Field()
    '''
    #
    reposts = Field()  # just mids
    comments = Field()  # just ids
    # user_timeline_v2  
    
    # 自定义字段
    first_in = Field()
    last_modify = Field()
    timestamp = Field() # created_at字段转化而来的时间戳

    pic_urls = Field() # 微博配图地址。多图时返回多图链接。无配图返回“[]”
    RESP_ITER_KEYS = ['created_at', 'id', 'mid', 'text', 'source', 'favorited', 'truncated', 
                      'in_reply_to_status_id', 'in_reply_to_user_id', 'in_reply_to_screen_name', 
                      'pic_urls', 'thumbnail_pic', 'geo']

    PIPED_UPDATE_KEYS = ['favorited', 'truncated','pid','reposts_count','comments_count','attitudes_count']

    def __init__(self):
        super(WeiboItem, self).__init__()
        default_empty_arr_keys = ['reposts', 'comments']
        for key in default_empty_arr_keys:
            self.setdefault(key, [])

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (UserItem, WeiboItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v

        return d

class CommentItem(Item):
    created_at = Field()
    created_at_obj = Field()
    id = Field() # 16位微博ID
    mid = Field() # 16位微博ID 
    idstr = Field() # 字符串型的微博ID
    text = Field() 
    #####
    sentiments = Field()
    sentiments_text = Field()  
    #####
    source = Field() 
    
    user = Field()  # just uid  

    # user_timeline_v2  
    reply_comment = Field()
    status = Field()
    # 自定义字段
    first_in = Field()
    last_modify = Field()
    timestamp = Field() # created_at字段转化而来的时间戳

    pic_urls = Field() # 微博配图地址。多图时返回多图链接。无配图返回“[]”
    

    def __init__(self):
        super(CommentItem, self).__init__()  

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (UserItem, WeiboItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v

        return d


class HotTopicItem(Item):
    rank = Field()
    created_at = Field()
    title = Field() 
    desc = Field() # 16位微博ID 
    readcount = Field() # 字符串型的微博ID
    readcount_fixed = Field() # 字符串型的微博ID
    host = Field()  
    rankdate = Field() 

    def __init__(self):
        super(HotTopicItem, self).__init__()  

    def to_dict(self):
        d = {}
        for k, v in self.items(): 
            d[k] = v 
        return d

class UserItem(Item):
    created_at = Field()
    timestamp = Field() # created_at字段转化而来的时间戳
    id = Field() # 用户UID
    page_id = Field() # page id 
    name = Field()
    gender = Field()
    province = Field()
    city = Field()
    birthday = Field()
    customerurl = Field()
    hobby = Field() #兴趣
    tags = Field()
    location = Field()
    description = Field()
    url = Field() # 用户博客地址
    domain = Field() # 用户个性化URL
    geo_enabled = Field() # 是否允许标识用户的地理位置
    verified = Field() # 加V标示，是否微博认证用户
    verified_type = Field() # 用户认证类型
    followers_count = Field()  # 粉丝数
    statuses_count = Field() # 微博数
    friends_count = Field()  # 关注数
    favourites_count = Field() # 收藏数
    profile_image_url = Field()
    allow_all_act_msg = Field()
    # user_timeline_v2
    idstr = Field() # 字符串型的用户UID
    profile_url = Field() # 用户的微博统一URL地址      
    weihao = Field() # 用户的微号
    verified_reason = Field() # 认证原因
    allow_all_comment = Field() # 是否允许所有人对我的微博进行评论
    online_status = Field() # 用户的在线状态，0：不在线、1：在线
    bi_followers_count = Field()
    lang = Field() # 用户当前的语言版本，zh-cn：简体中文，zh-tw：繁体中文，en：英语
    #
    followers = Field()  # just uids
    friends = Field()  # just uids
    # 自定义字段
    first_in = Field()
    last_modify = Field()

    RESP_ITER_KEYS = ['id', 'name','page_id' ,'gender', 'province', 'city', 'location', 'url', 'domain',
                      'geo_enabled', 'verified', 'verified_type','verified_reason', 'description', 
                      'followers_count', 'statuses_count', 'friends_count', 'favourites_count',
                      'profile_image_url', 'allow_all_act_msg', 'created_at','tags','customerurl','birthday','hobby']

    PIPED_UPDATE_KEYS = ['name', 'gender', 'province', 'city', 'location', 'url', 'domain',
                         'geo_enabled', 'verified', 'verified_type','verified_reason' ,'description',
                         'followers_count', 'statuses_count', 'friends_count', 'favourites_count',
                         'profile_image_url', 'allow_all_act_msg', 'created_at','tags','customerurl','birthday','hobby']

    def __init__(self):
        """
        >>> a = UserItem()
        >>> a
        {'followers': [], 'friends': []}
        >>> a.to_dict()
        {'followers': [], 'friends': []}
        """

        super(UserItem, self).__init__()
        default_empty_arr_keys = ['followers', 'friends']
        for key in default_empty_arr_keys:
            self.setdefault(key, [])

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (UserItem, WeiboItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d



class Relation(Item):
    # 自定义字段
    first_in = Field()
    last_modify = Field() 
    uid = Field()
    friend_uid = Field()

    RESP_ITER_KEYS = [ 'uid','friend_uid']

    PIPED_UPDATE_KEYS =  ['uid','friend_uid']

    def __init__(self):
        """
        >>> a = Relation()
        >>> a 
        """

        super(Relation, self).__init__() 

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v,Relation):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d

class UserId(Item):
    url = Field()
    uid = Field()

class SearchItem(Item):
    id = Field() # 16位微博ID
    mid = Field() # 16位微博ID
    created_at = Field()
    timestamp = Field() # created_at字段转化而来的时间戳
    text = Field()
    source = Field()
    favorited = Field()
    truncated = Field()
    in_reply_to_status_id = Field()
    in_reply_to_user_id = Field()
    in_reply_to_screen_name = Field()
    pic_urls = Field() # thumbnail_pic list
    thumbnail_pic = Field()
    geo = Field()
    user = Field()  # just uid
    retweeted_status = Field() # just mid
    #  预留字段，不写入数据
    urls = Field()
    hashtags = Field()
    emotions = Field()
    at_users = Field()
    repost_users = Field()
    #
    reposts = Field()  # just mids
    comments = Field()  # just ids
    # user_timeline_v2
    idstr = Field() # 字符串型微博ID
    mlevel = Field()
    reposts_count = Field()
    comments_count = Field()
    attitudes_count = Field()
    visible = Field()
    ad = Field() # 微博流内的推广微博ID
    # 自定义字段
    first_in = Field()
    last_modify = Field()

    RESP_ITER_KEYS = ['created_at', 'id', 'mid', 'text', 'source', 'favorited', 'truncated', 
                      'in_reply_to_status_id', 'in_reply_to_user_id', 'in_reply_to_screen_name', 
                      'pic_urls', 'thumbnail_pic', 'geo']

    PIPED_UPDATE_KEYS = ['favorited', 'truncated']

    def __init__(self):
        super(WeiboItem, self).__init__()
        default_empty_arr_keys = ['reposts', 'comments']
        for key in default_empty_arr_keys:
            self.setdefault(key, [])

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (UserItem, WeiboItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v

        return d

class TopicItem(Item):
    topic = Field()
    created_at = Field()
    date = Field() 
    viewed = Field()  #查看
    followed = Field() #关注
    reposted = Field() #转发

    def to_dict(self):
        d = {}
        for k, v in self.items(): 
            d[k] = v 
        return d
    
