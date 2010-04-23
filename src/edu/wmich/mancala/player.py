'''
Created on Apr 23, 2010

@author: changwang
'''
import random
import math
import sys

from neuralnet import NeuralNet
from utils import Pair

LEGAL_STRATEGY = ['greedy', 'random', 'weighted', 'exponential']

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
    def __init__(self, id, row=6, numStones=4):
        self.movelist = [[],[]]  # two lists to allow for playing against self
        self.id = 0
        self.learn = None
        self.alpha = 0.5
        self.discount = None
        self.setID(id)
        self.rowSize = row
        self.inputSize = 2+2*self.rowSize+1
        self.Q = NeuralNet(self.inputSize, 2 * self.inputSize)
        self.recentGames = []
        self.numIterations = 1
        self.numRecent = 1
        
    def setID(self, id):
        if id > 1 or id < 0:
            return False
        self.id = id
        return True
    
    def setLearning(self, toLearn):
        self.learn = toLearn
        
    def setDiscountFactor(self, discount):
        if discount > 1 or discount < 0:
            return False
        self.discount = discount
        return True
    
    def setStrategy(self, strategy):
        if strategy in LEGAL_STRATEGY:
            self.strategy = strategy
            return True
        return False
    
    def getMove(self, board):
        pass
        # FIXME
        
    def _getRandIndex(self, validQvals):
        """ choose a move randomly with uniform distribution """
        return random.randint(len(validQvals))
    
    def _getWeightedIndex(self, validQvals):
        """ choose a move randomly based on predicted Q values """
        validQvals = self._makePositive(validQvals)
        sumValue = sum(validQvals)
        arrow = random.random() * sumValue
        runningSum = 0
        for i in validQvals:
            runningSum += i
            if runningSum >= arrow:
                return i
        return 0
    
    def _getExponentialIndex(self, validQvals):
        validQvals = self._makePositive(validQvals)
        validQvals = self._getExponentialValues(validQvals)
        return self._getWeightedIndex(validQvals)
    
    def _getExponentialValues(self, arr):
        for index, val in enumerate(arr):
            arr[index] = math.exp(val)
            
        return arr
    
    def _makePositive(self, arr):
        """ if array has a negtive value, its abs value is added to
        all elements of the array; half the least postive value is then
        assigned for all zero values """
        
        min = min(arr)
        if min < 0:
            arr = self._addToArray(min, arr)
            min = self._getMinPos(arr)
            arr = self._addToZeros(min/2, arr)
        return arr
        
    def _getMinPos(self, arr):
        """ find the minimum positive value in the array """
        min = sys.maxint
        found = False
        for i in arr:
            if i > 0 and i < min:
                min = i
                found = True
                
        if found: return min
        else: return 0
        
    def _addToZeros(self, num, arr):
        """ add num to all zero values in the array """
        for index, val in enumerate(arr):
            if val == 0:
                arr[index] += num
        return arr
                
    def _addToArray(self, num, arr):
        """ add the number to all values in the array """
        return [i + num for i in arr]
    
    def _getBestIndex(self, validQvals):
        """ choose current expected best move """
        maxVal = validQvals # FIXME
        bestMoves = []
        for index, val in enumerate(validQvals):
            if val == maxVal:
                bestMoves.append(index)
                
        # heuristic: choose last bucket
        return bestMoves[-1]
    
    def _getQvals(self, board):
        state = self._getState(board)
        toNN = []
        for i in range(1, self.inputSize):
            toNN.append(state[i-1])
            
        qVals = []
        for i in range(self.rowSize):
            toNN[0] = i
            qVals[i] = self.Q.calculate(toNN)
        return qVals
        
    def _getState(self, board):
        mySide = board.mySide(self.id)
        oppSide = board.oppSide(self.id)
        myMancala = board.stonesInMyMancala(self.id)
        oppMancala = board.stonesInOppMancala(self.id)
        
        state = []
        state.append(myMancala)
        for i in range(self.rowSize):
            state.append(mySide[i])
        state.append(oppMancala)
        for i in range(self.rowSize):
            state.append(oppSide[i])
            
        return state
    
    def gameOver(self, myScore, oppScore):
        if not self.learn:
            return
        
        reward = myScore - oppScore
        self.movelist[self.id].append(reward)
        self._updateGameRecord(self.movelist[self.id])
        self.movelist[self.id] = []
        self._learnFromGameRecord()
        
    def _learnFromGameRecord(self):
        for i in self.recentGames:
            self._learnFromGame(self.recentGames[i])
            
    def _learnFromGame(self, movelist):
        reward = movelist[-1]
        # update Q function
        sap = movelist[-2]
        state = sap.state
        action = sap.action
        example = state[:]
        example[0] = action/1.0
        oldQ = self.Q.calculate(example)
        newQ = (1 - self.alpha) * oldQ + self.alpha * reward
        self.Q.learnFromExample(example, newQ)
        
        nextState = state[:]
        nextAction = action
        nextExample = example[:]
        
        for i in range(len(movelist)):
            sap = movelist[-i-1]
            reward = sap.reward
            state = sap.state
            action = sap.action
            
            example = action[:]
            example[0] = action
            
            # find expected rewards
            qVals = []
            for i in range(self.rowSize):
                nextExample[0] = i/1.0
                qVals[i] = self.Q.calculate(nextExample)
            
            maxVal = max(qVals)
            oldQ = self.Q.calculate(example)
            newQ = (1 - self.alpha) * oldQ + self.alpha * (reward + self.discount * maxVal)
            self.Q.learnFromExample(example, newQ)
            
    def _updateGameRecord(self, moves):
        """ update statistics """
        while len(self.recentGames) > self.numRecent:
            del self.recentGames[0]
        self.recentGames.extend(moves)
        
    def setNumRecent(self, recent):
        """ change number of results to store as recent """
        self.numRecent = recent
        
    def setNumIterations(self, iters):
        self.numIterations = iters
        
class RandomPlayer(Player):
    pass

class SimplePlayer(Player):
    pass

if __name__ == '__main__':
    nnplayer = NNPlayer(1)
    print nnplayer.id