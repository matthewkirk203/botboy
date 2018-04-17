# botboy
A silly attempt at a discord bot. Finally a bot that does the things you want.

# Commands
Commands are mixed between using spaces for arguments and using a "\_" with a prepended tag (e.g. ow_list).
For every command, the bot looks for a "!" before it (e.g. !ow_list).
## Rock Paper Scissors
* _rps player-choice_ - Play Rock Paper Scissors against the bot. The bot will choose rock, paper, or scissors. It will then express the result and update your record.
* _rps\_rank_ - Displays everyone's record sorted by wins.
## Overwatch
* _ow\_add battle-tag member_ - Adds a member to the database. Member will be ranked and have role updated. Note: if member is ommitted, it will use the member calling the command.
* _ow\_list_ - Lists all members in the database alphabetically.
* _ow\_rank_ - Ranks all members in the database by SR.
* _ow\_ru_ - Forces bot to update all SRs and roles.
