# -*- coding: utf-8 -*-
# __author__ = hul
import scrapy
from datetime import datetime
import re
from urllib.parse import urlencode
import json
import time

class ZhihutopicSpider(scrapy.Spider):
    name = 'zhihutopic'
    allowed_domains = ['zhihu.com']
    start_urls = 'https://www.zhihu.com/search?'
    topicurl ='https://www.zhihu.com/api/v4/topics/{}/feeds/top_activity?'
    answerurl ='https://www.zhihu.com/api/v4/questions/{}/answers?'

    keyword = '使徒行者'
    headers = {
        #'cookie': '_xsrf=OK42p91ZlwoEStTqRA765pgllzONK2PP; d_c0="ADDmLZZ03g2PTqP4X2Mpav6u9mNwqELlbIs=|1531047029"; _zap=3f991f36-39d1-41ea-8d78-fc5e9ce93da2; l_n_c=1; n_c=1; z_c0=Mi4xbTVNNEFnQUFBQUFBTU9ZdGxuVGVEUmNBQUFCaEFsVk44emg1WEFCSWRzak5iZklQTE0tZm5GY2R6MURXQnQ5dk9n|1535896307|c93e6d53f48712771ec8eab6891c8b909fb7311d; q_c1=6312ce8039604641b06bb12fe180597e|1538895456000|1531047029000; tst=r; tgw_l7_route=931b604f0432b1e60014973b6cd4c7bc; __utma=51854390.1147186281.1540358493.1540358493.1540358493.1; __utmb=51854390.0.10.1540358493; __utmc=51854390; __utmz=51854390.1540358493.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=51854390.100--|2=registration_date=20151025=1^3=entry_date=20151025=1',
        'referer': 'https://www.zhihu.com/topic',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

    def start_requests(self):
        """
        话题搜索页
        :return: 话题链接
        """
        parmas ={
            'q': self.keyword,
            'type': 'topic'
        }
        url = self.start_urls+urlencode(parmas)
        yield scrapy.Request(url,callback=self.parse_link,headers=self.headers)


    def parse_link(self, response):
        topiclink = 'https:'+response.xpath('//div[@class="Popover"]//span[contains(text(),"电影")]/../../../@href').extract_first()
        self.headers['referer'] = topiclink
        yield scrapy.Request(topiclink,headers=self.headers)


    def parse(self, response):
        topicid = re.search('(\d+)',response.url).group(1)
        topic_parmas ={
            'include':'data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.content,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.is_normal,comment_count,voteup_count,content,relevant_info,excerpt.author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=article)].target.content,voteup_count,comment_count,voting,author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=people)].target.answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics;data[?(target.type=answer)].target.annotation_detail,content,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[?(target.type=answer)].target.author.badge[?(type=best_answerer)].topics;data[?(target.type=article)].target.annotation_detail,content,author.badge[?(type=best_answerer)].topics;data[?(target.type=question)].target.annotation_detail,comment_count',
            'offset': '5',
            'limit': '10'
        }
        headers = self.headers
        headers['referer'] = response.url
        url = self.topicurl.format(topicid)+urlencode(topic_parmas)
        yield scrapy.Request(url,meta={'topicid':topicid},callback=self.parse_item,headers=self.headers)


    def parse_item(self, response):
       # topicid =response.meta['topicid']
        #print(json.loads(response.text)['paging']['is_end'])
        #if json.loads(response.text)['paging']['is_end'] != True:
        for info in json.loads(response.text)['data']:
                item={}
                print(info['target']['type'])
                if info['target']['type'] =='article':
                    item['title'] = info['target']['title']
                    item['questionurl'] = info['target']['url']
                    pubtime = info['target']['created']
                    item['pubtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pubtime))
                    content = info['target']['content']
                    item['content'] = re.sub("<[^>]*>", "", content)
                    answer_time = info['target']['created']
                    item['answer_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(answer_time))
                    item['answer_author'] = info['target']['author']['name']
                    item['answer_author_homepageurl'] = info['target']['author']['url']
                    item['answer_author_type'] = info['target']['author']['type']
                    item['answer_url'] = info['target']['url']
                    item['voteup_count'] = info['target']['voteup_count']
                    item['comment_count'] = info['target']['comment_count']
                    item['crawldate'] = str(datetime.now()).split('.')[0]
                    yield item
                elif info['target']['type'] !='article':
                    try:
                        item['title'] = info['target']['question']['title']
                        item['questionurl'] = info['target']['question']['url']
                        pubtime = info['target']['question']['created']
                        item['pubtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pubtime))
                    except:
                        item['title'] = info['target']['title']
                        item['questionurl'] = info['target']['url']
                        pubtime = info['target']['created']
                        item['pubtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pubtime))

                    headers=self.headers
                    headers['referer'] = response.url
                    questionurl = re.sub('http','https',item['questionurl'])
                    yield scrapy.Request(questionurl,meta={'item':item},callback=self.parse_answerurl,headers=headers)

        if json.loads(response.text)['paging']['is_end'] != 'true':
            next_answer_url = json.loads(response.text)['paging']['next']
            if next_answer_url:
                yield scrapy.Request(next_answer_url,callback=self.parse_item,headers=self.headers)

    def parse_answerurl(self, response):
        """
        解析每个topic的URL，获取每个topic的回答url
        :param response:
        :return: 回答url
        """
        item = response.meta['item']
        #print(item['questionurl'])
        try:
            answerid = re.search('http://www.zhihu.com/api/v4/questions/(.*)',item['questionurl']).group(1)

            detail_parmas ={
                'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics',
                'limit': '5',
                'offset':'',
                'sort_by': 'default'
            }
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                'x-ab-param': 'web_logoc=blue;se_major_onebox=major;top_newfollow=0;top_recall_tb_long=51;top_yc=0;top_tffrt=0;top_test_4_liguangyi=1;top_yhgc=0;top_free_content=-1;top_recall_tb=1;top_slot_ad_pos=1;se_refactored_search_index=0;top_sjre=0;top_follow_question_hybrid=0;top_keywordab=0;top_ntr=1;top_uit=0;tp_sft=a;top_recommend_topic_card=0;top_roundtable=1;top_universalebook=1;top_ac_merge=0;top_billread=1;top_feedre=1;top_recall_follow_user=91;pin_efs=orig;se_new_market_search=off;top_ebook=0;se_wiki_box=1;top_billpic=0;top_sj=2;tp_write_pin_guide=3;top_billab=0;top_root=1;top_vd_op=0;se_merger=1;se_minor_onebox=d;se_relevant_query=old;top_cc_at=1;top_gr_topic_reweight=0;top_recall_tb_short=61;zr_ans_rec=gbrank;se_entity=on;top_ad_slot=1;top_retagg=0;top_videos_priority=-1;top_an=0;top_adpar=0;top_manual_tag=2;top_new_user_gift=0;top_feedre_cpt=101;top_multi_model=0;se_consulting_price=n;se_gemini_service=content;top_billboard_count=1;web_ask_flow=exp_a;top_root_few_topic=0;se_daxuechuisou=new;top_nmt=0;top_vd_score_new=0;se_tf=1;top_billupdate1=3;top_pfq=1;top_gif=0;se_ingress=off;top_nucc=3;top_recall_tb_follow=71;top_feedre_itemcf=32;top_tag_isolation=0;top_distinction=0;se_rescore=0;top_root_mg=1;top_vds_alb_pos=0;top_memberfree=1;top_no_weighing=1;top_user_gift=0;top_tagore=1;top_mlt_model=0;top_raf=n;top_alt=0;top_bill=0;top_tr=0;top_video_fix_position=0;top_followtop=1;top_follow_reason=0;top_nuc=0;pin_ef=orig;top_recall=1;se_gi=0;top_card=-1;tp_discussion_feed_card_type=0;top_feedre_rtt=41;top_recall_deep_user=1;top_topic_feedre=21;top_v_album=1;top_hca=0;top_nad=1;ls_play_continuous_order=2;se_auto_syn=0;top_gr_auto_model=0;top_promo=1;top_nszt=0;top_is_gr=0;top_login_card=1;top_ab_validate=2;top_feedtopiccard=0;top_hqt=9;top_gr_model=0;tp_ios_topic_write_pin_guide=1;top_dtmt=2;top_lowup=1;top_billvideo=0;top_fqa=0;top_rank=6;top_spec_promo=1;top_vdio_rew=3;se_dt=1;top_hweb=1;top_root_web=0;top_vd_gender=0;top_newfollowans=0;se_consulting_switch=off;top_recall_core_interest=81;top_retag=0;top_fqai=0;top_keyword=0;top_quality=0;top_30=0;top_f_r_nb=1;top_root_ac=1;top_video_rew=0;ls_new_video=0;se_correct_ab=1;top_nid=0;top_tmt=0;top_video_score=1',
                'x-requested-with': 'fetch'
            }
            headers['referer'] = response.url
            answerurl = self.answerurl.format(answerid)+urlencode(detail_parmas)
            #print(answerurl)
            yield scrapy.Request(answerurl,meta={'item':item},callback=self.parse_answer,headers=headers)
        except:
            pass
    def parse_answer(self, response):
        """
        解析问题的回答
        :param response:
        :return:
        """
        item = response.meta['item']


        for info in json.loads(response.text)['data']:
            content =info['content']
            item['content'] = re.sub("<[^>]*>", "",content)
            answer_time = info['question']['created']
            item['answer_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(answer_time))
            item['answer_author'] =info['author']['name']
            item['answer_author_homepageurl'] = info['author']['url']
            item['answer_author_type'] =info['author']['type']
            item['answer_url'] = info['url']
            item['voteup_count'] = info['voteup_count']
            item['comment_count'] = info['comment_count']
            item['crawldate'] = str(datetime.now()).split('.')[0]

            yield item
        print(json.loads(response.text)['paging']['is_end'])
        if json.loads(response.text)['paging']['is_end'] != True:
            print('=' * 100)
            answernextpage = json.loads(response.text)['paging']['next']
            if answernextpage:
                headers = {
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                    'x-ab-param': 'web_logoc=blue;se_major_onebox=major;top_newfollow=0;top_recall_tb_long=51;top_yc=0;top_tffrt=0;top_test_4_liguangyi=1;top_yhgc=0;top_free_content=-1;top_recall_tb=1;top_slot_ad_pos=1;se_refactored_search_index=0;top_sjre=0;top_follow_question_hybrid=0;top_keywordab=0;top_ntr=1;top_uit=0;tp_sft=a;top_recommend_topic_card=0;top_roundtable=1;top_universalebook=1;top_ac_merge=0;top_billread=1;top_feedre=1;top_recall_follow_user=91;pin_efs=orig;se_new_market_search=off;top_ebook=0;se_wiki_box=1;top_billpic=0;top_sj=2;tp_write_pin_guide=3;top_billab=0;top_root=1;top_vd_op=0;se_merger=1;se_minor_onebox=d;se_relevant_query=old;top_cc_at=1;top_gr_topic_reweight=0;top_recall_tb_short=61;zr_ans_rec=gbrank;se_entity=on;top_ad_slot=1;top_retagg=0;top_videos_priority=-1;top_an=0;top_adpar=0;top_manual_tag=2;top_new_user_gift=0;top_feedre_cpt=101;top_multi_model=0;se_consulting_price=n;se_gemini_service=content;top_billboard_count=1;web_ask_flow=exp_a;top_root_few_topic=0;se_daxuechuisou=new;top_nmt=0;top_vd_score_new=0;se_tf=1;top_billupdate1=3;top_pfq=1;top_gif=0;se_ingress=off;top_nucc=3;top_recall_tb_follow=71;top_feedre_itemcf=32;top_tag_isolation=0;top_distinction=0;se_rescore=0;top_root_mg=1;top_vds_alb_pos=0;top_memberfree=1;top_no_weighing=1;top_user_gift=0;top_tagore=1;top_mlt_model=0;top_raf=n;top_alt=0;top_bill=0;top_tr=0;top_video_fix_position=0;top_followtop=1;top_follow_reason=0;top_nuc=0;pin_ef=orig;top_recall=1;se_gi=0;top_card=-1;tp_discussion_feed_card_type=0;top_feedre_rtt=41;top_recall_deep_user=1;top_topic_feedre=21;top_v_album=1;top_hca=0;top_nad=1;ls_play_continuous_order=2;se_auto_syn=0;top_gr_auto_model=0;top_promo=1;top_nszt=0;top_is_gr=0;top_login_card=1;top_ab_validate=2;top_feedtopiccard=0;top_hqt=9;top_gr_model=0;tp_ios_topic_write_pin_guide=1;top_dtmt=2;top_lowup=1;top_billvideo=0;top_fqa=0;top_rank=6;top_spec_promo=1;top_vdio_rew=3;se_dt=1;top_hweb=1;top_root_web=0;top_vd_gender=0;top_newfollowans=0;se_consulting_switch=off;top_recall_core_interest=81;top_retag=0;top_fqai=0;top_keyword=0;top_quality=0;top_30=0;top_f_r_nb=1;top_root_ac=1;top_video_rew=0;ls_new_video=0;se_correct_ab=1;top_nid=0;top_tmt=0;top_video_score=1',
                    'x-requested-with': 'fetch'
                }
                headers['referer'] = answernextpage
                yield scrapy.Request(answernextpage, meta={'item': item}, callback=self.parse_answer, headers=headers)
