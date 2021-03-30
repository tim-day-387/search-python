
import random
seed=input("type something for set seed, hit enter for random")
if seed=="":
    random.seed()
else:
    random.seed(seed)
import abc


###################


class Deck():
    def __init__(self,exceptFor=None):
        self.deck = []
        self.shuffle(exceptFor)
                
    def __str__(self):
        # Print the list without the brackets
        return str(self.deck).strip('[]')
    
    def shuffle(self,exceptFor=None): 
        self.deck = []
        if exceptFor is None: #if not given any exceptions
            skipCards=set() #make the set of cards to skip empty.
        else:
            skipCards=set(exceptFor) #if it's not a set, make it one. 
        for suit in ['U','F','Z','T']:
            for i in range(15):
                card=(suit,i) #turn this into a card, to compare with the set.
                if card not in skipCards: #if skipCards is empty, then don't skip anything.
                    self.deck.append(card)
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
#a player who shows legal cards instead of playing one.
#this only works if yieldMode is true
class YieldPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick,game):#added the game itself, since the AI needs that, even if it isn't used here.
        if len(trick) != 0:
            # Figure out what was led and follow it if we can
            suit = trick[0][0]
            #get a list of all valid cards
            legalCards=[]
            for card in self.hand:
                if card[0]==suit:
                    legalCards.append(card)
            #if it has anything, reveal only the legal cards.
            if len(legalCards)>0:
                return legalCards
        # If the trick is empty or if we can't follow suit, reveal hand
        return self.hand
    #special function only used by this class.
    def removeCard(self,card):
        self.hand.remove(card) # there should be only 1
        
class Game:  # Main class
    def __init__(self, players,yieldMode=False,quietMode=False):
        self.deck = Deck()
        self.players = players
        self.played_cards = []  # List of already played cards in this hand
        self.yieldM=yieldMode #should I yield? Only use with "yieldPlayers", which are used for AI. Very important this is False otherwise
        self.quiet=quietMode #setting this to true makes it not print anything.
        # some constants
        self.HAND_SIZE = 18
        self.ZOMBIE_ARMY = 12
        self.ZOMBIE_ARMY_PENALTY = 20
        self.WIN_SCORE = 200
        
    def slp(self,*args,**kwargs): #"sleepy print" helper function, acts exactly like print if quiet mode is off, does nothing if it is on.
        if self.quiet:
            return
        else:
            print(*args,**kwargs)
            
    def deal(self):
        self.deck.shuffle()
        self.played_cards = []
        for i in range(self.HAND_SIZE):
            for p in self.players:
                p.hand.append(self.deck.getCard())
    
    def dealSpecial(self,knownHand,playedCards,currentTrick): #deals out a virtual set of cards to players, except for the player about to play,
        #who gets the knownHand. Assumes first player goes first this trick. Also allows dealing out mid trick
        exclude=set(knownHand) |set(playedCards)|set(currentTrick) #union all cards we know aren't in other players hands, or in the deck
        self.deck.shuffle(exceptFor=exclude) #shuffle a deck without cards we know shouldn't be there.
        
        #Now, make sure the hand sizes are known.
        handSizes=[len(knownHand)]*3 #start with assuming that all players have the same hand size, will be fixed in next step.
        if len(currentTrick)>=1: #if we are the second or third player, then the first player has one fewer card.
            handSizes[0]-=1 #make the hand size for that player one smaller.
        if len(currentTrick)==2: #if we are the third player, then remove one from the second player as well. If we're the first player, neither if statement happens
            handSizes[1]-=1
        #Deal the hands.
        for pIndex in range(3):
            if pIndex == len(currentTrick): #if this is our known hand,
                self.players[pIndex].hand=knownHand.copy() #then give that player the known hand and keep going.
                continue #we copy it to make sure it doesn't mess with something it's not supposed to
            playerHand=[] #otherwise, get ready to fill a hand, then give it to them
            while len(playerHand) < handSizes[pIndex]:
                playerHand.append(self.deck.getCard())
            self.players[pIndex].hand=playerHand.copy() #make it a copy just in case

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
    
    def playHand(self,leader=0,trick=[]): #splitting off the playing a hand code from the rest. Trick is given here so starting mid trick is possible
        while len(self.players[0].hand) > 0: #while players have a card in hand.
            # Form the trick, get a card from each player. Score the trick.
            for i in range(len(trick),len(self.players)): #for every loop after the first, this is the same as the old code
                p_idx = (leader + i) % len(self.players)
                if self.yieldM: #if in yield mode...
                    #first, get the legal cards
                    legalCards=self.players[p_idx].playCard(trick,self) 
                    #then yield to let the game master choose a card.
                    chosenCard = yield (False,p_idx,legalCards,trick,self.played_cards) #this player would know these things, so use that to decide.
                    #it is not a terminal state, here's the player, the cards allowed to play, what's been played in this trick, and what in this hand.
                    self.players[p_idx].removeCard(chosenCard) #make sure that this card is not in the hand for later
                    trick.append(chosenCard)
                else: #if not using yeild players, just ask them directly
                    trick.append(self.players[p_idx].playCard(trick,self)) #yes, we send the whole game over
            self.slp(self.players[leader].name, "led:", trick)
            win_idx, score, n_zomb = self.scoreTrick(trick)

            # Convert winning trick index into new lead player index
            leader = (leader + win_idx) % len(self.players)
            self.slp(self.players[leader].name, "won trick", score, "points")
            

            # Check for zombie army
            self.players[leader].zombie_count += n_zomb
            if self.players[leader].zombie_count >= self.ZOMBIE_ARMY:  # Uh-oh here comes the Zombie army!
                self.players[leader].zombie_count = -self.ZOMBIE_ARMY #make sure they can't do it again
                self.slp("***** ZOMBIE ARMY *****")
                # Subtract 20 points from each opponent
                for i in range(len(self.players)-1):
                    self.players[(leader+1+i) % len(self.players)].score -= self.ZOMBIE_ARMY_PENALTY
            
            # Update score & check if won
            self.players[leader].score += score
            if self.players[leader].score >= self.WIN_SCORE:
                self.slp(self.players[leader].name, "won with", self.players[leader].score, "points!")
                return (True,True,leader) #is this terminal,did someone win, if so who? is what this should be read as.
            
            # Keep track of the cards played
            self.played_cards.extend(trick)
            trick=[] #now clear the trick, for the next loop.
        
        # Score the kitty (undealt cards)
        self.slp(self.deck)
        win_idx, score, n_zomb = self.scoreTrick(self.deck.deck)
        self.slp(self.players[leader].name, "gets", score, "points from the kitty")
        self.players[leader].score += score
        # Check for zombie army
        if self.players[leader].zombie_count >= self.ZOMBIE_ARMY:
            self.slp("***** ZOMBIE ARMY *****")
            # Subtract 20 points from each opponent
            for i in range(len(self.players)-1):
                self.players[(leader+1+i) % len(self.players)].score -= self.ZOMBIE_ARMY_PENALTY
        # Check for winner
            if self.players[leader].score >= self.WIN_SCORE:
                self.slp(self.players[leader].name, "won with", self.players[leader].score, "points!")
                return (True, True,leader) #yes, the hand ends, yes there's a winner, and it is leader
            #otherwise, another hand is needed.
            return (True, False, leader) #The hand is over, but a winner is not decided. Play next hand.
            
    def play(self):
        lead_player = 0
        while True:  # Keep looping on hands until we have a winner
            self.deal()
            result=self.playHand(leader=lead_player)
            if result[1]==True: #if the hand had someone win,
                return #then we're done.
            #otherwise...
            self.slp("\n* Deal a new hand! *\n")
            # reset the zombie count
            for p in self.players:
                p.zombie_count = 0
            #reset the played cards so they represet this hand
            self.played_cards=[]
            lead_player=result[2] #get the winner of the last hand
            
                
class RandomPlayer(Player):  # Inherit from Player
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick,game): #added the game itself, since the AI needs that, even if it isn't used here.
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

    def playCard(self, trick,game): #added the game itself, since the AI needs that, even if it isn't used here.
        pass  # This is just a placeholder, remove when real code goes here

#helper function to make an imaginary version of the game to play out. Creates with all the information the AI (player 2 in turn order) should know.
def makeVirtualGameCopy(currGame):
    pass #placeholder, also real inputs will be added

class RolloutPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick,game): #game is only used to make a virtual copy, does not hand look
        pass  # This is just a placeholder, remove when real code goes here

class MctsPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick,game): #game is only used to make a virtual copy, does not hand look
        pass  # This is just a placeholder, remove when real code goes here


#######
playahs = []
playahs.append(RandomPlayer("Foo"))
playahs.append(RandomPlayer("AI")) # Change this one for testing different AI
playahs.append(RandomPlayer("Bar"))
theGame = Game(playahs)

theGame.play()
