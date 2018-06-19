from urllib.request import urlopen
import aiohttp
import bs4
import json

async def get_sr_old(battle_tag):
    base_url = 'https://playoverwatch.com/en-us/career/pc/'
    battle_tag = battle_tag.split("#")
    battle_tag = "-".join(battle_tag)
    player_url = base_url + battle_tag
    async with aiohttp.ClientSession() as session:
        async with session.get(player_url) as r:
            print("Fetching page for {}".format(battle_tag))
            html = await r.read()
    print("Scraping page for {}".format(battle_tag))
    soup = bs4.BeautifulSoup(html, "lxml")
    comp_div = soup.find("div", class_="competitive-rank")
    # If we didn't find it, they are either unranked or the profile doesn't exist
    #TODO: Figure out how to look for Profile Not Found
    if comp_div is None:
        if soup.find('h1') is not None:
            # Player is unranked
            sr = 0
        # A nonexistent profile shows a 404 page when parsed. It's weird.
        else:
            # Profile doesn't exist
            sr = None
    else:
        sr = comp_div.find("div").contents[0]

    return sr

async def get_sr(battle_tag):
    battle_tag = battle_tag.split("#")
    battle_tag = "-".join(battle_tag)
    url = 'https://owapi.net/api/v3/u/{}/stats'.format(battle_tag)
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    # Have to send User-Agent or the site complains
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as r:
            print("Fetching page for {}".format(battle_tag))
            html = await r.text()
            data = json.loads(html)
            #print(data['us']['stats']['competitive']['overall_stats']['comprank'])
            try:
                sr = data['us']['stats']['competitive']['overall_stats']['comprank']
                if sr == None:
                    sr = 0
                return sr
            except KeyError:
                print("KeyError on {}".format(battle_tag))
                raise KeyError

def test():
    get_sr('RndEarthShil#1735')
    get_sr('icekingsimon#1441')
    get_sr('icekingsimon#14411')