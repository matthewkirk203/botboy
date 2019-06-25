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
import discord_token
import json

# Voice stuff
discord.opus.load_opus("libopus0")


# Establish db connection
db = 'botboy_database.sqlite'
conn = sqlite3.connect(db)
c = conn.cursor()
overwatch_table = "Overwatch"
rps_table = "RPS"

count = 0
message_list = ["what", "what do you want", "stop it", "cut it out"]

ow_roles = {}

TOKEN = discord_token.botboy_token

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
    guilds = []
    [guilds.append(x) for x in bot.guilds]
    guild = guilds[0]
    log.info('Server: ' + str(guild))

    # Compile list of OW roles per server, in a dictionary
    ranks = ["grandmaster","master","diamond","platinum","gold","silver","bronze"]
    for serv in guilds:
        ow_roles[serv] = [discord.utils.get(serv.roles, name=rank_name) for rank_name in ranks]


@bot.command()
async def hello(ctx):
    """Says world"""
    await ctx.send("world")


@bot.command()
async def add(ctx, left : int, right : int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def gtfo(ctx):
    """Makes Botboy leave (go offline)"""
    conn.close()
    await ctx.send("Bye!")
    await bot.logout()
    quit()


# Rock Paper Scissors
@bot.command()
async def rps(ctx, player_choice):
    """Play rock, paper, scissors against Botboy (eg. !rps r)"""
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
            await ctx.send("ERROR: must enter 'rock' (or r), 'paper' (or p), 'scissors' (or s)")
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
    win_percentage = (wins/(wins+draws+losses))*100
    response += "\nWins: " + str(wins) + "\nDraws: " + str(draws) + "\nLosses: " + str(losses) + "\nWin %: " + str(win_percentage) + "%"
    # Say it
    await ctx.send(response)
    conn.commit()
    
@bot.command()
async def rps_rank(ctx):
    """Rank rps players by # of wins"""
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
        
        win_percentage = (wins/(wins+draws+losses))*100
        # Append win percentage to last entry (because it's last)
        stats[-1].append(str(win_percentage))
        #response += "\n{0:25} {1:4} {2:4} {3:4} {4:6}".format(name, wins, draws, losses, win_percentage)

    em = discord.Embed(title="Rock Paper Scissors Leaderboard", colour=0x800020)
    em.add_field(name="Name", value='\n'.join(stats[0]), inline=True)
    em.add_field(name="W / D / L", value='\n'.join(stats[1]), inline=True)
    em.add_field(name="Win %", value='\n'.join(stats[-1]), inline=True)
    await bot.send_message(ctx.message.channel, embed=em)

# Overwatch
@bot.command()
async def ow_add(ctx, battle_tag, member : discord.Member = None):
    """Add an Overwatch player to the database (e.g. !ow_add JeffKaplan#420 @JeffKaplan)"""
    if member is None:
        member = ctx.message.author
    log.debug(type(member))
    log.debug(discord.Member)
    await bot.send_typing(ctx.message.channel)
    # print(type(member))
    # print(discord.Member)
    if type(member) is not discord.Member:
        await ctx.send("ERROR: @mention the user instead of just typing it")
        return

    # See if the battle_tag is already in the db
    query = sql.select(overwatch_table, column_names=['BattleTag', 'DiscordName'], condition={'BattleTag':battle_tag})
    if len((c.execute(query)).fetchall()) is not 0:
        await ctx.send("Account " + battle_tag + " already in list!")
        return

    sr = await owh.get_sr(battle_tag)
    if sr == None:
        await ctx.send("Account " + battle_tag + " doesn't exist!")
        return

    query = sql.insert(overwatch_table, [battle_tag, sr, str(member)])
    #query = "INSERT INTO " + overwatch_table + " VALUES('" + battle_tag + "', '" + str(member) + "')"
    #print(query)
    c.execute(query)
    await ctx.send("Added " + battle_tag + " with discord member @" + str(member))
    conn.commit()


@bot.command()
async def ow_list(ctx):
    """List players in Overwatch database"""
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

    await ctx.send(output)

@bot.command()
async def ow_rank(ctx):
    """Rank Overwatch players in database by SR"""
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

@bot.command()
async def ow_ru(ctx):
    """Update Discord users' roles according to Overwatch SR"""
    await bot.send_typing(ctx.message.channel)
    squery = sql.select(overwatch_table)
    # Because another query occurs in the loop, you have to put the data into an array first.
    data = c.execute(squery).fetchall()

    # Build list of requests
    print("Building tasks")
    tasks = [asyncio.ensure_future(update_sr(row[0])) for row in data]
    print("asyncio.gather on tasks")
    await asyncio.gather(*tasks)
    conn.commit()

    server = ctx.message.guild
    await update_roles(guild)
    await ctx.send("Done updating roles!")

async def update_sr(battle_tag):
    """Does something like this already exist???"""
    sr = str(await owh.get_sr(battle_tag))
    log.info("Updating {} to SR: {}".format(battle_tag, sr))
    uquery = sql.update(overwatch_table, {"SR":sr}, condition={"BattleTag":battle_tag})
    c.execute(uquery)    



# @bot.command(pass_context=True)
# async def tester(ctx):
#     em = discord.Embed(title='This is a test', description='My Embed Content.', colour=0xDEADBF)
#     em.set_author(name='A BottyBoy', icon_url=bot.user.default_avatar_url)
#     await bot.send_message(ctx.message.channel, embed=em)

@bot.command()
async def test(ctx):
    """A test for dummies"""
    member = ctx.message.author
    # for row in bot.servers:
    #     print(row)

    guilds = []
    [guilds.append(x) for x in bot.guilds]
    guild = guild[0]

    role = discord.utils.get(ctx.message.guild.roles, name='dumb')
    await bot.add_roles(member, role)

async def auto_role_update():
    # TODO: not tested at all
    for server in bot.servers:
        await update_roles(server)

# Update OW roles for given member in given server
async def update_role(member, server):
    """ Update a single role for the given member """
    log.info("--- UPDATING ROLES for {} ---".format(member))
    sr = 0
    # Get a list of all entries for member
    query = sql.select(overwatch_table, order="SR DESC", condition={"DiscordName":str(member)})
    # Determine highest SR for member
    data = c.execute(query).fetchall()
    if len(data) < 1:
        # Member doesn't exist in table
        log.info("    Member " + str(member) + " doesn't exist in table!")
        return
    else:
        log.info("    Using highest SR for {}".format(member))
        sr = data[0][1]

    # Determine OW rank from SR
    rank = get_rank(sr)
    log.info("    SR: {0} -- Rank: {1}".format(sr, rank))

    # Replace roles implementation here    
    new_roles = member.roles
    # Remove all OW related roles from list of member's roles
    for role in ow_roles[server]:
        if role in new_roles:
            log.info("    Removing role {0}".format(role))
            new_roles.remove(role)

    # If player is unranked, don't assign any new roles, otherwise append the correct role
    if rank == "unranked":
        log.info("    Member {0} is unranked, no new role assigned.".format(str(member)))
    else:
        log.info("    Giving member role: {0}".format(rank))
        new_roles.append(discord.utils.get(server.roles, name=rank))

    # Replace roles accordingly
    await bot.replace_roles(member, *new_roles)

# Update OW roles in the given server
async def update_roles(server):

    log.info("--- UPDATING ROLES PER SR ---")
    # Grab distinct members from table
    query = sql.select(overwatch_table, distinct=True, column_names=["DiscordName"])
    data = c.execute(query).fetchall()
    # Build list of the names for which to check
    members = [u[0] for u in data]
    log.info("MEMBERS: " + ','.join(members))
    # Build list of requests to update_role
    # Need to use server.get_member_named() because discord.utils.get doesn't work with 
    # discord member names if you pass in the # part. This way is more robust.
    # If a person doesn't exist in the table, it pretty gracefully skips it.
    # requests = [update_role(server.get_member_named(member), server) for member in members]
    requests = []
    for member in members:
        await asyncio.sleep(.5)
        discord_member = server.get_member_named(member)
        if discord_member is None:
            log.warning("Member {0} does not exist in server".format(member))
        else:
            # requests.append(update_role(discord_member, server))
            await update_role(discord_member, server)
    # Asynchronously perform all calls.
    # await asyncio.wait(requests)

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
    # Build list to remove all rank roles.
    roles = [discord.utils.get(server.roles, name=rank_name) for rank_name in ranks]
    await bot.remove_roles(member, *roles)

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

    global count    

    #log.debug("botboy id: {} / message raw_mentions: {}".format(bot.user.id, message.raw_mentions)) 
    if bot.user.id in message.raw_mentions:
        #log.debug("count: {}".format(count))
        await bot.send_message(message.channel, message_list[count])

        if count >= len(message_list):
            count = 0
        else:
            count += 1
 
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

# bot.loop.create_task(background_tasks(60))
bot.run(TOKEN)
conn.close()
