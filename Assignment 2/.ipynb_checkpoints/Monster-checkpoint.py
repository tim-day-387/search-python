#commented out the lines of code that cause problems
#playahs = []
#playahs.append(RandomPlayer("Foo"))
#playahs.append(RandomPlayer("Bar"))
#playahs.append(RandomPlayer("Baz"))
#game = Game(playahs)

#game.play()

###################

import random
random.seed(2021)
import abc

class Deck():
    def __init__(self):
        self.deck = []
        self.shuffle()
                
    def __str__(self):
        # Print the list without the brackets
        return str(self.deck).strip('[]')
    
    def shuffle(self):
        self.deck = []
        for suit in ['U','F','Z','T']:
            for i in range(15):
                self.deck.append((suit, i))
        random.shuffle(self.deck)
        
    def getCard(self):
        return self.deck.pop()


class Player(metaclass=abc.ABCMeta):  # This is an abstract base class.
    def __init__(self, name):
        self.name = name
        self.hand = []  # List of cards (tuples). I don't think this needs to be a class....
        self.score = 0
        self.zombie_count = 0
        
    def __repr__(self):  # If __str__ is not defined this will be used. Allows easy printing
        # of a list of these, e.g. "print(players)" below.
        return str(self.name) + ": " + str(self.hand) + "\n"
    
    @abc.abstractmethod
    def playCard(self):
        pass

class RandomPlayer(Player):  # Inherit from Player
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick):
        print("-", self.name+"("+str(self.score)+")(Z"+str(self.zombie_count)+")", "sees", trick)
        if len(trick) != 0:
            # Figure out what was led and follow it if we can
            suit = trick[0][0]
            # print(self.name, ":", suit, "was led")
            # Get the first occurence of a matching suit in our hand
            # This 'next' thing below is a "generator expression"
            card_idx = next((i for i,c in enumerate(self.hand) if c[0]==suit), None)
            if card_idx != None:
                return self.hand.pop(card_idx)
        # If the trick is empty or if we can't follow suit, return anything
        return self.hand.pop()

class GrabAndDuckPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick):
        pass  # This is just a placeholder, remove when real code goes here

class RolloutPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick):
        pass  # This is just a placeholder, remove when real code goes here

class MctsPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick):
        pass  # This is just a placeholder, remove when real code goes here

class Game():  # Main class
    def __init__(self, players):
        self.deck = Deck()
        self.players = players
        self.played_cards = []  # List of already played cards
        # some constants
        self.HAND_SIZE = 18
        self.ZOMBIE_ARMY = 12
        self.ZOMBIE_ARMY_PENALTY = 20
        self.WIN_SCORE = 200

    def deal(self):
        self.deck.shuffle()
        self.played_cards = []
        for i in range(self.HAND_SIZE):
            for p in self.players:
                p.hand.append(self.deck.getCard())

    def scoreTrick(self, trick):
        # Score the trick and add the score to the winning player
        # Get the suit led
        suit = trick[0][0]
        value = trick[0][1]
        winner = 0
        score = 0
        # Determine who won (trick position not player!)
        for i in range(len(trick)-1):
            if trick[i+1][0] == suit and trick[i+1][1] > value:
                winner = i+1
                value = trick[i+1][1]
        # Determine the score
        # Separate the suit and value tuples
        suits_list = list(zip(*trick))[0]
        if suits_list.count('T') == 0:
            # No Trolls, go ahead and score the unicorns
            score += suits_list.count('U') * 3
        score += suits_list.count('F') * 2
        n_zomb = suits_list.count('Z')
        score -= n_zomb
        return winner, score, n_zomb  # Index of winning card
        
    def play(self):
        lead_player = 0
        while True:  # Keep looping on hands until we have a winner
            self.deal()
            while len(self.players[0].hand) > 0:
                trick = []
                # Form the trick, get a card from each player. Score the trick.
                for i in range(len(self.players)):
                    p_idx = (lead_player + i) % len(self.players)
                    trick.append(self.players[p_idx].playCard(trick))
                print(self.players[lead_player].name, "led:", trick)
                win_idx, score, n_zomb = self.scoreTrick(trick)

                # Convert winning trick index into new lead player index
                lead_player = (lead_player + win_idx) % len(self.players)
                print(self.players[lead_player].name, "won trick", score, "points")

                # Check for zombie army
                self.players[lead_player].zombie_count += n_zomb
                if self.players[lead_player].zombie_count >= self.ZOMBIE_ARMY:  # Uh-oh here comes the Zombie army!
                    self.players[lead_player].zombie_count = 0
                    print("***** ZOMBIE ARMY *****")
                    # Subtract 20 points from each opponent
                    for i in range(len(self.players)-1):
                        self.players[(lead_player+1+i) % len(self.players)].score -= self.ZOMBIE_ARMY_PENALTY
                
                # Update score & check if won
                self.players[lead_player].score += score
                if self.players[lead_player].score >= self.WIN_SCORE:
                    print(self.players[lead_player].name, "won with", self.players[lead_player].score, "points!")
                    return 
                
                # Keep track of the cards played
                self.played_cards.extend(trick)
            
            # Score the kitty (undealt cards)
            print(self.deck)
            win_idx, score, n_zomb = self.scoreTrick(self.deck.deck)
            print(self.players[lead_player].name, "gets", score, "points from the kitty")
            self.players[lead_player].score += score
            
            # Check for zombie army
            if self.players[lead_player].zombie_count >= self.ZOMBIE_ARMY:
                print("***** ZOMBIE ARMY *****")
                # Subtract 20 points from each opponent
                for i in range(len(self.players)-1):
                    self.players[(lead_player+1+i) % len(self.players)].score -= self.ZOMBIE_ARMY_PENALTY

            # Check for winner
            if self.players[lead_player].score >= self.WIN_SCORE:
                print(self.players[lead_player].name, "won with", self.players[lead_player].score, "points!")
                return 

            print("\n* Deal a new hand! *\n")
            # reset the zombie count
            for p in self.players:
                p.zombie_count = 0
            

# Run it as
