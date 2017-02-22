# =============================================================================
#          File: transfermarkt_crawler.py
#        Author: Andre Brener
#       Created: 18 Feb 2017
# Last Modified: 18 Feb 2017
#   Description: description
# =============================================================================
import requests
import pandas as pd

from scrapy.http import TextResponse

base_url = "http://www.transfermarkt.es/"
url = "{base_url}/premier-league/marktwerte/wettbewerb/GB1/pos//detailpos/0/altersklasse/alle/plus/1".format(
    base_url=base_url)
ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"

rqst = requests.get(url, headers={"User-Agent": ua})
resp = TextResponse(url, body=rqst.content)
players = []
nat = []
ages = []
clubs = []
mkt_values = []
positions = []

for e in resp.css(".items").xpath("./tbody/tr/td/a"):
    club_sel = e.css("img")
    # print(clubs)
    club = club_sel.xpath("@alt").extract()
    # print(club_link)
    clubs.append(club[0])

for e in resp.css(".inline-table").xpath("./tr/td"):
    position = e.xpath("text()").extract()
    if len(position) < 2:
        positions.append(position[0])

for e in resp.css(".items").xpath("./tbody/tr"):
    player = e.css(".spielprofil_tooltip")
    flag = e.css(".flaggenrahmen")
    centered = e.css(".zentriert")
    price_data = e.css("span")
    player_name = player.xpath("text()").extract()
    cnt = flag.xpath("@title").extract()
    age = centered.xpath("text()").extract()
    value = price_data.xpath("text()").extract()

    
    if len(age) > 1:
        players.append(player_name[0])
        ages.append(age[1])
        mkt_values.append(value[0])
        if cnt:
            nat.append(cnt[0])

# print(players)
# print(nat)
# print(ages)
# print(clubs)
# print(mkt_values)
# print(positions)

# print(len(players))
# print(len(nat))
# print(len(ages))
# print(len(clubs))
# print(len(mkt_values))
# print(len(positions))

player_dict = {}

for n, player in enumerate(players):
    player_dict[player] = [nat[n], ages[n], positions[n], clubs[n],
            mkt_values[n]]

df = pd.DataFrame(player_dict).T.reset_index()
df.columns=['name', 'nationality', 'age',
    'position', 'club', 'market_value']

print(df)
