# -*- coding: utf-8 -*-

import re
from ..items import MatchReport
from scrapy import Request
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
# from scrapy.shell import inspect_response  # debugging


class SquawkaSpider(CrawlSpider):
    """ Scrape match reports from squawka.com.

    :param competition_id: Competition ID
    :param season: Start year of season
    """

    name = "squawka"
    allowed_domains = ["squawka.com"]
    start_urls = (
        'http://www.squawka.com/match-results',
    )

    rules = (
        Rule(LinkExtractor(allow='http://www.squawka.com/match-results\?pg=.*')),
        Rule(LinkExtractor(allow='.*squawka\.com\/.*\/matches'), callback='process_match'),
    )

    def __init__(self, *a, **kw):
        super(SquawkaSpider, self).__init__(*a, **kw)
        self.competition_id = kw['competition_id']
        self.season = kw['season']

    def parse_start_url(self, response):
        """ Visit match-results to get some cookies before switching to the competition page.
        :param response: scrapy.Response
        :return: scrapy.Request
        """
        competition_url = 'http://www.squawka.com/match-results?ctl={competition_id}_s{season}'
        url = competition_url.format(competition_id=self.competition_id, season=self.season)
        yield Request(url,
                      cookies={
                          'sqhome_competition': 165,
                          'sqhome_competitionteam': 0,
                          'sqhome_competitionidinfeed': self.competition_id,
                          'sqhome_seasonid': self.season,
                      })

    def process_match(self, response):
        """ Find the game ID and s3 url from respectively the chatroom ID and url.
        :param response: scrapy.Response
        :return: scrapy.Request
        """
        room_id = re.findall("chatClient.roomID.*=.*parseInt\(\'([0-9]*)\'\)", response.body)
        s3_base_url = re.findall("chatClient.centreUrl.*=.*\'(.*)match", response.body)
        if room_id and s3_base_url:
            s3_url = s3_base_url[0] + "dp/ingame/{room_id}".format(room_id=room_id[0])
            yield Request(s3_url, callback=self.process_match_report)

    def process_match_report(self, response):
        """ Process the XML match report.
        :param response: scrapy.Response
        :return: MatchReport
        """
        match_report = MatchReport()
        match_report['url'] = response.url
        match_report['data'] = response.body
        yield match_report
