import sqlite3 as sql

sql_file = 'botboy_database.sqlite'
overwatch_table = 'Overwatch'
rps_table = 'RPS'

conn = sql.connect(sql_file)
c = conn.cursor()

c.execute('CREATE TABLE ' + overwatch_table + ' (BattleTag varchar, DiscordName varchar)')
c.execute('CREATE TABLE ' + rps_table + ' (DiscordName varchar, Wins int, Draws int, Losses int)')

conn.commit()
conn.close()
