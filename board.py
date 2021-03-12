import numpy as np
import random as RNG

class moveException (Exception):
    pass

class board:
    """contains a board with weighted queens on it.
    Includes the cost of the board, both as it is, and with the moves up to this point. Note y is first.
    Template by Romaji."""
    #please do this one first, to establish the format it's saved in (probably the same as the "queens" and "extraQueens" formats?)
    def __init__(self,size,queens,extraQueens,startCost=0):
        """size is the size of the board, as a single number (since they are square)
        queens is a array of the main queen for each column, in the format (row,weight)
        extra queens is a array of any additional queens, in the format (coll,row,weight)
        start cost is how much comes from prior moves"""
        board = np.zeros((size, size))

        if(queens != None):
            for i in range(0, size):
                board[queens[i][0]][i] = queens[i][1]

        if(extraQueens != None):
            for i in range(0, len(extraQueens)):
                board[extraQueens[i][1]][extraQueens[i][0]] = extraQueens[i][2]

        self.board = board
        self.startCost = startCost
        self.size = size
        #code by Tim Day

    @classmethod
    def empty(cls,size):
        """Creates an empty board
        Example: test = board.empty(7)"""
        return cls(size, None, None, 0)
        #code by Tim Day

    @classmethod
    def regularQueens(cls,size,maxWeight=9):
        """Creates a board with 1 queen per column
        All queens have weight between 1 and maxWeight
        Example: test = board.regularQueens(4)"""        
        queens = []

        for i in range(0, size):
            queens.append([RNG.randint(0,size-1), RNG.randint(1,maxWeight)])
            
        return cls(size, queens, None, 0)
        #code by Tim Day

    @classmethod
    def extraQueens(cls,size,maxWeight=9):
        """Creates a board with 1 queen per column with an addition 'size' # of queens
        All queens have weight between 1 and maxWeight
        Example: test = board.heavyQueens(4)"""        
        queens = []
        extraQueens = []
        extra = 0
        seen = {}

        for i in range(0, size):
            y = RNG.randint(0,size-1)
            queens.append([y, RNG.randint(1,maxWeight)])
            seen[(i,y)] = 1
            
        while extra < size:
            x = RNG.randint(0,size-1)
            y = RNG.randint(0,size-1)

            if(not((x,y) in seen)):
                extraQueens.append([x, y, RNG.randint(1,maxWeight)])
                extra = extra + 1
                seen[(x,y)] = 1

        return cls(size, queens, extraQueens, 0)
        #code by Tim Day
        
    def showState(self):
        """prints the board state out, in a way like
        Board:
        +-+-+-+-+
        | |1| | |
        +-+-+-+-+
        |2| | |4|
        +-+-+-+-+
        | | | | |
        +-+-+-+-+
        | | |3| |
        +-+-+-+-+
        Cost: [cost number goes here]
        The width is now calculated automatically"""

        width = 0
        
        for i in range(self.size):
            for j in range(self.size):
                if(len(str(self.board[i][j])) > width):
                    width = len(str(self.board[i][j]))
        
        print("Board:")
        token ="+"+width*"-"
        for i in range(self.size):
            print(self.size*token+"+")
            print("|",end="")
            for j in range(self.size):
                if self.board[i][j]!=0:
                    print(str(self.board[i][j]).rjust(width),end="|")
                else:
                    print(" "*width,end="|")
            print()
        print(self.size*token+"+")
        #print(self.board) #replaced by proper board formatting.
        print("Cost:",self.getCost())
        #code by Tim Day, romaji

    def getQueens(self):
        """Returns a list of the queens on the board, same format as set state"""
        queens = []

        for i in range(0, self.getSize()):
            for j in range(0, self.getSize()):
                if(self.board[i][j] != 0):    
                    queens.append([i, j, self.board[i][j]])

        return queens
        #code by Tim Day

    def getSize(self):
        """returns the size of the board (as a single number, as it is square)"""
        return self.size
        #code by Tim Day

    def validMove(self, y1, x1, y2, x2): #wait, what? I thought we'd only look at vertical moves.
        """returns True if the move is valid, false otherwise"""
        output = False

        if(x1 == x2):
            output = True

        if(y1 == y2):
            output = True

        if(abs(y2 - y1) == abs(x2 - x1)):
            output = True

        return output
        #code by Tim Day

    def squaresMoved(self, y1, x1, y2, x2):
        """Gets the number of squares moved"""
        if(self.validMove(y1, x1, y2, x2) == False):
            raise moveException("Invalid move.")     

        if(x1 == x2):
            return abs(y2 - y1)

        if(y1 == y2):
            return abs(x2 - x1)

        return abs(x2 - x1);
        #code by Tim Day
            
    def moveQueen(self, y1, x1, y2, x2=None):
        """moves the queen at y1,x1, to y2, x2. Note that Y is first! assumes same X if not given
        Note that if the queen is already there, it will error, same as if it would overlap with another queen.
        This changes the board, so if you want to keep the old version, use moveQueenCopy"""
        size = self.getSize()
        if x2 == None:
            x2=x1
        
        if(y1 < 0 or y2 < 0 or x1 < 0 or x2 < 0 or y1 >= size or y2 >= size or x1 >= size or x2 >= size):
            raise moveException("Out of bounds.")
        
        if(self.validMove(y1, x1, y2, x2) == False):
            raise moveException("Invalid move.")
            
        if(self.board[y1][x1] == 0):
            raise moveException("No Queen in first position.")
            
        if(self.board[y2][x2] != 0):
            raise moveException("Queen in second position.")

        self.board[y2][x2] = self.board[y1][x1]
        self.board[y1][x1] = 0
        self.startCost = self.startCost + (self.squaresMoved(y1, x1, y2, x2) * self.board[y2][x2]**2)
        #code by Tim Day, Romaji.

    def moveQueenCopy(self, y1, x1, y2, x2=None):
        """Makes a copy of the board, then moves the queen. Useful if you want to explore a selection of moves"""
        ret = self.copy()

        ret.moveQueen(y1, x1, y2, x2)

        return ret
        #code by Romaji, Tim Day
        
    def countPairs(self):
        """returns the number of paired queens on the board, in all directions.
        It does not multiply this value by 100, and does not take into account the moves to get there.
        this is what a class using this one would do.
        Vertical matchings can be computed by just adding the number of extra queens."""
        return 0 #TODO! Actually implement!
        #code by Tim Day

    def getCost(self,includePairs=True):
        """Returns the cost of the board, which is the cost from moves plus 100*[the number of pairs]
        If includePairs is set to False, does not include the cost from paired queens, useful for getting just the cost of movement.
        """
        ret=self.startCost
        if includePairs:
            ret+=100*self.countPairs()
        return ret
        #code by Romaji

    def copy(self):
        """returns a copy of the board object"""
        ret=board(self.size,[(0,0)]*self.size) #makes a blank board of the correct size
        ret.board=self.board
        ret.startCost=self.startCost
        return ret
        #code by Tim Day, Romaji

    def listMoves(self):
        "returns a list of the format (queenY,queenX,newY), of all legal VERTICAL moves (that do something). Useful for hill climbing."
        #code by
        
    def autoAdjust(self,other):
        """if possible, will make the minimum cost moves from itself to reach "other".
        should throw an exception if: Board sizes are different, number of queens are different, or weight of queens are different.
        Remember that if a queen and an extra queen need to swap places, this is three moves: move lighter queen one space (closer 
        if possible), move heavier queen to spot, move lighter queen to the other spot.
        Useful for genetic algorithms."""
        #code by


# Test Code
"""
test = board.empty(7)
test.showState()
test = board.regularQueens(9)
test.showState()
test = board.extraQueens(4)
test.showState()
"""
