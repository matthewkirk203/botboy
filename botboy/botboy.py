import discord
import random
from discord.ext import commands

TOKEN = 'NDMwNTU3MTAxNDU1MDQ4NzE2.DaR7XQ.A_K3I6ULvana5W32H312GdBnZ2A'

description = '''BotBoy is here'''
bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
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
async def rpc(player_choice):
	result_matrix = [['draw','user','bot'],['bot','draw','user'],['user','bot','draw']]
	choices = ['rock','paper','scissors']
	bot_choice_index = random.randint(0,2)	
	player_choice_index = choices.index(player_choice)

	result = result_matrix[bot_choice_index][player_choice_index]

	await bot.say("The winner is: " + result)



bot.run(TOKEN)

