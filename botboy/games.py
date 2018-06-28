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
    def __init__(self, name, id, hand=[]):
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
        card_values = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        card_suits = ['♥','♦','♣','♠']
        suits = '♥♦♣♠'
        self.default_deck = [v+s for v in card_values for s in card_suits]
        self.deck = self.default_deck*number_of_decks
        random.shuffle(self.deck)
        self.game_started = False

    def draw(self, num_cards=1):
        """Attempting to draw more cards than there is deck will raise
            an exception."""
        cards = []
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
        CardGame.__init__(self,number_of_decks)

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
    def __init__(self, name, id, hand=[]):
        Player.__init__(self,name,id,hand)
        self.suits = '♥♦♣♠'
        self.face_down = []
        self.face_up = []

    def play(self, card, num=1):
        """Play a card with an option to play more than 1.
        This method returns whether or not the player has made a valid
        selection. Whether or not the it is valid to play at the current time
        in the game is up to the game class to decide."""
        # Make sure player has card
        card_present = False
        card_count = 0
        card = card.strip(self.suits)
        if self.hand:
            for c in self.hand:
                c_strip = c.strip(self.suits)
                if card == c_strip:
                    print("Card found in hand")
                    card_present = True
                    card_count += 1
        elif self.face_up:
            print("Checking face_up")
            for c in self.face_up:
                c_strip = c.strip(self.suits)
                if card == c_strip:
                    print("Card found in face_up")
                    card_present = True
                    card_count += 1
        else: # You're playing a face_down card
            print("Playing face_down")
            self.hand = self.face_down.pop()
            card = self.hand[0].strip(self.suits)
            card_present = True
            card_count = 1
            num = 1

        if card_present and num <= card_count:
            # Once this is is discord integrated, this will probably be
            # a discord command. Maybe it should call the Idiot instance
            # .process_play()
            return card, num
        else:
            return None

    def remove_cards(self, card, num=1):
        # Can we assume that this will get valid data? Probably no.
        # Face down cards are added to your hand before you play them
        cards = []
        if self.hand:
            inds = self.find_cards_with_value(self.hand, card.strip(self.suits))
            inds.sort(reverse=True)
            for i in range(num):
                cards.append(self.hand.pop(inds[i]))
                i += 1
            return cards
        elif self.face_up:
            inds = self.find_cards_with_value(self.face_up, card.strip(self.suits))
            inds.sort(reverse=True)
            for i in range(num):
                card.append(self.face_up.pop(inds[i]))
                i += 1
            return cards
        else:
            # This shouldn't happen. THere should always be a hand or face up cards
            return []

    def find_cards_with_value(self,cards, value):
        """Returns a list of all of the indicies where a card with the given
            value is. In the example '4♠', the value is '4'."""
        indices = []
        i = 0
        for c in cards:
            c_strip = c.strip(self.suits)
            if c_strip == value:
                indices.append(i)
            i += 1
        return indices

class Idiot(CardGame):
    players = []
    game_started = False
    cur_player_index = 1
    # Because a 10 can beat anything it gets the highest score.
    # A 2 will just have to be written as an exception
    card_rank = {
        '2' : 2,
        '3' : 3,
        '4' : 4,
        '5' : 5,
        '6' : 6,
        '7' : 7,
        '8' : 8,
        '9' : 9,
        '10': 14,
        'J' : 11,
        'Q' : 12,
        'K' : 13,
        'A' : 14
        }
    def __init__(self,number_of_decks=1):
        CardGame.__init__(self, number_of_decks)
        self.pile = []

    def add_player(self, player):
        if not self.game_started:
            self.players.append(player)
        else:
            print("Game has already started")

    def start(self):
        if len(self.players) < 2:
            print("Not enough players. Need at least 2.")
            return
        self.game_started = True
        self.num_decks = self.det_num_decks(len(self.players))
        self.deal()

    #TODO figure out how this interface should interact with Player.play()
    # Do we pass in the game instance to Player.play()?
    def process_play(self, player, card, num):
        """A player has decided to play. Is it valid?
            @param player the player that is making the play
            @param card the card value being played (A, 9, 6, etc.)
            @param num how many of the card is being played

            It is assumed that the play being made is vaild in the sense that
            the player has the cards. This function will make sure it follows
            game rules such as checking what's in the pile and so forth."""
        # Make sure it can be played - check the pile
        # Check for empty pile or that the played card is >= the top of pile
        pile_rank = self.card_rank[self.pile[-1]]
        # A 2 beats everything, but can be beat by everything.
        # This handles that exception.
        if card.strip(self.suits) == 2:
            card_rank = 14
        else:
            card_rank = self.card_rank[card.strip(self.suits)]
        if self.pile and card_rank < pile_rank:
            # If there is stuff in the pile and what's being played is less
            # valuable than it, then it is invalid
            print("You can't play that!")
            return
        # Remove card(s) from hand/face-up
        cards = player.remove_cards(card,num)
        # Send to IdiotGame pile
        self.pile + cards
        # Check for blowup
        if self.pile[-1].strip(self.suits) == 10:
            self.pile.clear()
            print("BOOM")
        # Check to see if the last 4 are the same
        else:
            boom = True
            # Last 4 of plie
            for c in self.pile[-4:]:
                if c.strip(self.suits) != self.pile[-1].strip(self.suits):
                    #no boom
                    boom = False
                    break
            if boom:
                self.pile.clear()
                print("BOOM")


    def turn(self):
        """Whose turn is it?"""
        return self.players[self.cur_player_index].name

    def deal(self):
        for p in self.players:
            # deal 3 face down, 3 face up, 3 to hand
            p.face_down = self.draw(3)
            p.face_up = self.draw(3)
            p.hand = (self.draw(3))

    def det_first_player(self):
        # The first player is whoever has the 3 of clubs
        # I'll figure this out later
        pass

    def player_order(self):
        s = ''
        i = 1
        for p in self.players:
            s += '{}. {}\n'.format(i, p.name)
            i += 1
        return s


    @staticmethod
    def det_num_decks(num_players):
        return math.ceil(num_players/4)

    #TODO figure out how to format this so it prints more betterer
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
    p1 = IdiotPlayer("Matt","1")
    p2 = IdiotPlayer("Jesse","2")
    g = Idiot()
    g.add_player(p1)
    g.add_player(p2)
    g.start()




