from datetime import date, datetime, timedelta

import requests
import pandas as pd

from scrapy.http import TextResponse
from pytrends.request import TrendReq


def get_trends_data(google_username, google_password, kw_list, sd):
    pytrend = TrendReq(
        google_username,
        google_password,
        custom_useragent='LTA')

    pytrend.build_payload(kw_list=kw_list)

    df = pytrend.interest_over_time().reset_index()

    sd = datetime.strptime(sd, '%Y-%m-%d').date()

    while sd.strftime(
            '%Y-%m-%d') not in df['date'].dt.strftime('%Y-%m-%d').values:
        sd = sd - timedelta(1)

    df = df[(df['date'].dt.year == sd.year) & (df['date'].dt.month == sd.month)
            & (df['date'].dt.day == sd.day)]

    df = df.T.reset_index()

    df.columns = ['player', 'google_trend']

    return df


def date_range(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield (start_date + timedelta(n)).strftime('%Y-%m-%d')


def get_data_lists(resp):

    players = []
    nat = []
    ages = []
    trans_prices = []
    positions = []
    prev_clubs = []
    next_clubs = []
    mkt_values = []

    for e in resp.css(".inline-table").xpath("./tr/td"):
        position = e.xpath("text()").extract()
        # print(position)
        if len(position) < 2 and any(x.isupper() for x in position[0]):
            positions.append(position[0])

    for e in resp.css(".items").xpath("./tbody/tr"):
        player = e.css(".spielprofil_tooltip")
        flag = e.css(".flaggenrahmen")
        centered = e.css(".zentriert")
        rechts = e.css(".rechts")
        clubs_css = e.css(".vereinprofil_tooltip")
        price_data = e.css("a")
        player_name = player.xpath("@title").extract()
        cnt = flag.xpath("@title").extract()
        age = centered.xpath("text()").extract()
        value = price_data.xpath("text()").extract()
        mkt_value = rechts.xpath("text()").extract()
        clubs = clubs_css.xpath("text()").extract()
        # print(clubs)

        players.append(player_name[0])
        ages.append(age[0])
        trans_prices.append(value[-1])
        prev_clubs.append(value[1])
        nat.append(cnt[0])
        mkt_values.append(mkt_value[0])
        if len(clubs) > 1:
            next_clubs.append(clubs[1])
        elif clubs[0] != value[1]:
            next_clubs.append(clubs[0])

    return players, nat, ages, positions, prev_clubs, next_clubs, mkt_values, trans_prices


def get_df(players,
           nat,
           ages,
           positions,
           prev_clubs,
           next_clubs,
           mkt_values,
           trans_prices,
           transfer_date):

    player_dict = {}

    for n, player in enumerate(players):
        player_dict[player] = [nat[n], ages[n], positions[n], prev_clubs[n],
                               next_clubs[n], mkt_values[n], trans_prices[n]]

    df = pd.DataFrame(player_dict).T.reset_index()

    df.columns = [
        'player',
        'nationality',
        'age',
        'position',
        'previous_club',
        'next_club',
        'market_value',
        'transfer_value']

    df['transfer_date'] = [transfer_date] * df.shape[0]

    return df


def run_crawler(base_url, ua, start_date, end_date,
                google_username, google_password):

    temp_df = pd.DataFrame()

    dates = date_range(start_date, end_date)

    for d in dates:
        url = '{0}//transfers/transfertagedetail/statistik/top/land_id_zu/0/land_id_ab/0/leihe//datum/{1}/plus/1'.format(
            base_url, d)

        rqst = requests.get(url, headers={"User-Agent": ua})
        resp = TextResponse(url, body=rqst.content)

        players, nat, ages, positions, prev_clubs, next_clubs, mkt_values, trans_prices = get_data_lists(
            resp)

        df = get_df(players,
                    nat,
                    ages,
                    positions,
                    prev_clubs,
                    next_clubs,
                    mkt_values,
                    trans_prices,
                    d)

        trends_df = get_trends_data(google_username, google_password,
                                    players, d)

        df = pd.merge(df, trends_df, how='left', on='player')

        temp_df = pd.concat([temp_df, df])

    return temp_df


base_url = "http://www.transfermarkt.es/"

start_date = date(2017, 2, 19)
end_date = date(2017, 2, 20)

ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"

df = run_crawler(base_url, ua, start_date, end_date,
                 'andre.testing12@gmail.com', 'andretest')

print(df)
