# -*- coding: utf-8 -*-

import os
import re

OUTPUT_DIR = 'data'


class MatchReportPipeline(object):

    def process_item(self, item, spider):
        """
        Construct path and save.
        :param item: items.MatchReport
        :param spider: squawka.SquawkaSpider
        :return: items.MatchReport
        """
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        competition = re.findall("s3-irl-(.*)\.squawka\.com", item['url'])
        game_id = re.findall("ingame/(.*)", item['url'])
        file_name = '_'.join((competition[0], game_id[0])) + '.xml'
        item_path = os.sep.join((OUTPUT_DIR, file_name))
        with open(item_path, 'wr') as f:
            f.write(item['data'])
        return item
