'''
Created on Apr 23, 2010

@author: changwang
'''

import math

DELTA = 0.1 # learning rate

class NeuralNet(object):
    def __init__(self, input_size, hidden_size):
        # TODO: make sure there is a bias hidden layer node
        self.inputSize = input_size
        self.hiddenSize = hidden_size
        self.input = [0.0 for i in range(input_size)]     # value of input node
        
        self.output = 0.0   # value of output node
        
        self.weights = [0.0 for i in range(hidden_size)]    # weight of hidden to output node
        
        self.hidden = [0.0 for i in range(hidden_size)]    # value of hidden node
        self.hidden.append(1.0)  # bias for hidden layer
        
        self.hiddenWeights = {}   # two dimensional array, weight of input to hidden node
        for i in range(hidden_size):
            self.hiddenWeights[i] = [0 for j in range(input_size)]
            
    def calculate(self, example):
        """ Calculate the output of the given input """
        self.input = example    # copy example input
        
        # calculate hidden layer
        for i in range(self.hiddenSize):
            self.hidden[i] = 0.0
            for j in range(self.inputSize):
                self.hidden[i] += self.input[j] * self.hiddenWeights[i][j]
            self.hidden[i] = self.sigmoid(self.hidden[i])
        self.output = 0.0
        for i in range(self.hiddenSize):
            self.output += self.hidden[i] * self.weights[i]
            
        return self.output
    
    def learnFromExample(self, example, desired):
        """ update weights to better approximate given example """
        result = self.calculate(example)
        err = desired - result
        for i in range(self.hiddenSize):
            errN = err * self.weights[i] * (1 - self.hidden[i]) * self.hidden[i]
            for j in range(self.inputSize):
                self.hiddenWeights[i][j] += DELTA * errN * self.input[j]
        
        for i in range(self.hiddenSize):
            self.weights[i] += DELTA * err * self.hidden[i]
            
    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))
    
    def printNetwork(self):
        print "==================== beginning ========================="
        print self.input
        print "========================================================"
        print self.hidden
        print "========================================================"
        print self.hiddenWeights
        print "========================================================"
        print self.output
        print "===================== ending ==========================="
        
if __name__ == "__main__":
    net = NeuralNet(3, 5)
    net.printNetwork()
    data = [[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]
    classes = [0, 1, 1, 1]
    
    allCorrect = False
    epsilon = 0.1
    counter = 0
    while not allCorrect:
#        if counter % 1000000 == 0:
        allCorrect = True
        for i in range(len(data)):
            output = net.calculate(data[i])
            if output - classes[i] > epsilon and classes[i] - output > epsilon:
                allCorrect = False
            
            net.learnFromExample(data[i], classes[i])
            counter += 1
            net.printNetwork()
            
        print counter