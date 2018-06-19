import json
import urllib.request
import time
import aiohttp
import asyncio

def syncronous(battle_tag):
	url = 'https://owapi.net/api/v3/u/{}/stats'.format(battle_tag)
	user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
	headers = {'User-Agent': user_agent}

	req = urllib.request.Request(url,None,headers)
	try:
		with urllib.request.urlopen(req) as response:
			data = json.loads(response.read())
		print(data['us']['stats']['competitive']['overall_stats']['comprank'])

	except urllib.error.HTTPError:
		print("Profile {} not found".format(battle_tag))

async def fetch(session, url):
	async with session.get(url) as response:
		return await response.text()

async def main():
	user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
	headers = {'User-Agent': user_agent}
	tags = ['icekingsimon-1441', 'SideOfRice-11888', 'RndEarthShil-1735']
	tasks = list()
	async with aiohttp.ClientSession(headers=headers) as session:
		for tag in tags:
			task = asyncio.ensure_future(fetch(session, 'https://owapi.net/api/v3/u/{}/stats'.format(tag)))
			tasks.append(task)
		responses = await asyncio.gather(*tasks)
		for r in responses:
			data = json.loads(r)
			print(data['us']['stats']['competitive']['overall_stats']['comprank'])

if __name__ == "__main__":
	#syncronous("icekingsimon-1441")
	#syncronous("icekingsimon-144145")
	#syncronous("Chesterfoppl-11700")

	loop = asyncio.get_event_loop()
	future = asyncio.ensure_future(main())
	loop.run_until_complete(future)