# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from hashlib import md5

class VideoSitesPipeline(object):
    def process_item(self, item, spider):
        item['hash'] = self._get_guid(item)
        return item

    def _get_guid(self, item):
        """Generates an unique identifier for a given item."""
        # hash based solely in the url field
        try:
            return md5(item['url']).hexdigest()
        except:
            return md5(item['url'].encode('utf8')).hexdigest()