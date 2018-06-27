import math
import asyncio
import random

class Game:
    number_of_players = 0
    def reset(self):
        "reset all things to default"

    def play(self):
        "setup game. Print to channel and so forth"

    def join(self):
        "join the game as a player"

    def start(self):
        "start the game with the players that have joined"
        "this should DM each player their hand"

class Player:
    """This player can play many types of games"""
    def __init__(self, name, id, hand=list()):
        self.hand = hand
        self.name = name
        self.id = id

    def __str__(self):
        return "Name: {}\nID: {}\nHand: {}".format(self.name, self.id, self.hand)

    def add_to_hand(self, cards):
        self.hand += cards

    def send_hand(self):
        """Send a DM to the user of their hand.
        Need to store the id for this reason. Name in the server might not work?"""
        pass



class CardGame(Game):
    def __init__(self,number_of_decks=1):
        card_values = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
        card_suits = ['♥','♦','♣','♠']
        self.deck = [v+s for v in card_values for s in card_suits]
        self.deck = self.deck*number_of_decks
        random.shuffle(self.deck)
        self.game_started = False

    def draw(self, num_cards=1):
        cards = list()
        for i in range(num_cards):
            cards.append(self.deck.pop())
        if len(cards) == 1: # should we just return a size 1 list?
            return cards[0]
        elif len(cards) > 1:
            return cards
        else: # Deck is empty?
            return None

class TexasHoldEm(CardGame):
    def __init__(self,number_of_decks=1):
        CardGame(self,number_of_decks)

    def fold(self, player):
        "fold the player that issued this command"

    def call(self, player):
        "match the current bet for the player that issued this command"

    def raise_bet(self, player, amount):
        "raise the bet for the player by amount. raise is a keyword, so raise_bet is used"

    def check(self, player):
        "basically a pass"

class IdiotPlayer(Player):
    """This player can only play idiot.
        Should this be a subclass?"""
    # I think using the inherited init is fine?

    face_down = list()
    face_up = list()

class Idiot(CardGame):
    def __init__(self,number_of_decks=1):
        CardGame(self,number_of_decks)
        self.pile = list()

    @staticmethod
    def det_num_decks(num_players):
        return math.ceil(num_players/4)

    @staticmethod
    def rules():
        """Returns the rules for the game."""
        rules = """Idiot is a game played with an normal deck of cards.
        The goal is to get rid of all of your cards. There are no winners,
        there is only one loser, which is the idiot. Normally, we have the
        idiot wear a bucket on their head during the next game, but instead
        we'll give out a special Idiot role and keep track of losses.

        Each player begins the game with 9 cards: 3 face down, 3 face up, and 3 for the hand.
        The face down cards remain face down for the majority of the game,
        they are only flipped up once you have no other cards to play.
        The 6 known cards dealt to each player (3 face up and 3 to the hand) can be chosen
        as the face-up cards for the game. You can only make these swaps at
        the beginning of the game.

        Play proceeds as follows:
        Each turn, a player must either play cards or pick up the pile.
        There is no 'passing'. To play a card, you must have a card that meets or beats
        whatever the top card on the pile is. You can play any number of the same card.
        (e.g. Top card is a 4, I can play 2 additional 4s, a 5, 3 6s, etc.).
        If you can't play a card (or choose not to), you must pick up the pile and
        add it to your hand. If you pick up the pile, that is your turn.
        At the end of your turn, you must draw cards from the deck
        until you have at least 3 cards. If you have more than 3 cards, you do not draw.
        Once the deck is gone, card drawing stops. At this point, cards are only added
        to your hand via picking up the pile.

        Once your hand is empty, you can start playing your face-up cards. If you can't
        play any of your face up cards, you must pick up the pile and cannot resume playing
        face up cards until your hand is empty once again.

        Once your hand is empty and your face-up cards have been played, you can start
        playing your face-down cards. These cards are revealed one at a time when they
        are played. If the revealed card cannot be played, you must pick up the pile,
        adding the revealed card to your hand as well. If the card cannot be played,
        you are not required to reveal its value to the other players. If you
        were able to play your revealed card, that is your turn and play continues
        as normal. You may only play cards on the table if you have no cards in
        your hand. The last player with cards is the IDIOT.

        Cards follow a typical ranking (A > J > 5 > 3 etc.), but has some notable exceptions:
        2: Beats everything, beat by everything. Can always be played, can always be beaten.
        10: Beats everything and 'blows up the pile' (removes the cards in the pile, including
        the 10, from play). This then affords the player of the 10 an extra play (to set the pile).

        Notable additional rule: Playing four-of-a-kind also blows up the pile, following the
        same rules as the 10, the only exception being that the value of the card must be able to
        be played. If playing with multiple decks, playing more than four of a kind has the same
        effect.

        Note:If playing with >4 players, it's wise to play with 2 decks. In general, you should
        use ceil(num_players/4) decks. e.g: 3 players - 1 deck, 5 players - 2 decks, 9 players - 3 decks"""

        return rules

if __name__ == "__main__":
    p = Player("Matt","1")





