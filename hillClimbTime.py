from board import board, moveException
import random as RNG
#code by Romaji.
#god this is kinda a mess.
#at least I comment well.

#alternate version that limits time taken instead of number of restarts 

seed=input("type something for a set seed, hit enter for random.")
if seed=="":
    RNG.seed()
else:
    RNG.seed(seed)

sideways=int(input("How many sideways moves?")) 
updates=True
while updates==True:
    updates=int(input("How many moves before updating (or 0 to hide all work)?"))
    if updates == 0:
        q=input("No updates? Type n to cancel, anything else to procede.")
        if q=="n":
            updates=True
        else:
            print("continuing in silent mode...")
            
    elif updates < 0:
        print("bad value! Retry.")
        updates=True
    elif updates < 100:
        print("Warning, setting this too low can cause slowdown due to printing.")
        q=input("are you sure you want to get updates that often? (y to confirm)")
        if q!="y":
            print("Try again, then.")
            updates=True

restartShuffle=int(input("how many random moves to make for a restart?"))
#this determines how many moves are made at a random restart to ensure they
#don't do the same thing. Should not be more than 9, as each queen is moved once.
#restarts=int(input("how many restarts?"))
allowedTime=True
while allowedTime==True:
    try:
        allowedTime=float(input("how many SECONDS will you allow this to run for?"))
    except ValueError:
        print("try again with a positive number")
        allowedTime=True
        continue
    if allowedTime <=0:
        print("must be a positive value")
        allowedTime=True
        continue

print("generating board...")
startBoard = board.extraQueens(8) #Can add an option for changing the max weight if wanted.
startBoard.showState() #assuming the biggest possible is 2 digits.

bestBoard=startBoard
bestCost=startBoard.getCost()
movesToBestBoard=[]
restartOfBestBoard=-1
timeElapsedWhenFound=0.0

endAfter=time.process_time()+allowedTime

while time.process_time() < endAfter:
    thisBoard=startBoard.copy()
    moveList=[]
    
    if restart > 0: #don't shuffle first attempt
        usedSet={} #contains a set of queens that have been moved
        #(by new position and weight, to make it easier)
        for queen in range(restartShuffle):
            possible=thisBoard.getQueens()
            
            choice=None
            while choice==None: #randomly get and remove items until an unused is found
                #will throw an error if runs out of options.
                index=RNG.randrange(len(possible)) #chose an index.
                choice=possible.pop(index)
                if choice in usedSet: 
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
            
            moveList.append((oldCord,newCord)) #save the move
            usedSet.add(choice) #save that this queen has been moved.

    sidewaysRemaining=sideways
    tillUpdate=updates
    
    while True: #the break out condition is later. Possible make option for finite?
        if thisBoard.startCost >= bestCost: #if there's no way we can be better,
            break #just leave
        #otherwise, get our next possible moves, and go through them.
        possibleNext=thisBoard.listMoves()
        costToBeat=thisBoard.getCost() #look for moves the same or better.
        bestMoves=[] #list of moves found as good as costToBeat.
        for move in possibleNext:
            temp=thisBoard.moveQueenCopy(*move) #so clean
            if temp.getCost() > costToBeat:
                continue #if it gets worse, ignore it
            if temp.getCost() == costToBeat:
                bestMoves.append(move) #add to the list
            else: #if it's better
                costToBeat=temp.getCost() #save the cost
                bestMoves=[move] #and clear the list, saving just it.
        #then, see if the best move is sideways.
        if costToBeat == thisBoard.getCost(): #then this is sideways
            sidewaysRemaining -=1 #remove one
            if sidewaysRemaining <1:
                break
        else:
            sidewaysRemaining=sideways #otherwise, reset the counter.
            
        try:
            chosenMove=RNG.choice(bestMoves)
        except IndexError: #if there's no moves, then this is done
            break
        #save the chosen move
        moveList.append(((move[0],move[1]),(move[2],move[0])))
        #do the chosen move
        thisBoard.moveQueen(*move)

        tillUpdate-=1
        if tillUpdate==0: #waits until it's decreased to 0, but if starts at 0,
            #will never run
            thisBoard.showState()
            print("moves:",len(moveList),"restart:",restart+1)
            tillUpdate=updates
    #now, we're done with the hill climbing loop, time to check if it's the best
    if thisBoard.getCost() < bestCost:
        #note, if the cost isn't better, don't save it.
        bestBoard=thisBoard
        bestCost=thisBoard.getCost()
        movesToBestBoard=moveList
        restartOfBestBoard=restart
        # record when found
        timeElapsedWhenFound=time.process_time()-endAfter+allowedTime
    #otherwise, just proceed without recording.
# get how long it truly took.
trueTime=time.process_time()-endAfter+allowedTime
# finally, print the stuff.
bestBoard.showState()
print("Moves")
print(*movesToBestBoard,sep="\n") #split each one across a line
print("Restart number:",restartOfBestBoard)
print("Found",timeElapsedWhenFound,"seconds into computation")
print("true time elapsed:",trueTime,"seconds vs",allowedTime,"seconds specified.")
