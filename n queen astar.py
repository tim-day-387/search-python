from board import board
import numpy as np
import random as RNG
import time
import queue


def Hfunction(state):
    '''
    Calculate H fucntion: The total squared weights of the lighter queen in conflicting pairs.
    '''
    result = []
    n = state.shape[0]
    
    '''Rows'''
    for i in range(n):
        if len( np.delete(state[i], np.where(state[i] == 0)) ) > 1:
            result.append( np.delete(state[i], np.where(state[i] == 0)) )

    '''Diagonals from top left to bottom right'''
    for i in range(-(n-2), (n-1)):
        aux = np.diagonal(state, offset=i)

        if len( np.delete(aux, np.where(aux == 0)) ) > 1:
            result.append( np.delete(aux, np.where(aux == 0)) )
    
    '''Add results of diagonals from top right to bottom left'''
    for i in range(-(n-2), (n-1)):
        aux = np.diagonal(np.fliplr(state), offset=i)

        if len( np.delete(aux, np.where(aux == 0)) ) > 1:
            result.append( np.delete(aux, np.where(aux == 0)) )
    '''output''' 
    if len(result) == 0:
        result = 0
    else:
        result_ = 0
        for i in result:
            i = np.sort(i)
            n = len(i) - 1
            for j in i:
                result_ += (j**2)*n
                n -= 1
            result = result_

    return result

class BoardA:

    def __init__(self, s,p=None,m=None, c=None, x=None, g_c=None):
        self.s = s.copy() # Current board state
        self.p = p # the parent node of the current 
        self.t = 0 # current cost
        self.h = Hfunction(state = self.s) # current h value
        self.l = 0 # length of solution path 
        self.m_t = [] # the moves to reach this node. 
        self.time = time.time()
        self.astar = self.t + self.h 

    def __lt__(self, other):
        return self.astar<other.astar

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return  np.array_equal(self.s,other.s)
        else:
            return False

    def __hash__(self):
       return hash(self.astar)

    def create_child_astar(self, state, move):
        '''  
            Create a child board 
        '''
        child = BoardA(s=state)
        child.p = self # the parent node of the current node
        child.t = self.t + abs(int(np.where(self.s.T[move[1]] > 0)[0]) - move[0])*np.sum(state, axis=0)[move[1]]**2 
        child.l = self.l + 1 # length of solution path 
        child.m_t = self.m_t + [move] # the moves to reach this node.
        child.time = self.time 
        child.astar = child.t + child.h 

        return child


    def expand_astar(self):
        '''  
            Expand the current node, adding one layer of children
        '''
        output = []

        #all possible spaces 
        x_0 , y_0 = np.where(self.s==0)
        
        weights = np.sum(self.s, axis=0)

        #Create children nodes
        for i in range(len(x_0)):
            
            child_state = self.s.copy()
            #Define the column to 0
            child_state.T[y_0[i]] = 0
            #Replace value
            child_state[(x_0[i], y_0[i])] = weights[y_0[i]] 
            child = self.create_child_astar(child_state, (x_0[i], y_0[i]))

            #output
            if child != self.p:
                output.append(child)
        
        return output

def build(s):
    q=queue.PriorityQueue() #PriorityQueue of expansion nodes
    b=BoardA(s)
    q.put(b)
    s=set()
    s.add(b)
    sum=1
    start_time=time.time()
    while not q.empty():
        current=q.get()
        if (time.time()-start_time)>300:
            print("No solution found in 300 seconds")   
            break
        elif current.h==0: #if heuristic value=0, finish
            print("Initial State:")
            print(b.s)
            print("Total nodes expanded:", sum)
            a=time.time()-start_time
            print("Time Consumption:", "%.2f" % a)
            branch=sum/len(current.m_t)
            print("Effective Branching Factor:", "%.2f" % branch)
            print("Cost:", current.t)
            print("Sequence of moves:",current.m_t)
            print("Solution:")
            print(current.s)
            break
        else:
            child=current.expand_astar()
            for i in child:
                if i not in s:
                    q.put(i)
                    sum+=1
                    s.add(i)
                    
    
#Execution

n = int(input("How many queens:"))
t = board.regularQueens(n)
c=np.nonzero(t.board)
state= np.zeros((n,n))
state[c]= t.board[c]
build(state)

                    
