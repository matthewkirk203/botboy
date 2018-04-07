from urllib.request import urlopen
import bs4

def get_sr(battle_tag):
	base_url = 'https://playoverwatch.com/en-us/career/pc/'
	battle_tag = battle_tag.split("#")
	battle_tag = "-".join(battle_tag)
	player_url = base_url + battle_tag
	html = urlopen(player_url)
	soup = bs4.BeautifulSoup(html.read(), "html.parser")
	comp_div = soup.find("div", class_="competitive-rank")
	# If we didn't find it, they are either unranked or the profile doesn't exist
	#TODO: Figure out how to look for Profile Not Found
	if comp_div is None:
		if soup2.find(string="Profile Not Found") is None:
			# Player is unranked
			sr = -1
		else:
			# Profile doesn't exist
			sr = None
	else:
		sr = comp_div.find("div").contents[0]

	print(sr)
	return sr


get_sr('RndEarthShil#1735')
get_sr('icekingsimon#1441')
get_sr('icekingsimon#14411')