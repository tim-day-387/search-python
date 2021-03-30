import random
seed=input("type something for set seed, hit enter for random")
if seed=="":
    random.seed()
else:
    random.seed(seed)
import abc
import time

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
                yield (True,True,leader) #is this terminal,did someone win, if so who? is what this should be read as.
            
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
            yield (True, True,leader) #yes, the hand ends, yes there's a winner, and it is leader
        else:
            #otherwise, another hand is needed.
            yield (True, False, leader) #The hand is over, but a winner is not decided. Play next hand.
            
    def play(self): #don't use if yield players are in play!
        lead_player = 0
        while True:  # Keep looping on hands until we have a winner
            self.deal()
            try: #have to do it this way since its a generator now
                result=next(self.playHand(leader=lead_player))
            except StopIteration:
                print("Didn't stop successfully.")
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
        #comment out for quiet mode
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
#block of helper keys for grab and duck
#each one places prefered cards at the end of the list,for pop.
def trollKey(card):
    if card[0]=="T": #is this a troll?
        ret=1500 #ensures legal moves triumph if possible
        if card[1]>0: #ensures that ones that beat rank above those that don't
            ret+=100
        ret-=card[1] #prioritizes lowest possible
    elif card[0]=="Z":
        ret=1000+card[1]
    elif card[0]=="F":
        ret=500-card[1]
    else:
        ret=-card[1]
    return ret

def zombieKey(card):
    if card[0]=="Z":
        ret=1500 #ensures legal moves triumph if possible
        if card[1]<0: #ensures that ones that lose rank above those that don't
            ret+=100
        ret+=card[1] #prioritizes highest possible
    elif card[0]=="T":
        ret=1000-card[1]
    elif card[0]=="F":
        ret=500-card[1]
    else:
        ret=-card[1]
    return ret

def fairyKey(card):
    if card[0]=="F":
        ret=1500 #ensures legal moves triumph if possible
        if card[1]>0: #ensures that ones that beat rank above those that don't
            ret+=100
        ret-=card[1] #prioritizes lowest possible
    elif card[0]=="Z":
        ret=1000+card[1]
    elif card[0]=="T":
        ret=500-card[1]
    else:
        ret=-card[1]
    return ret

def unicornKey(card):
    if card[0]=="U":
        ret=1500 #ensures legal moves triumph if possible
        if card[1]>0: #ensures that ones that beat rank above those that don't
            ret+=100
        ret-=card[1] #prioritizes lowest possible
    elif card[0]=="T":
        ret=1000-card[1]
    elif card[0]=="Z":
        ret=500+card[1]
    else:
        ret=-card[1]
    return ret
    

class GrabAndDuckPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick,game): #added the game itself, since the AI needs that, even if it isn't used here.
        if len(trick) != 0:
            #first, if we don't have a choice, just play it.
            if len(self.hand)==1:
                return self.hand.pop()
            # Figure out what was led
            suit = trick[0][0]
            #Next, determine the "threshold to win"
            threshold=trick[0][1]
            if len(trick)==2 and trick[1][0]==suit and trick[1][1]>threshold: #order is important here, 
                #the trick must have 2 entries to look at the second one.
                threshold=trick[1][1] #if that's the case, then the second player will win, so consider their
                #card instead
            #make a "psudo hand" with the threshold subtracted from each card. this makes highest that loses -1,
            # and lowest that loses 1. These help with the key functions.
            pHand=[]
            for card in self.hand:
                pHand.append((card[0],card[1]-threshold))
            #now, sort our psudo hand based on the threshold and the suit played.
            if suit=="T":
                pHand.sort(key=trollKey)
            elif suit=="Z":
                pHand.sort(key=zombieKey)
            elif suit=="F":
                pHand.sort(key=fairyKey)
            else:
                pHand.sort(key=unicornKey)
            #now that it's sorted, we  it, then convert to normal card
            pCard=pHand.pop()
            card=(pCard[0],pCard[1]+threshold)
            #finally, remove the card and return it.
            self.hand.remove(card)
            return card
        else: #how to start the trick
            lowestTroll= 30 #this is an error value. If the "lowest troll" is 30, then I have none.
            lowestZombie= 30 #same idea for each of these
            highestFairy=-30
            highestUnicorn=-30
            #figure out each kind of card.
            for card in self.hand:
                if card[0]=="T": #if it's a troll
                    if card[1] < lowestTroll:
                        lowestTroll=card[1]
                elif card[0]=="Z": #if a zombie
                    if card[1] < lowestZombie:
                        lowestZombie=card[1]
                elif card[0]=="F":
                    if card[1] > highestFairy:
                        highestFairy=card[1]
                else:
                    if card[1] > highestUnicorn:
                        highestUnicorn=card[1]
            #now, see if you have a troll, zombie, fairy, or only unicorns, in that order
            if lowestTroll < 30:
                card=("T",lowestTroll)
                self.hand.remove(card) #should never fail, since lowestTroll is not 30
                return card
            #next, zombies
            if lowestZombie < 30:
                card=("Z",lowestZombie)
                self.hand.remove(card) #should never fail, since lowestZombie is not 30
                return card
            #then fairies
            if highestFairy > -30:
                card=("F",highestFairy)
                self.hand.remove(card) #should never fail, since highestFairy is not -30
                return card
            #if we haven't returned by now, the hand must be all unicorns.
            card=("U",highestUnicorn)
            self.hand.remove(card)
            return card

#helper function to make an imaginary version of the game to play out. Creates with all the information the AI (player 2 in turn order) should know.
#Returns the random state and a generator to use for the AI to play with.
def makeVirtualGameCopy(currGame,thisTrick):
    #make a virtual game with 3 players with set names (to aid in debug)
    alice=YieldPlayer("alice")
    me =YieldPlayer("me")
    bob =YieldPlayer("bob")
    virPlayers=[alice,me,bob]
    #make the scores and zombie_count match
    for i in range(3):
        virPlayers[i].score=currGame.players[i].score
        virPlayers[i].zombie_count=currGame.players[i].zombie_count
    #get my hand and played cards 
    myHand=currGame.players[1].hand
    playedCards=currGame.played_cards
    #now, make the game.
    newGame=Game(virPlayers,yieldMode=True,quietMode=True)
    #deal the cards
    newGame.dealSpecial(myHand,playedCards,thisTrick) #Randomly deal the unknown cards, while keeping the known cards with me.
    #save alice and bob's starting hands
    aliceHand=frozenset(newGame.players[0].hand)
    bobHand=frozenset(newGame.players[2].hand)
    #figure out the leader
    lead=2-len(thisTrick) #if the currentTrick is empty, we are the leader. if there are two cards, bob must have lead.
    #create the generator
    gen = newGame.playHand(leader=lead,trick=thisTrick.copy()) #we copy the trick just in case
    return (gen,aliceHand,bobHand)



class RolloutPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick,game): #game is only used to make a virtual copy, does not hand look
        terminateBy=time.process_time()+1.0 #set a timer for one second.
        while time.process_time() < terminateBy: #loop until time has finished.
            pass #I'm not up for coding this right now

class MctsPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def playCard(self, trick,game): #game is only used to make a virtual copy, does not hand look
        terminateBy=time.process_time()+1.0 #set a timer for one second.
        while time.process_time() < terminateBy: #loop until time has finished.
            pass #I'm not up for coding this right now

# try at the end?
playahs = []
playahs.append(GrabAndDuckPlayer("Foo"))
playahs.append(GrabAndDuckPlayer("AI")) # Change this one for testing different AI
playahs.append(GrabAndDuckPlayer("Bar"))
theGame = Game(playahs)

theGame.play()
