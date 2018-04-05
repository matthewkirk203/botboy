import random
import discord
import logging
from discord.ext import commands
import sqlite3


# Establish db connection
db = 'botboy_database.sqlite'
conn = sqlite3.connect(db)
c = conn.cursor()
overwatch_table = "Overwatch"
rps_table = "RPS"

TOKEN = 'NDMwNTU3MTAxNDU1MDQ4NzE2.DaR7XQ.A_K3I6ULvana5W32H312GdBnZ2A'

description = '''BotBoy is here'''
bot = commands.Bot(command_prefix='!', description=description)


@bot.event
async def on_ready():
    log.info('Logged in as: {0}'.format(bot.user.name))
    log.info('ID: {0}'.format(bot.user.id))
    log.info("DB: {0}".format(db))


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
    await bot.logout()
    quit()


# Rock Paper Scissors
@bot.command()
async def rps(player_choice):
    # Result matrix - columns: player's choice / rows: bot's choice
    result_matrix = [['draw','user','bot'],['bot','draw','user'],['user','bot','draw']]
    choices = ['rock','paper','scissors']
    alt_choices = ['r','p','s']
    # Bot makes a choice
    bot_choice_index = random.randint(0,2)
    log.debug("rps - player input: {0}".format(player_choice))
    log.debug("rps - bot's random number: {0}".format(bot_choice_index))
    # Try getting index from players choice
    try:
        player_choice_index = choices.index(player_choice)
    except:
        try:
            player_choice_index = alt_choices.index(player_choice)
        except:
            await bot.say("ERROR: must enter 'rock' (or r), 'paper' (or p), 'scissors' (or s)")
            return

    # Determine result from matrix
    result = result_matrix[bot_choice_index][player_choice_index]

    if result == "user":
        winner = "You win!"
    elif result == "draw":
        winner = "It's a draw ¯\_(ツ)_/¯"
    elif result == "bot":
        winner = "Better luck next time!"
    # Create response
    response = "You chose: {0} \nBotBoy chose: {1} \n{2}".format(choices[player_choice_index], choices[bot_choice_index], winner)
    # Say it
    await bot.say(response)


# Overwatch
@bot.command(pass_context=True)
async def ow_add(ctx, battle_tag, member = None):
    if member is None:
        member = ctx.message.author
    log.debug(type(member))
    log.debug(discord.Member)
    # print(type(member))
    # print(discord.Member)
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
    log.debug(tags)
    # print(tags)
    output = ''
    for row in tags:
        output += row[0] + " as @" + row[1] + '\n'

    await bot.say(output)


@bot.command(pass_context=True)
async def tester(ctx):
    em = discord.Embed(title='This is a test', description='My Embed Content.', colour=0xDEADBF)
    em.set_author(name='A BottyBoy', icon_url=bot.user.default_avatar_url)
    await bot.send_message(ctx.message.channel, embed=em)


def setup_logger():
    logger = logging.getLogger()
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        fmt_str = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        formatter = logging.Formatter(fmt_str)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)

        logger.addHandler(sh)


setup_logger()

log = logging.getLogger('BotBoy')

bot.run(TOKEN)
conn.close()
