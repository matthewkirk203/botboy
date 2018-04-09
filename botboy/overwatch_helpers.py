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
		#soup = bs4.BeautifulSoup(html.read(),"html.parser")
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


def test():
	get_sr('RndEarthShil#1735')
	get_sr('icekingsimon#1441')
	get_sr('icekingsimon#14411')