import asyncio

class Game:
	def reset(self):
		"reset all things to default"

	def play(self):
		"setup game. Print to channel and so forth"

	def join(self):
		"join the game as a player"

	def start(self):
		"start the game with the players that have joined"
		"this should DM each player their hand"


class TexasHoldEm(Game):

	default_deck = 'all the cards'

	def __init__(self):
		self.deck = 'array of all the cards here' # ['A♠', '2♠', '3♠'... etc]*5
		self.game_started = False

	def fold(self, player):
		"fold the player that issued this command"

	def call(self, player):
		"match the current bet for the player that issued this command"

	def raise_otherword(self, player, amount):
		"raise the bet for the player by amount"

	def check(self, player):
		"basically a pass"




