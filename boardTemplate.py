import numpy as np

class board:
    """contains a board with weighted queens on it.
    Includes the cost of the board, both as it is, and with the moves up to this point
    Template by Romaji."""
    #please do this one first, to establish the format it's saved in (probably the same as the "queens" and "extraQueens" formats?)
    def __init__(self,size,queens,extraQueens,startCost):
        """size is the size of the board, as a single number (since they are square)
        queens is a array of the main queen for each column, in the format (row,weight)
        extra queens is a array of any additional queens, in the format (coll,row,weight)
        start cost is how much comes from prior moves"""
        board = np.zeros((size, size))

        for i in range(0, size):
            board[i][queens[i][0]] = queens[i][1]

        if(extraQueens != None):
            for i in range(0, len(extraQueens)):
                board[extraQueens[i][0]][extraQueens[i][1]] = extraQueens[i][2]

        self.board = board
        self.startCost = startCost
        self.size = size
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
        Cost: [cost number goes here]"""

        print("Board:")        
        print(self.board)
        print("Cost:")
        print(self.startCost)
        #code by Tim Day

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

    def validMove(self, y1, x1, y2, x2):
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
            print("Invalid move.")
            return 0        

        if(x1 == x2):
            return abs(y2 - y1)

        if(y1 == y2):
            return abs(x2 - x1)

        return abs(x2 - x1);
        #code by Tim Day
            
    def moveQueen(self, y1, x1, y2, x2):
        """moves the queen numbered as queenNum
        (so 0 to size-1 for normal queens, size and up for extra queens), to row newRow, and adds the cost to its internal cost.
        Note that if the queen is already there, it should do nothing, and if it would overlap with another queen,
        it should error (this would only happen if there's an extra queen on the row).
        This changes the board, so if you want to keep the old version, use moveQueenCopy"""
        size = self.getSize()

        
        if(y1 < 0 or y2 < 0 or x1 < 0 or x2 < 0 or y1 >= size or y2 >= size or x1 >= size or x2 >= size):
            print("Out of bounds.")
            return
        
        if(self.validMove(y1, x1, y2, x2) == False):
            print("Invalid move.")
            return
            
        if(self.board[y1][x1] == 0):
            print("No Queen in first position.")
            return
            
        if(self.board[y2][x2] != 0):
            print("Queen in second position.")
            return

        self.board[y2][x2] = self.board[y1][x1]
        self.board[y1][x1] = 0
        self.startCost = self.startCost + (self.squaresMoved(y1, x1, y2, x2) * self.board[y2][x2] * self.board[y2][x2])
        #code by Tim Day

    def moveQueenCopy(self,queenNum,newRow):
        "Makes a copy of the board, then moves the queen. Useful if you want to explore a selection of moves"
        #code by Romaji
        ret = self.copy()
        ret.moveQueen(queenNum,newRow)
        return ret
        
    def countPairs(self):
        """returns the number of paired queens on the board, in all directions.
        It does not multiply this value by 100, and does not take into account the moves to get there.
        this is what a class using this one would do.
        Vertical matchings can be computed by just adding the number of extra queens."""
        #code by

    def getCost(self,includePairs=True):
        """Returns the cost of the board, which is the cost from moves plus 100*[the number of pairs]
        If includePairs is set to False, does not include the cost from paired queens, useful for getting just the cost of movement.
        """
        #code by

    def copy(self):
        """returns a copy of the board object"""
        #code by

    def listMoves(self):
        "returns a list of the format (queenNum,newRow), of all legal moves (that do something). Useful for hill climbing."
        #code by
        
    def autoAdjust(self,other):
        """if possible, will make the minimum cost moves from itself to reach "other".
        should throw an exception if: Board sizes are different, number of queens are different, or weight of queens are different.
        Remember that if a queen and an extra queen need to swap places, this is three moves: move lighter queen one space (closer 
        if possible), move heavier queen to spot, move lighter queen to the other spot.
        Useful for genetic algorithms."""
        #code by


# Test Code

tq = [[0, 3],[1, 9],[2, 3],[3, 9]]
tqe = [[1, 0, 5]]
test = board(4,tq,tqe,0)
test.showState()
print(test.getQueens())
test.moveQueen(0, 0, 3, 0)
test.showState()
print(test.getQueens())
test.moveQueen(3, 3, 0, 3)
test.showState()
print(test.getQueens())
