class board:
    """contains a board with weighted queens on it.
Includes the cost of the board, both as it is, and with the moves up to this point
Template by Romaji."""
    #please do this one first, to establish the format it's saved in (probably the same as the "queens" and "extraQueens" formats?)
    def __init__(self,size,queens,extraQueens=None,startCost=0):
        """size is the size of the board, as a single number (since they are square)
queens is a list of the main queen for each column, in the format (row,weight)
extra queens is a list of any additional queens, in the format (coll,row,weight)
start cost is how much comes from prior moves"""
        #code by

    def showState(self,width=1):
        """prints the board state out, in a way like
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
width specifies how many dashes between + characters, and how much room there is for each number"""
        #code by

    def getNormQueens(self):
        """Returns a list of the queens on the board, same format as set state
Note that the normal queens start at column zero, not column one"""
        #code by
        
    def getExQueens(self):
        """returns a list of extra queens, in the same format as extra queens in set state, or None if their are none.
Note that each queen here is size+index, so the first extra queen is numbered the size of the board."""
        #code by

    def getSize(self):
        "returns the size of the board (as a single number, as it is square)"
        #code by

    def moveQueen(self,queenNum,newRow):
        """moves the queen numbered as queenNum
(so 0 to size-1 for normal queens, size and up for extra queens), to row newRow, and adds the cost to its internal cost.
Note that if the queen is already there, it should do nothing, and if it would overlap with another queen,
it should error (this would only happen if there's an extra queen on the row).
This changes the board, so if you want to keep the old version, use moveQueenCopy"""
        #code by

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
If includePairs is set to False, does not include the cost from paired queens, useful for getting just the cost of movement."""
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
Remember that if a queen and an extra queen need to swap places, this is three moves: move lighter queen one space (closer if possible), move heavier queen to spot, move lighter queen to the other spot.
Useful for genetic algorithms."""
        #code by
