from board import board, moveException
from fractions import Fraction as fr #used to invert the costs into fitnesses without roundoff error
import random as RNG
import time
#code by Romaji.
#god this is kinda a mess.
#at least I comment well.
#this version uses time instead of generation

seed=input("type something for a set seed, hit enter for random.")
if seed=="":
    RNG.seed()
else:
    RNG.seed(seed)
size=int(input("how large a board?"))

quickMode=input("run in quick mode? y for yes, anything else for no.")

def mutate(offspring,mutations):
    """mutates offspring by mutations list. See makeOffspring for more details on the format of the list.
Be sure to not have the same queen number twice!
Updates the offspring in place"""
    queens=offspring.getQueens()
    for mutation in mutations:
        coordinate=queens[mutation[0]][:2] #strip the weight information.
        goalY=(2*RNG.randint(0,1)-1)*mutation[1] + coordinate[0] #get the goal Y
        try:
            offspring.moveQueen(coordinate[0],coordinate[1],goalY)
        except moveException:
            goalY=-1*goalY+2*coordinate[0] #flip the direction
            goalY=max(goalY,0)%size #normalize it
            while offspring.board[goalY][coordinate[1]]!=0: #was checking the wrong space for a queen (it goes Y X, not X Y)
                goalY=(goalY+1)%size
            offspring.moveQueen(coordinate[0],coordinate[1],goalY)
                

def makeOffspring(par1,par2,original,mutations1=None,mutations2=None):
    """Combines parent 1 (par1) and parent 2 (par2) without modifying them.
Then, performs any mutations (listed in [queenNumber, amount] format,
where queen number is 0 to size, 
and amount is how much to move by (if possible. Otherwise, goes to an open space.).
Finally, it computes the proper movement cost from the original.
Then repeats with the alternate offspring.
Offspring 1 uses mutations 1, offspring 2 uses mutations 2
Picks columns at random for mutation"""
    division=[False] #list for which offspring gets which column. First offspring always gets first colum.
    allFalse=True #make sure there's at least one true.
    for i in range(size-1):
        temp=(RNG.random()>0.5)
        if temp==True:
            allFalse=False
        elif i==size-2 and allFalse:
            temp=True #ensure last one is true if all others are False
        division.append(temp)
    #make the offspring
    off1=par1.copy()
    off2=par2.copy()
    for col in range(size):
        if division[col]: #only swap if marked.
            for row in range(size):
                temp=off1.board[row][col]
                off1.board[row][col]=off2.board[row][col]
                off2.board[row][col]=temp
    #mutate
    if mutations1 != None:
        mutate(off1,mutations1)
    if mutations2 != None:
        mutate(off2,mutations2)
    #make them have correct cost
    ret1=original.copy()
    ret2=original.copy()
    ret1.autoAdjust(off1) #this function moves everything that's in original to the position of offspring 1, in the cheapest way.
    ret2.autoAdjust(off2)

    return (ret1,ret2)

##generations=True #replaced with timing
##while generations: #this kind of thing would be a function if I was coding cleaner
##    try:
##        generations=int(input("How many generations before asking to continue?"))
##    except ValueError:
##        print("try again with a positive integer.")
##        generations=True
##        continue
##    
##    if generation <=0:
##        print("Must be positive")
##        generations=True
##        continue
##
##    if generation < 30:
##        q=input("are you sure you want it to be that low? hit y to procede:")
##        if q!="y":
##            generations=True
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

timeTillUpdate=True
while timeTillUpdate==True:
    try:
        timeTillUpdate=float(input("how many SECONDS will you wait for an update?"))
    except ValueError:
        print("try again with a positive number")
        timeTillUpdate=True
        continue
    if timeTillUpdate <=0:
        print("must be a positive value")
        timeTillUpdate=True
        continue
    if timeTillUpdate >= allowedTime:
        q=input("Doing this will give no updates. Are you sure? (y for yes)")
        if q=="y":
            timeTillUpdate=2*allowedTime #ensure that it can't do it by accident.
        else:
            print("Please input a time less than", allowedTime)
            timeTillUpdate=True

populationSize=True
while populationSize==True:
    try:
        populationSize=int(input("How many population members?"))
    except ValueError:
        print("try again with a positive integer.")
        populationSize=True
        continue
    if populationSize <=30:
        print("too small.")
        populationSize=True
        continue
    if populationSize %2 ==1: #if it is odd.
        q=input("Warning, code may work strangely if this is odd. Continue (y)?")
        if q!="Y":
            populationSize=True
#and these I'm just going to bake in, you'll have to change the file if you want to modify
preserve=4
cull= 2*(int(populationSize*0.15))
mutateChance=0.04 #per queen number
mutateSize=size//2 +1 #bigger means more chance of large values

def getMutateList():
    ret=[]
    for queen in range((7+9*size)//8): #the +7 makes it so the number of queens rounds up
        if RNG.random() <=0.04:
            moveSize=abs(RNG.randrange(mutateSize+1)+RNG.randint(-1*mutateSize,mutateSize)) #bias to smaller values.
            if moveSize==0:
                moveSize=1
            elif moveSize>size: #these should have been size thw whole time.
                moveSize=size
            ret.append((queen,moveSize))
    if len(ret)==0:
        return None
    else:
        return ret

print("generating board...")
startBoard = board.extraQueens(size) #Can add an option for changing the max weight if wanted.
if quickMode=="y":
    print(startBoard.getCost())
else:
    startBoard.showState()

print("generating population...")
parents=[startBoard.copy()] #make it so it can't be worse than the unmodified board.
while len(parents) < populationSize:
    temp=startBoard.copy()
    for i in range(4*size): #this is slow, but... it's only run once per member of the starting population.
        moves=temp.listMoves()
        move=RNG.choice(moves)
        temp.moveQueen(*move)
    parent=startBoard.copy() #this is to  fix that all those moves will throw the cost crazy high
    parent.autoAdjust(temp) #kinda embarrassing I forgot to do this the first time
    parents.append(parent)
print("parents generated.")
parents.sort(key=lambda this:this.getCost()) #sort by cost, smallest to largest
print("best so far")
if quickMode=="y":
    print(parents[0].getCost())
else:
    parents[0].showState()


generation=1
timeOfLastUpdate=time.process_time()
endAfter=time.process_time()+allowedTime #marks the point when this should stop, by taking the process clock
startTime=endAfter-allowedTime
lastImprovement=0.0
#before the loop, and adding the number of seconds allowed
bestOf=[parents[0]] #saves the best of each generation for later display
while time.process_time() < endAfter: #has the clock hit the ending yet?
    kids=parents[:preserve] #keep the top however many
    #culling step
    parents=parents[:-1*cull]
    #big change to this version: make it so the actual cost of the parents is used in generating rank,
    #not just their position.
    invertedCost=[] #takes the "fitness" function role
    totalInvertedCost=fr() #makes the starting total inverted cost be zero
    for par in parents:
        temp=fr(1,int(par.getCost()))#the int is just so that I'm sure the fraction class won't complain
        invertedCost.append(temp)
        totalInvertedCost+=temp
        
    while len(kids) < populationSize and time.process_time() < endAfter: #makes sure to break out if spent too much time
        #get the parent IDs
        #first parent
        parentIndex1=0
        #make a random fraction between 0 and just less than the total inverted cost
        generatingNumber=fr(RNG.randrange(totalInvertedCost.numerator),totalInvertedCost.denominator)
        while generatingNumber > invertedCost[parentIndex1]: #will continue until the generating number is small enough.
            generatingNumber -= invertedCost[parentIndex1] #remove this element, to represent moving past it
            parentIndex1 +=1 #move forward again
        #now parentIndex 1 is set, but something special is done to make sure the same parent isn't picked twice
        invCostSubPar1=totalInvertedCost-invertedCost[parentIndex1] #remove from the roulet parent 1's index
        parentIndex2=0
        #now make the generating number
        generatingNumber=fr(RNG.randrange(invCostSubPar1.numerator),invCostSubPar1.denominator)
        while True: #writing this differently helps clarify
            if parentIndex2==parentIndex1: #if the indexes are the same, proceed on to skip the parentIndex1 slice
                parentIndex2+=1
                continue
            #otherwise, continue with checking if this in the slice
            if generatingNumber <= invertedCost[parentIndex2]:
                break #if the generating number is small enough, we're done.
            #otherwise, move on to the next index
            generatingNumber -= invertedCost[parentIndex2]
            parentIndex2+=1
        #Now get them from the list
        par1=parents[parentIndex1]
        par2=parents[parentIndex2]
        #make the mutation lists
        mut1=getMutateList()
        mut2=getMutateList()
        #generate the offspring
        offspring=makeOffspring(par1,par2,startBoard,mutations1=mut1,mutations2=mut2)
        kids.extend(offspring) #and now save them
    #sort the kids
    kids.sort(key=lambda this:this.getCost()) #sort by cost, smallest to largest
##    print("generation",generation,"best result")
##    kids[0].showState()
    bestOf.append(kids[0])
    if bestOf[-2].getCost() >bestOf[-1].getCost(): #has it improved?
        lastImprovement=time.process_time()-startTime
    #see if update is needed.
    if time.process_time()>=timeOfLastUpdate+timeTillUpdate:
            timeOfLastUpdate=time.process_time() #save time now, before the screen draw
            if quickMode=="y":
                print(generation,endAfter-timeOfLastUpdate,lastImprovement,
                      bestOf[-1].getCost(),sep=",")
            else:
                print("generation:",generation,"time remaining:",endAfter-timeOfLastUpdate)
                bestOf[-1].showState()
    #move to next generation
    parents=kids
    generation+=1
#now, report the results.
trueTime=time.process_time()-endAfter+allowedTime #mark how much over... probably a ms or so.
print("In",trueTime,"seconds, computed",generation,"generations")
q=input("c for csv output, s for summary, f for final result:").lower()
if q=="c":
    for i in range(bestOf):
        print(i,bestOf[i].getCost(),sep=",")
elif q=="s":
    lastCost=bestOf[-1].getCost()
    midCost=bestOf[(populationSize//2)-1].getCost()
    firstCost=bestOf[0].getCost()
    print("at start",firstCost,"then half way",midCost,"with finally ending on",lastCost)
    if (lastCost/midCost) < (midCost/firstCost):
        print("it really picked up at the end")
    elif (lastCost/midCost) ==(midCost/firstCost):
        print("it was constant")
    else:
        print("the start was the best.")
elif q=="f":
    bestOf[-1].showState()
else:
    print("No visualization selected.")
print("Check variable 'bestOf' for the best result of each generation.")
