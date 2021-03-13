from board import board, moveException
import random as RNG
import time
#code by Romaji.
#god this is kinda a mess.
#at least I comment well.
#this version uses time instead of genetic

seed=input("type something for a set seed, hit enter for random.")
if seed=="":
    RNG.seed()
else:
    RNG.seed(seed)

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
            goalY=max(goalY,0)%8 #normalize it
            while offspring.board[coordinate[0]][goalY]!=0:
                goalY=(goalY+1)%8
            offspring.moveQueen(coordinate[0],coordinate[1],goalY)
                

def makeOffspring(par1,par2,original,mutations1=None,mutations2=None):
    """Combines parent 1 (par1) and parent 2 (par2) without modifying them.
Then, performs any mutations (listed in [queenNumber, amount] format,
where queen number is 0 to 8, 
and amount is how much to move by (if possible. Otherwise, goes to an open space.).
Finally, it computes the proper movement cost from the original.

Then repeats with the alternate offspring.
Offspring 1 uses mutations 1, offspring 2 uses mutations 2

Picks collumns at random for mutation"""
    division=[False] #list for which offspring gets which column. First offspring always gets first colum.
    allFalse=True #make sure there's at least one false.
    for i in range(7):
        temp=(RNG.random()>0.5)
        if temp==True:
            allFalse=False
        elif i==6 and allFalse:
            temp=True #ensure last one is true if all others are False
        division.append(temp)
    #make the offspring
    off1=par1.copy()
    off2=par2.copy()
    for col in range(8):
        if division[col]: #only swap if marked.
            for row in range(8):
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
while allowedTime:
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


populationSize=True
while populationSize:
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
mutateSize=5 #bigger means more chance of large values

def getMutateList():
    ret=[]
    for queen in range(9):
        if RNG.random() <=0.04:
            moveSize=abs(RNG.randrange(mutate+1)+RNG.randint(-1*mutateSize,mutateSize)) #bias to smaller values.
            if moveSize==0:
                moveSize=1
            elif moveSize>8:
                moveSize=8
            ret.append((queen,moveSize))
    if len(ret)==0:
        return None
    else:
        return ret

print("generating board...")
startBoard = board.extraQueens(8) #Can add an option for changing the max weight if wanted.
startBoard.showState()

print("generating population...")
parents=[]
while len(parents) < populationSize:
    temp=startBoard.copy()
    for i in range(30): #this is slow, but... it's only run once per member of the starting population.
        moves=temp.listMoves()
        move=RNG.choice(moves)
        temp.moveQueen(*move)
    parents.append(temp)
print("parents generated.")
parents.sort(key=lambda this:this.getCost()) #sort by cost, smallest to largest
print("best so far")
parents[0].showState()

generation=1
endAfter=time.process_time()+allowedTime #marks the point when this should stop, by taking the process clock
#before the loop, and adding the number of seconds allowed
bestOf=[parents[0]] #saves the best of each generation for later display
while time.process_time() < endAfter: #has the clock hit the ending yet?
    kids=parents[:preserve] #keep the top however many
    #culling step
    parents=parents[:-1*cull]
    while len(kids) < populationSize:
        parentIndex1= int((RNG.uniform(1,(len(parents))**2))**0.5)-1 #biases more to lower ranked parents. Cannot be the last parent
        parentIndex2= int((RNG.uniform((parentIndex1+1)**2,(len(parents)+1)**2))**0.5)-1 #can be the last parent. Higher than par1
        #get the parents
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
    midCost=bestOf[(generation/2)-1].getCost()
    firstCost=bestOf[0].getCost()
    print("at start",firstCost,"then half way",midCost,"with finally ending on",lastCost)
    if (lastCost/midCost) > (midCost/firstCost):
        print("it really picked up at the end")
    else:
        print("the first half was at least as good as the second")
elif q=="f":
    bestOf[-1].showState()
else:
    print("No visualization selected.")
print("Check variable 'bestOf' for the best result of each generation.")
