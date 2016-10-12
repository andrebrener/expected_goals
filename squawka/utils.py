import gc
import os
import re
import glob
import logging
import warnings
import multiprocessing

from functools import partial

import numpy as np
import pandas as pd

from lxml import etree
from dateutil import parser

COMPETITIONS = {
    4: 'World Cup',
    5: 'Champions League',
    6: 'Europa League',
    8: 'English Barclays Premier League',
    9: 'Dutch Eredivisie',
    10: 'Football League Championship',
    21: 'Italian Serie A',
    22: 'German Bundesliga',
    23: 'Spanish La Liga',
    24: 'French Ligue 1',
    98: 'US Major League Soccer',
    114: 'Turkish Super Lig',
    129: 'Russian Premier League',
    199: 'Mexican Liga MX - Apertura',
    214: 'Australian A-League',
    363: 'Brazilian Serie A',
    385: 'Mexican Liga MX - Clausura',
}

ev_xpath1 = '/squawka/data_panel/filters/{filter_type}/time_slice/event'
ev_xpath2 = '/squawka/data_panel/possession/period/time_slice/{filter_type}'
EVENTS = {
    'action_areas': ev_xpath1,
    'all_passes': ev_xpath1,
    'balls_out': ev_xpath1,
    'blocked_events': ev_xpath1,
    'cards': ev_xpath1,
    'clearances': ev_xpath1,
    'corners': ev_xpath1,
    'crosses': ev_xpath1,
    'extra_heat_maps': ev_xpath1,
    'fouls': ev_xpath1,
    'goal_keeping': ev_xpath1,
    'goals_attempts': ev_xpath1,
    'headed_duals': ev_xpath1,
    'interceptions': ev_xpath1,
    'keepersweeper': ev_xpath1,
    'offside': ev_xpath1,
    'oneonones': ev_xpath1,
    'setpieces': ev_xpath1,
    'swap_players': ev_xpath2,
    'tackles': ev_xpath1,
    'takeons': ev_xpath1
}

ALL_STATISTICS = sorted(EVENTS.keys() + ['players', 'teams'])

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class SquawkaReport:
    """Squawka match report object.

    :param path: Path to XML-file to generate match report from.
    """

    def __init__(self, path):
        self.__time_slice_events = EVENTS
        self.path = path
        self.xml = self.read_xml(path)

    # See:
    # https://stackoverflow.com/questions/10967551/how-do-i-dynamically-create-properties-in-python
    def __getattr__(self, name):
        if name in self.__time_slice_events:
            return self._parse_timeslice(name)
        else:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))

    @staticmethod
    def read_xml(path):
        """Read XML file.
        :param path: Path to XML-file.
        :return: XML tree.
        """
        with open(path, 'r') as f:
            data = f.read()
        xml = etree.fromstring(data)
        return xml

    def _parse_timeslice(self, filter_type):
        xpath = EVENTS[filter_type].format(filter_type=filter_type)
        return self._get_elements(xpath)

    def _get_elements(self, xpath):
        elements = self.xml.xpath(xpath)
        if elements:
            return self._parse_elements(elements)
        else:
            return None

    def _parse_elements(self, elements):
        parsed = [dict({c.tag: c.text for c in
                        e.getchildren()}.items() + e.attrib.items())
                  for e in elements]
        return parsed

    @property
    def competition(self):
        return re.findall("/(.*)_\d*.xml", self.path)[0]

    @property
    def filters(self):
        filters_element = self.xml.xpath('/squawka/data_panel/filters')
        if filters_element:
            return [ch.tag for ch in filters_element[0].getchildren()]
        # Some match reports don't have data.
        else:
            return None

    @property
    def kickoff(self):
        date = self.xml.xpath("/squawka/data_panel/game/kickoff/text()")[0]
        return parser.parse(date).strftime('%Y-%m-%d %H:%M:%S %z')

    @property
    def match_id(self):
        return int(re.findall("/.*_(\d+).xml", self.path)[0])

    @property
    def name(self):
        return self.xml.xpath("/squawka/data_panel/game/name/text()")[0]

    @property
    def players(self):
        # TODO: Remove non-player elements
        xpath = '/squawka/data_panel/players/player'
        return self._get_elements(xpath)

    @property
    def teams(self):
        xpath = '/squawka/data_panel/game/team'
        return self._get_elements(xpath)

    @property
    def venue(self):
        return self.xml.xpath("/squawka/data_panel/game/venue/text()")[0]

    @property
    def match_info(self):
        info = ({
            'competition': self.competition,
            'kickoff': self.kickoff,
            'match_id': self.match_id,
            'name': self.name,
            'venue': self.venue,
        })
        for team in self.teams:
            for k in ['id', 'short_name']:
                info['_'.join((team['state'], k))] = team[k]
        return info


def stats_from_file(path, statistic, convert=True):
    """Load data for a statistic from file.

    :param path: Path to file.
    :param statistic: Statistic to load (e.g. 'goals_attempts', 'cards').
    :param convert: Process and clean the data (boolean)
    :return pd.DataFrame with data
    """
    report = SquawkaReport(path)
    return stats_from_report(report, statistic, convert)


def stats_from_report(report, statistic, convert=True):
    """Load data for a statistic from a SquawkaReport object.

    :param report: SquawkaReport object
    :param statistic: Statistic to load (e.g. 'goals_attempts', 'cards').
    :param convert: Process and clean the data (boolean)
    :return pd.DataFrame with data
    """
    stats = pd.DataFrame(getattr(report, statistic))
    stats['competition'] = report.competition
    stats['kickoff'] = report.kickoff
    stats['match_id'] = report.match_id
    if convert:
        return convert_export(stats)
    else:
        return stats


def export_all_stats(
    xml_dir,
    out_dir,
    statistics=ALL_STATISTICS,
    convert=True,
    n_jobs=None,
    sequential=(
        'all_passes',
        'extra_heat_maps')):
    """Export all statistics from all XML-files in a folder to CSV.

    :param xml_dir: Path to folder containing XML-files
    :param out_dir: Path to folder to save output to
    :param statistics: Statistics to export
    :param convert: Process and clean the data (boolean)
    :param n_jobs: Number of processes to use
    :param sequential: Iterable with statistics to process sequentially (for memory-intensive stats)
    """

    xml_paths = glob.glob(os.path.join(xml_dir, '*.xml'))

    if n_jobs is None:
        n_jobs = multiprocessing.cpu_count() - 1

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    pool = multiprocessing.Pool(n_jobs)
    for statistic in statistics:
        if statistic in sequential:
            df = pd.concat((_load_xml(p, statistic)
                            for p in xml_paths), axis=0, ignore_index=True)
        else:
            partial_loader = partial(_load_xml, statistic=statistic)
            df = pd.concat(
                pool.imap(
                    partial_loader,
                    xml_paths),
                axis=0,
                ignore_index=True)
        if convert:
            df = convert_export(df)
        save_path = os.path.join(out_dir, '{}.csv'.format(statistic))
        df.to_csv(save_path, index=False, encoding='utf8')
        # Try to free up memory.
        del df
        gc.collect()
        logger.debug("Exported %s to %s", statistic, save_path)


def _load_xml(path, statistic):
    """Load XML files ignoring etree.XMLSyntaxErrors.

    :param path: Path to file.
    :param statistic: Statistic to load (e.g. 'goals_attempts', 'cards').
    :return: XML tree (or None on etree.XMLSyntaxError).
    """
    try:
        return stats_from_file(path, statistic)
    except etree.XMLSyntaxError:
        msg = "XML error loading {}, skipping it...".format(path)
        warnings.warn(msg, RuntimeWarning)


def convert_export(df):
    """Convert a statistics export.
    :param df: pd.DataFrame with statistics (see e.g. stats_from_file())
    :return: processed pd.DataFrame
    """

    def parse_indicator(s, indicator):
        return s.notnull() & (s == indicator)  # Nulls are interpreted as False

    convert_cols = {
        'id': 'int',
        'match_id': 'int',
        'mins': 'int',
        'minsec': 'int',
        'secs': 'int',
        'team_id': 'int'
    }
    coordinate_cols = [
        'end',
        'loc',
        'middle',
        'start',
    ]
    indicator_cols = {
        'is_own': 'yes',
        'headed': 'true',  # Note: ignores all falses
        'shot': 'true',  # Note: ignores all falses
    }
    # Convert strings to ints.
    for col in df.columns.intersection(convert_cols):
        df[col] = df[col].replace('', -1)
        df.loc[df[col].isnull(), col] = -1
        df[col] = df[col].astype(convert_cols[col])

    # Convert indicator cols.
    for col in df.columns.intersection(indicator_cols):
        df[col] = parse_indicator(df[col], indicator_cols[col])

    # Convert coordinate cols.
    for col in df.columns.intersection(coordinate_cols):
        df[[col + '_x', col + '_y']] = split_coordinates(df[col])
        df.drop(col, axis=1, inplace=True)

    return df


def split_coordinates(s):
    """Split Series containing strings with coordinates into a DataFrame.

    :param s: pd.Series
    :return: pd.DataFrame with columns 'x' and 'y'
    """
    if s.notnull().all():
        concatenated = s
    else:
        concatenated = s.copy()
        concatenated.loc[concatenated.isnull()] = ','
    split = pd.DataFrame(
        concatenated.str.split(',').tolist(), columns=[
            'x', 'y'], dtype=float)
    return split.replace('', np.nan)
