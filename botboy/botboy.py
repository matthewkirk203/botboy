import random
import discord
import logging
from discord.ext import commands
import sqlite3
import sql
import setup
import asyncio
import urllib.request
import overwatch_helpers as owh

# Establish db connection
db = 'botboy_database.sqlite'
conn = sqlite3.connect(db)
c = conn.cursor()
overwatch_table = "Overwatch"
rps_table = "RPS"

TOKEN = 'NDMwNTU3MTAxNDU1MDQ4NzE2.DaR7XQ.A_K3I6ULvana5W32H312GdBnZ2A'

description = '''BotBoy is here'''
bot = commands.Bot(command_prefix='!', description=description)

async def background_tasks(loop_timer):
    await bot.wait_until_ready()
    counter = 0
    #TODO: Get the channel ID. Right now it is for bot-testing
    channel = discord.Object(id=430560047295234051)
    while not bot.is_closed:
        counter += 1
        await bot.send_message(channel, counter)
        await asyncio.sleep(loop_timer) # task runs every loop_timer seconds

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
@bot.command(pass_context=True)
async def rps(ctx, player_choice):
    # See if player is already in database. If not, create their entry.
    member = str(ctx.message.author)
    query = sql.select(rps_table, condition={"DiscordName":member})
    # Store all results from query in a list of tuples
    results = c.execute(query).fetchall()
    if len(results) == 0:
        # Create entry
        default_values = [member,0,0,0]
        c.execute(sql.insert(rps_table, default_values))
    
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
    
    column_update = {}
    if result == "user":
        winner = "You win!"
        column_update = {"Wins":"Wins+1"}
    elif result == "draw":
        winner = "It's a draw ¯\_(ツ)_/¯"
        column_update = {"Draws":"Draws+1"}
    elif result == "bot":
        winner = "Better luck next time!"
        column_update = {"Losses":"Losses+1"}
        
    # Update database
    c.execute(sql.update(rps_table, column_update, {"DiscordName":member}))
    
    # Create response
    response = "You chose: {0} \nBotBoy chose: {1} \n{2}".format(choices[player_choice_index], choices[bot_choice_index], winner)
    query = sql.select(rps_table, condition={"DiscordName":member})
    results = c.execute(query).fetchone()
    wins = results[1]
    draws = results[2]
    losses = results[3]
    if (draws+losses) == 0:
        win_percentage = 'Infinity!'
    else:
        win_percentage = (wins/(draws+losses))*100
    response += "\nWins: " + str(wins) + "\nDraws: " + str(draws) + "\nLosses: " + str(losses) + "\nWin %: " + str(win_percentage) + "%"
    # Say it
    await bot.say(response)
    conn.commit()
    
@bot.command(pass_context=True)
async def rps_rank(ctx):
    query = sql.select(rps_table, order="Wins DESC")
    #response = "{0:25} {1:4} {2:4} {3:4} {4:6}".format('Name', 'Wins', 'Draws', 'Losses', 'Win%')
    # Create a list of lists that is Name Wins Draws Losses Win%
    stats = [[],[],[]]
    for row in c.execute(query):
        wins = row[1]
        draws = row[2]
        losses = row[3]
        # Populate each sublist with the appropriate value
        stats[0].append(str(row[0]))
        scores = [str(wins),str(draws),str(losses)]
        stats[1].append(" / ".join(scores))

        if (draws+losses) == 0:
            win_percentage = 'Infinity!'
        else:
            win_percentage = (wins/(draws+losses))*100
        # Append win percentage to last entry (because it's last)
        stats[-1].append(str(win_percentage))
        #response += "\n{0:25} {1:4} {2:4} {3:4} {4:6}".format(name, wins, draws, losses, win_percentage)

    em = discord.Embed(title="Rock Paper Scissors Leaderboard", colour=0x800020)
    em.add_field(name="Name", value='\n'.join(stats[0]), inline=True)
    em.add_field(name="W / D / L", value='\n'.join(stats[1]), inline=True)
    em.add_field(name="Win %", value='\n'.join(stats[-1]), inline=True)
    await bot.send_message(ctx.message.channel, embed=em)

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

    query = sql.insert(overwatch_table, [battle_tag, str(member)])
    #query = "INSERT INTO " + overwatch_table + " VALUES('" + battle_tag + "', '" + str(member) + "')"
    #print(query)
    c.execute(query)
    await bot.say("Added " + battle_tag + " with discord member @" + str(member))
    conn.commit()


@bot.command()
async def ow_list():
    query = sql.select(overwatch_table)
    #query = "SELECT * FROM Overwatch"
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

@bot.command()
async def test(battle_tag):
    owh.get_sr(battle_tag)


# Policing
@bot.listen('on_message')
async def policer(message):
    # TODO: add toggle for deleting or not deleting commands
    #       e.g. in videos-memes, commands should not be responded to, and should be deleted
    #       in other channels, we may want to allow commands, but not allow regular text
    #       may require a change to on_message coroutine

    # Get the first word / section in a message, similar to how discord.py does it
    # Inspired by process_commands in bot.py
    view = commands.view.StringView(message.content)
    view.skip_string(bot.command_prefix)
    command = view.get_word()
    log.debug(command)

    # Check if message starts with a command - if yes, return
    if command in bot.commands:
        log.debug("--- caught a command")
        return
    # Check if BotBoy wrote the message
    if message.author != bot.user:
        # Check if the message has attachments
        if not message.attachments:
            log.debug(message.author)
            log.info("No attachments found in message")
            # TODO: get rid of return when we add an await
            # await bot.send_message(message.channel, "You know the rules.")
            return
    else:
        # TODO: do async's need an await every time? Or is return sufficient?
        return

setup.setup_logger()

log = logging.getLogger('BotBoy')

bot.loop.create_task(background_tasks(60))
bot.run(TOKEN)
conn.close()
