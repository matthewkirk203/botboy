import asyncio
import random

class Game:
	self.number_of_players = 0
	def reset(self):
		"reset all things to default"

	def play(self):
		"setup game. Print to channel and so forth"

	def join(self):
		"join the game as a player"

	def start(self):
		"start the game with the players that have joined"
		"this should DM each player their hand"

class CardGame(Game):
	def __init__(self,number_of_decks=1):
		card_values = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
		card_suits = ['♥','♦','♣','♠']
		self.deck = [v+s for v in card_values for s in card_suits]
		self.deck = self.deck*number_of_decks
		random.shuffle(self.deck)
		self.game_started = False

class TexasHoldEm(CardGame):
	def __init__(self,number_of_decks=1):
		CardGame(self,number_of_decks)
	
	def fold(self, player):
		"fold the player that issued this command"

	def call(self, player):
		"match the current bet for the player that issued this command"

	def raise_otherword(self, player, amount):
		"raise the bet for the player by amount"

	def check(self, player):
		"basically a pass"
		
class Idiot(CardGame):
	def __init__(self,number_of_decks=1):
		CardGame(self,number_of_decks)
		
	
		
	




