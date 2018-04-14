import random
import discord
import logging
import time
from discord.ext import commands
import sqlite3
import sql
import setup
import asyncio
import urllib.request
import overwatch_helpers as owh
import token

# Establish db connection
db = 'botboy_database.sqlite'
conn = sqlite3.connect(db)
c = conn.cursor()
overwatch_table = "Overwatch"
rps_table = "RPS"

TOKEN = token.botboy_token
global server

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
    # Get the server the bot's on. Right now it's just getting 
    # the first one which should hopefully be the one we care about???
    servers = []
    [servers.append(x) for x in bot.servers]
    server = servers[0]
    log.info('Server: ' + str(server))


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
async def ow_add(ctx, battle_tag, member : discord.Member = None):
    if member is None:
        member = ctx.message.author
    log.debug(type(member))
    log.debug(discord.Member)
    await bot.send_typing(ctx.message.channel)
    # print(type(member))
    # print(discord.Member)
    if type(member) is not discord.Member:
        await bot.say("ERROR: @mention the user instead of just typing it")
        return

    # See if the battle_tag is already in the db
    query = sql.select(overwatch_table, column_names=['BattleTag', 'DiscordName'], condition={'BattleTag':battle_tag})
    if len((c.execute(query)).fetchall()) is not 0:
        await bot.say("Account " + battle_tag + " already in list!")
        return

    sr = owh.get_sr(battle_tag)
    if sr == None:
        await bot.say("Account " + battle_tag + " doesn't exist!")
        return

    query = sql.insert(overwatch_table, [battle_tag, sr, str(member)])
    #query = "INSERT INTO " + overwatch_table + " VALUES('" + battle_tag + "', '" + str(member) + "')"
    #print(query)
    c.execute(query)
    await bot.say("Added " + battle_tag + " with discord member @" + str(member))
    conn.commit()


@bot.command()
async def ow_list():
    query = sql.select(overwatch_table, order="LOWER(BattleTag)")
    #query = "SELECT * FROM Overwatch"
    tags = []
    for row in c.execute(query):
        battle_tag = row[0]
        sr = row[1]
        member_name = row[2]
        tags.append([battle_tag, member_name])
    #tags.sort(key=lambda y: y[0].lower())
    log.debug(tags)
    # print(tags)
    output = ''
    for row in tags:
        output += row[0] + " as @" + row[1] + '\n'

    await bot.say(output)

@bot.command(pass_context=True)
async def ow_rank(ctx):
    query = sql.select(overwatch_table, order="SR DESC")
    em = discord.Embed(title="Overwatch SR Leaderboard", colour=0xFF00FF)
    rank = 1
    for row in c.execute(query):
        name = "#"+str(rank)+" "+row[0]
        values = ["SR: " + str(row[1]), "@"+row[2]]
        value = '\n'.join(values)
        em.add_field(name=name, value=value)
        rank += 1
    await bot.send_message(ctx.message.channel, embed=em)

@bot.command(pass_context=True)
async def ow_ru(ctx):
    query = sql.select(overwatch_table)
    for row in c.execute(query):
        battle_tag = row[0]
        sr = str(owh.get_sr(battle_tag))
        c.execute(sql.update(overwatch_table, {"SR":sr}, condition={"BattleTag":battle_tag}))

    conn.commit()

    server = ctx.message.server
    await update_roles(server)

@bot.command(pass_context=True)
async def tester(ctx):
    em = discord.Embed(title='This is a test', description='My Embed Content.', colour=0xDEADBF)
    em.set_author(name='A BottyBoy', icon_url=bot.user.default_avatar_url)
    await bot.send_message(ctx.message.channel, embed=em)

@bot.command(pass_context=True)
async def test(ctx):
    member = ctx.message.author
    for row in bot.servers:
        print(row)

    servers = []
    [servers.append(x) for x in bot.servers]
    server = servers[0]

    role = discord.utils.get(ctx.message.server.roles, name='dumb')
    await bot.add_roles(member, role)

async def auto_role_update():
    # TODO: not tested at all
    for server in bot.servers:
        await update_roles(server)

async def update_roles(server):
    log.info("--- UPDATING ROLES PER SR ---")
    query = sql.select(overwatch_table, order="SR ASC")
    for row in c.execute(query):
        for member in server.members:
            if row[2] == str(member):
                log.info("UPDATING INFO FOR: {0}".format(str(member)))

                # Check if OW account is member's highest SR - is no, continue
                # main = True
                # for check_row in c.execute(query):
                #     # log.info("        CHECKING - row: {0} - check_row: {1}".format(row[2], check_row[2]))
                #     if row[2] == check_row[2] and row[1] < check_row[1]:
                #         # log.info("        CAUGHT HIGHER ACCOUNT - member: {0} - SR: {1}".format(check_row[2], check_row[1]))
                #         main = False
                #         break

                # if not main:
                #     log.info("    Member: {0} - Account with SR: {1} - is not main".format(str(member), row[1]))
                #     continue
                    
                # Determine OW rank from SR
                rank = get_rank(row[1])
                log.info("    SR: {0} -- Rank: {1}".format(row[1], rank))
                # If member is unranked, don't update role
                if rank == "unranked":
                    log.info("    Member {0} is unranked, not updating role.".format(str(member)))
                    continue

                role = discord.utils.get(server.roles, name=rank)
                # If member already has this rank, don't update role
                if role in member.roles:
                    log.info("    Member {0} already has role: {1} - not updating.".format(str(member), str(role)))
                    continue

                log.info("    Updating member: {0} - with role: {1}".format(str(member), str(role)))
                await bot.add_roles(member, role)
                # await remove_other_ranks(server, rank, member)
            else:
                continue

def get_rank(sr):
    if sr >= 4000:
        return "grandmaster"
    elif sr >= 3500 and sr <= 3999:
        return "master"
    elif sr >= 3000 and sr <= 3499:
        return "diamond"
    elif sr >= 2500 and sr <= 2999:
        return "platinum"
    elif sr >= 2000 and sr <= 2499:
        return "gold"
    elif sr >= 1500 and sr <= 1999:
        return "silver"
    elif sr >= 1 and sr <= 1499:
        return "bronze"
    elif sr == 0:
        return "unranked"

async def remove_other_ranks(server, rank, member):
    log.info("    PASSED IN: {0}".format(rank))
    ranks = ["grandmaster","master","diamond","platinum","gold","silver","bronze"]
    for rank_name in ranks:
        # If rank passed in == rank from list, skip removal
        if rank == rank_name:
            continue

        role = discord.utils.get(server.roles, name=rank_name)

        # If role doesn't exist in server, skip removal
        if role == None:
            log.info("    Role {0} does not exist".format(rank_name))
            continue

        # If member has role, remove it
        if role in member.roles:
            log.info("    Updating member: {0} - removing role: {1}".format(str(member), str(role)))
            await bot.remove_roles(member, role)
        else:
            log.info("    Member does not have role {0} - nothing to remove".format(str(role)))

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
            # log.debug(message.author)
            # log.debug("No attachments found in message")
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
