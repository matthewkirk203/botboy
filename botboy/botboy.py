import random
import discord
from discord.ext import commands
import sqlite3 as sql

# Establish db connection
db = 'botboy_database.sqlite'
conn = sql.connect(db)
c = conn.cursor()
overwatch_table = "Overwatch"
rps_table = "RPS"

TOKEN = 'NDMwNTU3MTAxNDU1MDQ4NzE2.DaR7XQ.A_K3I6ULvana5W32H312GdBnZ2A'

description = '''BotBoy is here'''
bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print("DB: " +db)
    print('------')


@bot.command()
async def hello():
    """Says world"""
    await bot.say("world")


@bot.command()
async def add(left : int, right : int):
    """Adds two numbers together."""
    await bot.say(left + right)

@bot.command()
async def leave():
	conn.close()
	await bot.say("Bye!")
	quit()

# Rock Paper Scissors
@bot.command()
async def rpc(player_choice):
	result_matrix = [['draw','user','bot'],['bot','draw','user'],['user','bot','draw']]
	choices = ['rock','paper','scissors']
	bot_choice_index = random.randint(0,2)	
	player_choice_index = choices.index(player_choice)

	result = result_matrix[bot_choice_index][player_choice_index]

	await bot.say("The winner is: " + result)

# Overwatch
@bot.command(pass_context=True)
async def ow_add(ctx, battle_tag, member = None):
	if member is None:
		member = ctx.message.author
	print(type(member))
	print(discord.Member)
	if type(member) is not discord.Member:
		await bot.say("ERROR: @mention the user instead of just typing it")
		return

	query = "INSERT INTO " + overwatch_table + " VALUES('" + battle_tag + "', '" + str(member) + "')"
	#print(query)
	c.execute(query)
	await bot.say("Added " + battle_tag + " with discord member @" + str(member))
	conn.commit()

@bot.command()
async def ow_list():
	query = "SELECT * FROM Overwatch"
	tags = []
	for row in c.execute(query):
		battle_tag = row[0]
		member_name = row[1]
		tags.append([battle_tag, member_name])
	tags.sort(key=lambda y: y[0].lower())
	print(tags)
	output = ''
	for row in tags:
		output += row[0] + " as @" + row[1] + '\n'

	await bot.say(output)



bot.run(TOKEN)
conn.close()
