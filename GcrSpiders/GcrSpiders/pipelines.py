# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from GcrSpiders.items import MkItem, U17Item, TxdmItem, ZztbItem, ZptbItem, DoubanItem, WeiboItem,KKItem
from datetime import date


class GcrspidersPipeline(object):
    """
    update into mysql
    """
    def __init__(self):
        self.conn = pymysql.connect(
                                    host='',
                                    user='',
                                    password='',
                                    db='',
                                    charset='utf8',
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        """
        save to mysql
        """
        if isinstance(item, MkItem):
            self.cursor.execute("""INSERT INTO `novel_rawdata`.`anime_rawdata`
                                (`title`,
                                `author`,
                                `animeid`,
                                `status`,
                                `click_count`,
                                `comment_count`,
                                `coll_count`,
                                `tags`,
                                `category`,
                                `license_status`,
                                `rating`,
                                `rating_count`,
                                `site`,`ctime`) VALUES 
                                ('%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s','%s');""" % (item['title'],
                                             item['author'],
                                             item['animeid'],
                                             item['status'],
                                             item['click_count'],
                                             item['comment_count'],
                                             item['coll_count'],
                                             item['tags'],
                                             item['category'],
                                             item['license_status'],
                                             item['rating'],
                                             item['rating_count'],
                                             item['site'],str(date.today())))
            self.conn.commit()
        elif isinstance(item, U17Item):
            self.cursor.execute("""INSERT INTO `novel_rawdata`.`anime_rawdata`
                                (`title`,
                                `author`,
                                `animeid`,
                                `status`,
                                `click_count`,
                                `comment_count`,
                                `recomment_count`,
                                `tags`,
                                `category`,
                                `license_status`,
                                `monthtickets`,
                                `coll_count`,
                                `tucao_count`,
                                `site`,`ctime`) VALUES 
                                ('%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s','%s');""" % (item['title'],
                                             item['author'],
                                             item['animeid'],
                                             item['status'],
                                             item['click_count'],
                                             item['comment_count'],
                                             item['recomment_count'],
                                             item['tags'],
                                             item['category'],
                                             item['license_status'],
                                             item['monthtickets'],
                                             item['coll_count'],
                                             item['tucao_count'],
                                             item['site'],str(date.today())))
            self.conn.commit()

        elif isinstance(item, KKItem):
            self.cursor.execute("""INSERT INTO `novel_rawdata`.`anime_rawdata`
                                 (`title`,
                                 `author`,
                                 `animeid`,
                                 `status`,
                                 `click_count`,
                                 `comment_count`,
                                 `likes`,
                                 `tags`,
                                 `category`,
                                 `comics_count`,
                                 `coll_count`,
                                 `renqi`,
                                 `site`,`ctime`) VALUES 
                                 ('%s',
                                 '%s',
                                 '%s',
                                 '%s',
                                 '%s',
                                 '%s',
                                 '%s',
                                 '%s',
                                 '%s',
                                 '%s',
                                 '%s',
                                 '%s',
                                 '%s','%s');""" % (item['title'],
                                                   item['author'],
                                                   item['animeid'],
                                                   item['status'],
                                                   item['click_count'],
                                                   item['comment_count'],
                                                   item['likes'],
                                                   item['tags'],
                                                   item['category'],
                                                   item['comics_count'],
                                                   item['coll_count'],
                                                   item['renqi'],
                                                   item['site'], str(date.today())))
            self.conn.commit()
        elif isinstance(item, TxdmItem):
            self.cursor.execute("""INSERT INTO `novel_rawdata`.`anime_rawdata`
                                (`title`,
                                `author`,
                                `animeid`,
                                `status`,
                                `click_count`,
                                `comment_count`,
                                `tags`,
                                `rating`,
                                `rating_count`,
                                `coll_count`,
                                `tucao_count`,
                                `redtickets`,
                                `blacktickets`,
                                `site`,`ctime`) VALUES 
                                ('%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s',
                                '%s','%s');""" % (item['title'],
                                             item['author'],
                                             item['animeid'],
                                             item['status'],
                                             item['click_count'],
                                             item['comment_count'],
                                             item['tags'],
                                             item['rating'],
                                             item['rating_count'],
                                             item['coll_count'],
                                             item['tucao_count'],
                                             item['redtickets'],
                                             item['blacktickets'],
                                             item['site'],str(date.today())))
            self.conn.commit()
        elif isinstance(item, ZztbItem):
            self.cursor.execute("""UPDATE `novel_rawdata`.`mapping_author`
                                SET `r4_zztb_vip_number`='%s',
                                `r4_zztb_themes_number`='%s',
                                `r4_zztb_reply_number`='%s'
                                WHERE `id`='%s';""" % (item['r4_zztb_vip_number'],
                                                       item['r4_zztb_themes_number'],
                                                       item['r4_zztb_reply_number'],
                                                       item['indexid']))
            self.conn.commit()
        elif isinstance(item, ZptbItem):
            self.cursor.execute("""UPDATE `novel_rawdata`.`third_party_data`
                                SET `r4_zptb_vip_number`='%s', 
                                `r4_zptb_themes_number`='%s',
                                `r4_zptb_reply_number`='%s'
                                WHERE `id`='%s';""" % (item['r4_zptb_vip_number'],
                                                       item['r4_zptb_themes_number'],
                                                       item['r4_zptb_reply_number'],
                                                       item['indexid']))
            self.conn.commit()
        elif isinstance(item, DoubanItem):
            self.cursor.execute("""UPDATE `novel_rawdata`.`third_party_data`
                                SET `r4_db_reviews_number`='%s'
                                WHERE `id`='%s';""" % (item['r4_db_reviews_number'],
                                                       item['indexid']))
            self.conn.commit()
        elif isinstance(item, WeiboItem):
            self.cursor.execute("""UPDATE `novel_rawdata`.`third_party_data`
                                SET `r3_wb_fans_number`='%s'
                                WHERE `id`='%s';""" % (item['r3_wb_fans_number'],
                                                       item['indexid']))
            self.conn.commit()
        else:
            pass
        return item
