from board import board, moveException
import time
import random as RNG
#code by Romaji.
#god this is kinda a mess.
#at least I comment well.

#alternate version that limits time taken instead of number of restarts
# and reflects the change for repeated moves.

seed=input("type something for a set seed, hit enter for random.")
if seed=="":
    RNG.seed()
else:
    RNG.seed(seed)

sideways=int(input("How many sideways moves?")) 
##updates=True
##while updates:
##    updates=int(input("How many moves before updating (or 0 to hide all work)?"))
##    if updates == 0:
##        q=input("No updates? Type n to cancel, anything else to procede.")
##        if q=="n":
##            updates=True
##        else:
##            print("continuing in silent mode...")
##            
##    elif updates < 0:
##        print("bad value! Retry.")
##        updates=True
##    elif updates < 100:
##        print("Warning, setting this too low can cause slowdown due to printing.")
##        q=input("are you sure you want to get updates that often? (y to confirm)")
##        if q!="y":
##            print("Try again, then.")
##            updates=True
size=int(input("How large a board?"))

restartShuffle=int(input("how many random moves to make for a restart?"))
#this determines how many moves are made at a random restart to ensure they
#don't do the same thing. Should not be more than the number of queens, as each queen is moved once.
#restarts=int(input("how many restarts?"))
allowedTime=None
while allowedTime==None:
    try:
        allowedTime=float(input("how many SECONDS will you allow this to run for?"))
    except ValueError:
        print("try again with a positive number")
        allowedTime=None
        continue
    if allowedTime <=0:
        print("must be a positive value")
        allowedTime=None
        continue

timeTillUpdate=None
while timeTillUpdate==None:
    try:
        timeTillUpdate=float(input("how many SECONDS will you wait for an update?"))
    except ValueError:
        print("try again with a positive number")
        timeTillUpdate=None
        continue
    if timeTillUpdate <=0:
        print("must be a positive value")
        timeTillUpdate=None
        continue
    if timeTillUpdate >= allowedTime:
        q=input("Doing this will give no updates. Are you sure? (y for yes)")
        if q=="y":
            timeTillUpdate=2*allowedTime #ensure that it can't do it by accident.
        else:
            print("Please input a time less than", allowedTime)
            timeTillUpdate=None
            
print("generating board...")
startBoard = board.extraQueens(size) #Can add an option for changing the max weight if wanted.
startBoard.showState() #assuming the biggest possible is 2 digits.

bestBoard=startBoard
bestCost=startBoard.getCost()
initialCost=bestCost
#movesToBestBoard=[] #no longer needs to save moves
restartOfBestBoard=-1
timeElapsedWhenFound=0.0

timeOfLastUpdate=time.process_time()
endAfter=time.process_time()+allowedTime
restart=0
while time.process_time() < endAfter:
    thisBoard=startBoard.copy()
    #moveList=[]
    restart+=1
    if restart > 1: #don't shuffle first attempt
        usedList=[] #contains a LIST of queens that have been moved
        #(by new position and weight, to make it easier)
        #list as unhashable objects only
        for queen in range(restartShuffle):
            possible=thisBoard.getQueens()
            
            choice=None
            while choice==None: #randomly get and remove items until an unused is found
                #will throw an error if runs out of options.
                index=RNG.randrange(len(possible)) #chose an index.
                choice=possible.pop(index)
                if choice in usedList: 
                    choice=None
            #now, proced to randomly move it. 
            newY=RNG.randrange(thisBoard.size)
            while True: #loop until the move works
                try:
                    thisBoard.moveQueen(choice[0],choice[1],newY)
                    break
                except moveException:
                    newY=(newY+1)%thisBoard.size #try one down, then from the top
            #save the old and new coordinates of the successful move for the list.
            oldCord=choice[:2] #strip the weight info
            choice[0]=newY #make it reflect the new position.
            newCord=choice[:2]
            
            #moveList.append((oldCord,newCord)) #save the move
            usedList.append(choice) #save that this queen has been moved.

    sidewaysRemaining=sideways
    
    while time.process_time() < endAfter and sidewaysRemaining >0:
        #Should end before the process time, but just in case
        #get our next possible moves, and go through them.
        possibleNext=thisBoard.listMoves()
        costToBeat=thisBoard.getCost() #look for moves the same or better.
        bestMoves=[] #list of moves found as good as costToBeat.
        for move in possibleNext:
            temp=startBoard.copy() #make a copy for auto adjust
            temp2=thisBoard.moveQueenCopy(*move) #so clean
            temp.autoAdjust(temp2) #reset the cost system
            if temp.getCost() > costToBeat:
                continue #if it gets worse, ignore it
            if temp.getCost() == costToBeat:
                bestMoves.append(move) #add to the list
            else: #if it's better
                costToBeat=temp.getCost() #save the cost
                bestMoves=[move] #and clear the list, saving just it.
        #then, see if the best move is sideways.
        #print(bestMoves)#debug
        if costToBeat == thisBoard.getCost(): 
            sidewaysRemaining -=1 #remove one
            #print(sidewaysRemaining) #debug
        else:
            sidewaysRemaining=sideways #otherwise, reset the counter.
            
        try:
            chosenMove=RNG.choice(bestMoves)
        except IndexError: #if there's no moves, then this is done
            break
        #save the chosen move
        #moveList.append(((move[0],move[1]),(move[2],move[0])))
        #do the chosen move
        newBoard=thisBoard.moveQueenCopy(*chosenMove) #... this was move. Which didn't work.
        #newBoard.showState()#debug
        #now, replace this board with the original, for auto adjust
        thisBoard=startBoard.copy()
        thisBoard.autoAdjust(newBoard)

        if time.process_time()>=timeOfLastUpdate+timeTillUpdate:
            timeOfLastUpdate=time.process_time() #save time now, before the screen draw
            thisBoard.showState()
            #newBoard.showState() #debug, these should be the same
            #print(chosenMove) #come on, please.
            print("restart:",restart, 
                  "time remaining:",endAfter-timeOfLastUpdate) #might be negative on the last loop.
            
    #now, we're done with the hill climbing loop, time to check if it's the best
    if thisBoard.getCost() < bestCost:
        #note, if the cost isn't better, don't save it.
        bestBoard=thisBoard
        bestCost=thisBoard.getCost()
        #movesToBestBoard=moveList
        restartOfBestBoard=restart
        # record when found
        timeElapsedWhenFound=time.process_time()-endAfter+allowedTime
    #otherwise, just proceed without recording.
# get how long it truly took.
trueTime=time.process_time()-endAfter+allowedTime
# finally, print the stuff.
bestBoard.showState()
#print("Moves")
#print(*movesToBestBoard,sep="\n") #split each one across a line
print("Cost reduced from",initialCost,", reduced by",100*(bestCost/initialCost),"%")
print("Restart number:",restartOfBestBoard)
print("Found",timeElapsedWhenFound,"seconds into computation")
print("true time elapsed:",trueTime,"seconds vs",allowedTime,"seconds specified.")
