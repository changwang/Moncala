#coding:utf-8
'''
Created on Apr 23, 2010
@author: changwang
'''
import random
import math
import sys

from neuralnet import NeuralNet

PLAYER_TYPES = [
    "simple",
    "random",
    "neuralnet",
    "human",
]

class Pair(object):
    """ struct to hold state, action, reward """
    
    def __init__(self, state, action, reward=0):
        self.state = state
        self.action = action
        self.reward = reward
        
    def __repr__(self):
        return "(a=" + self.action + ", r=" + self.reward + ", s=" + self.state + ")"

class Player(object):
    """ this is a abstract class, defines the neccessary methods that
    a player should have. there may have different type of players,
    like human player, nnplayer (neural network), simple player, 
    random player, et."""
    def setID(self, id):
        """ set the identity of the player """
        raise NotImplementedError("must be implemented in subclass") 
    
    def getMove(self, board):
        """ return the player's next move from 1 to rowSize """
        raise NotImplementedError("must be implemented in subclass")
    
    def gameOver(self, myScore, oppScore):
        """ notify the player of the endgame result """
        raise NotImplementedError("must be implemented in subclass")
    
class NNPlayer(Player):
    """ A manacala player uses a neural network to store its approximation function """
    
    LEGAL_STRATEGY = [
        'greedy',
        'random', 
        'weighted', 
        'exponential'
    ]
    
    def __init__(self, id, row=6, numStones=4):
        self.setID(id)
        
        self.learn = True
        self.alpha = 0.5
        self.discount = 0.9
        
        self.rowSize = row
        self.stones = numStones
        self.movelist = [[]] * 2  # two lists to allow for playing against self
        
        self.inputSize = 2+2*self.rowSize+1
        self.Q = NeuralNet(self.inputSize, 2 * self.inputSize) # set the hidden layer 2 times the input layer
        # if exploit, choose expected optimal move
        # otherwise, explore (randomize choice)
        self.strategy = "greedy"
        
        self.recentGames = []   # holds the transcripts of the most recent games
        self.numIterations = 1
        self.numRecent = 1      # number of games to track as recent
        
    def setID(self, id):
        """ set player identity """
        if id > 1 or id < 0:
            return False
        self.id = id
        return True
    
    def setLearning(self, toLearn):
        self.learn = toLearn
        
    def setDiscountFactor(self, discount):
        """ set discount factor """
        if discount > 1 or discount < 0:
            return False
        self.discount = discount
        return True
    
    def setStrategy(self, strategy):
        """ if given strategy is supported return true """
        if strategy in NNPlayer.LEGAL_STRATEGY:
            self.strategy = strategy
            return True
        return False
    
    def getMove(self, board):
        """ chooses next move """
        state = self._getState(board)
        qVals = self._getQvals(board)
        myside = board.mySide(self.id)
        validMoves = [i for i in myside if i > 0]
        
        # if there is no action available, just choose 0
        if len(validMoves) == 0: return -1
        # condense to only non-empty pits
        validQVals = []
        for index, val in enumerate(validMoves):
            validQVals[index] = qVals[val]
            
        # choose action based on strategy
        if self.strategy == NNPlayer.LEGAL_STRATEGY[0]: # greedy
            validMove = self._getBestIndex(validQVals)
        elif self.strategy == NNPlayer.LEGAL_STRATEGY[1]: # random
            validMove = self._getRandIndex(validQVals)
        elif self.strategy == NNPlayer.LEGAL_STRATEGY[2]:   # weighted
            validMove = self._getWeightedIndex(validQVals)
        elif self.strategy == NNPlayer.LEGAL_STRATEGY[3]:   #exponential
            validMove = self._getExponentialIndex(validQVals)
        else:   # greedy
            validMove = self._getBestIndex(validQVals)
        
        move = validMoves[validMove]
        self.movelist[self.id].append(Pair(state, move))
        return move
        
    def _getRandIndex(self, validQvals):
        """ chooses a move randomly with uniform distribution """
        return random.randint(len(validQvals))
    
    def _getWeightedIndex(self, validQvals):
        """ chooses a move randomly based on predicted Q values """
        validQvals = self._makePositive(validQvals)
        sumValue = sum(validQvals)
        arrow = random.random() * sumValue
        runningSum = 0
        for index, val in enumerate(validQvals):
            runningSum += val
            if runningSum >= arrow:
                return index
        return 0
    
    def _getExponentialIndex(self, validQvals):
        """ chooses a moove randomly based on the exponential of the Q values """
        validQvals = self._makePositive(validQvals)
        validQvals = self._getExponentialValues(validQvals)
        return self._getWeightedIndex(validQvals)
    
    def _getExponentialValues(self, arr):
        """ returns an array of the exponential of the values of the array """
        return [math.exp(val) for val in arr]
    
    def _makePositive(self, arr):
        """ if array has a negtive value, its abs value is added to
        all elements of the array; half the least postive value is then
        assigned for all zero values """
        minVal = min(arr)
        if minVal < 0:
            arr = self._addToArray(minVal, arr)
            minVal = self._getMinPos(arr)
            arr = self._addToZeros(minVal/2, arr)
        return arr
        
    def _getMinPos(self, arr):
        """ finds the minimum positive value in the array """
        min = sys.maxint
        found = False
        for i in arr:
            if i > 0 and i < min:
                min = i
                found = True
        # the minimum positive was found
        if found: return min
        # array has no positive values
        else: return 0
        
    def _addToZeros(self, num, arr):
        """ adds num to all zero values in the array """
        for index, val in enumerate(arr):
            if val == 0:
                arr[index] += num
        return arr
                
    def _addToArray(self, num, arr):
        """ adds the num to all values in the array """
        return [i + num for i in arr]
    
    def _getBestIndex(self, validQvals):
        """ chooses current expected best move """
        maxVal = max(validQvals) # FIXME
        bestMoves = [move for move in validQvals if move == maxVal]

        # heuristic: choose last bucket
        return int(bestMoves[-1])
    
    def _getQvals(self, board):
        """ retrieves the q values for all actions from the current state """
        state = self._getState(board)
        # create the input to neural network
        toNN = [state[i-1] for i in range(1, self.inputSize)]
        # find expected rewards
        qVals = []
        for i in range(self.rowSize):
            toNN[0] = float(i)
            qVals[i] = self.Q.calculate(toNN)
        return qVals
        
    def _getState(self, board):
        """ constructs the state as a list """
        mySide = board.mySide(self.id)
        oppSide = board.oppSide(self.id)
        myMancala = board.stonesInMyMancala(self.id)
        oppMancala = board.stonesInOppMancala(self.id)
        
        state = [] # size should be inputSize - 1
        state.append(float(myMancala))
#        for i in range(self.rowSize):
#            state.append(mySide[i])
        for my in mySide:
            state.append(float(my))
        state.append(float(oppMancala))
#        for i in range(self.rowSize):
#            state.append(oppSide[i])
        for op in oppSide:
            state.append(float(op))
        return state
    
    def gameOver(self, myScore, oppScore):
        """ notifies learner that the game is over,
        update the Q function based on win or loss and the move list """
        if not self.learn:
            return
        
        reward = float(myScore) - float(oppScore)
        self.movelist[self.id].append(reward)
        self._updateGameRecord(self.movelist[self.id])
        self.movelist[self.id] = []
        self._learnFromGameRecord()
        
    def _learnFromGameRecord(self):
        for i in self.recentGames:
            self._learnFromGame(self.recentGames[i])
            
    def _learnFromGame(self, movelist):
        reward = float(movelist[-1])
        # update Q function
        sap = movelist[-2]
        state = sap.state
        action = sap.action
        
        example = []
        example.append(float(action))
        example.extend(state[:self.inputSize-1])
        
        oldQ = self.Q.calculate(example)
        newQ = float((1.0 - self.alpha) * oldQ + self.alpha * reward)
        self.Q.learnFromExample(example, newQ)
        
        nextState = state[:]
        nextAction = action
        nextExample = example[:]
        
        for i in range(3, len(movelist)):
            sap = movelist[len(movelist)-i]
            reward = sap.reward
            state = sap.state
            action = sap.action
            
            example = []
            example.append(float(action))
            example.extend(state[:self.inputSize-1])
        
            # find expected rewards
            qVals = []
            for i in range(self.rowSize):
                nextExample[0] = float(i)
                qVals[i] = self.Q.calculate(nextExample)
            
            maxVal = max(qVals)
            oldQ = self.Q.calculate(example)
            newQ = float((1.0 - self.alpha) * oldQ + self.alpha * (reward + self.discount * maxVal))
            self.Q.learnFromExample(example, newQ)
            
    def _updateGameRecord(self, moves):
        """ updates statistics """
        while len(self.recentGames) > self.numRecent:
            del self.recentGames[0]
        self.recentGames.extend(moves)
        
    def setNumRecent(self, recent):
        """ changes number of results to store as recent """
        self.numRecent = recent
        
    def setNumIterations(self, iters):
        self.numIterations = iters
        
    def saveToFile(self, filename, mode):
        self.Q.saveToFile(filename, mode)
        f = open(filename, mode)
        f.write(str(self.id)+"\n")
        f.write(str(self.rowSize)+"\n")
        f.write(str(self.stones)+"\n")
        f.write(str(self.inputSize)+"\n")
        f.write(self.strategy+"\n")
        f.write(str(self.learn)+"\n")
        f.write(str(self.alpha)+"\n")
        f.write(str(self.discount)+"\n")
        f.write(str(self.numIterations)+"\n")
        f.write(str(self.numRecent)+"\n")
        f.flush()
        f.close()
        
    def loadFromFile(self, filename):
        self.Q.loadFromFile(filename)
        f = open(filename, 'r')
        self.id = int(f.readline())
        self.rowSize = int(f.readline())
        self.stones = int(f.readline())
        self.strategy = f.readline().trim()
        self.learn = f.readline()
        self.alpha = float(f.readline())
        self.discount = float(f.readline())
        self.numIterations = int(f.readline())
        self.numRecent = int(f.readline())
        
class RandomPlayer(Player):
    """ this player simply chooses a random pit to play after each move """
    def __init__(self, id):
        self.setID(id)
        self.gamePlayed = 0.0
        self.averageNumTurns = 1.0
        self.thisNumTurns = 0.0
        
    def setID(self, id):
        self.id = id
    
    def gameOver(self, myScore, oppScore):
        """ When called this method will print out some statistics about
        the games it has played """
        self.gamePlayed += 1
        self.averageNumTurns = (self.averageNumTurns * self.gamePlayed + self.thisNumTurns) / self.gamePlayed
        self.thisNumTurns = 0.0
        
    def getMove(self, board):
        """ will pseudo-randomly select the next pit to play """
        self.thisNumTurns += 1
        moves = self._getAvailableActions(board)
        return moves[random.randint(len(moves))]
    
    def _getAvailableActions(self, board):
        """ returns a linked list of all actions that are legal for this state """
        myPits = board.mySide(self.id)
        return [i for i in myPits if i > 0]
            

class SimplePlayer(Player):
    """ the simple player always choosees the pit closet to its own
    mancala to play. this has the effect of trying to retain stones on its
    own side in the hopes that the opponent will run out of stones. """
    def __init__(self, id):
        self.setID(id)
        
    def setID(self, id):
        self.id = id
        return True
        
    def gameOver(self, myScore, oppScore):
        """ does nothing """
        pass
    
    def getMove(self, board):
        """ returns the closest pit to the manacla with stones in it. """
        moves = self._getAvailableActions(board)
        return moves[-1]
    
    def _getAvailableActions(self, board):
        """ returns a list of all actions that are legal
        for this state """
        myPits = board.mySide(self.id)
        return [i for i in myPits if i > 0]

class HumanPlayer(Player):
    def __init__(self, id):
        self.setID(id)
        
    def setID(self, id):
        self.id = id
        
    def getMove(self, board):
        move = -1
        while move < 0:
            move = int(raw_input())
            if move < 1 or move > 6:
                move = -1
                
            if board.mySide(self.id)[move-1] == 0:
                move = -1
        return move
    
    def gameOver(self, myScore, oppScore):
        if myScore > oppScore:
            print "Win"
        elif myScore < oppScore:
            print "Lost"
        else:
            print "Tie"

if __name__ == '__main__':
    nnplayer = NNPlayer(1)
    print nnplayer.id