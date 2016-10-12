# -*- coding: utf-8 -*-

import scrapy


class MatchReport(scrapy.Item):
    url = scrapy.Field()
    data = scrapy.Field()

    def __repr__(self):
        """only print out attr1 after exiting the Pipeline"""
        return repr({"item-url": self['url']})
