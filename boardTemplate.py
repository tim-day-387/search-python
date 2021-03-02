class board:
    """contains a board with weighted queens on it.
does not contain the sum total of movement costs, only the cost of each move.
NOTE! Currently no functions are implemented, and this is a template.
Template by Romaji."""
    def setState(size,queens,extraQueens):
        """size is the size of the board, as a single number (since they are square)
queens is a list of the main queen for each column, in the format (row,weight)
extra queens is a list of any additional queens, in the format (coll,row,weight)
This replaces whatever board is there."""

    def showState(width=1):
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
width specifies how many dashes between + characters, and how much room there is for each number"""

    def getNormQueens():
        """Returns a list of the queens on the board, same format as set state
Note that the normal queens start at column zero, not column one"""
        
    def getExQueens():
        """returns a list of extra queens, in the same format as extra queens in set state
Note that each queen here is size+index, so the first extra queen is numbered the size of the board."""

    def getSize():
        "returns the size of the board"

    def moveQueen(queenNum,newRow):
        """moves the queen numbered as queenNum
(so 0 to size-1 for normal queens, size and up for extra queens), to row newRow, and returns the cost.
Note that if the queen is already there, it should return zero, and if it would overlap with another queen,
it should error (this would only happen if there's an extra queen on the row).
This changes the board, so if you want to keep the old version, copy first."""

    def countPairs():
        """returns the number of paired queens on the board, in all directions.
It does not multiply this value by 100, and does not take into account the moves to get there.
this is what a class using this one would do.
Vertical matchings can be computed by just adding the number of extra queens."""

    def copy():
        """returns a copy of the board object"""
