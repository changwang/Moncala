#coding:utf-8
'''
Created on Apr 23, 2010

@author: changwang
'''

import math

DELTA = 0.1 # learning rate

class NeuralNet(object):
    def __init__(self, input_size, hidden_size):
        self.setupNetwork(input_size, hidden_size)
    
    def setupNetwork(self, input_size, hidden_size):
        """ set up the network by the given input and hidden layer number """
        self.inputSize = input_size
        self.hiddenSize = hidden_size
         
        self.input = [0.0] * input_size # value of input node
        self.input.append(1.0)   # bias for hidden layer
        
        self.hidden = [0.0] * hidden_size   # value of hidden node
        self.hidden.append(1.0)  # bias for output layer
        self.weights = [0.0] * (hidden_size + 1)    # weight of hidden to output node
        
        self.hiddenWeights = {}   # two dimensional array, weight of input to hidden node
        for i in range(input_size+1):
            self.hiddenWeights[i] = [0.0] * (hidden_size + 1)
        
        self.output = 0.0   # value of output node
    
    def calculate(self, example):
        """ Calculate the output of the given input """
        self.input[:len(example)] = example[:]    # copy example input
        
        # calculate hidden layer
        for i in range(self.hiddenSize):
            self.hidden[i] = 0.0
            for j in range(self.inputSize+1):
                self.hidden[i] += self.input[j] * self.hiddenWeights[j][i]
            self.hidden[i] = self.sigmoid(self.hidden[i])
        
        for i in range(self.hiddenSize+1):
            self.output += self.hidden[i] * self.weights[i]
            
        return self.output
    
    def learnFromExample(self, example, desired):
        """ update weights to better approximate given example """
        result = float(self.calculate(example))
        err = float(desired) - result
        for i in range(self.hiddenSize+1):
            errN = float(err * self.weights[i] * (1 - self.hidden[i]) * self.hidden[i])
            for j in range(self.inputSize+1):
                self.hiddenWeights[j][i] += DELTA * errN * self.input[j]
        
        for i in range(self.hiddenSize+1):
            self.weights[i] += DELTA * err * self.hidden[i]
            
    def sigmoid(self, x):
        """ non-linear function for hidden layer """
        return float(1.0) / (1 + math.exp(-x))
    
    def saveToFile(self, filename, mode):
        """ saves network weights to specified file """
        f = open(filename, mode)
        f.write(str(self.inputSize)+"\n")
        f.write(str(self.hiddenSize)+"\n")
        for i in self.weights:
            f.write(str(i)+',')
        f.write("\n")
        for key in iter(self.hiddenWeights):
            for weight in self.hiddenWeights[key]:
                f.write(str(weight)+',')
            f.write('\n')
        f.flush()
        f.close()
        
    def loadFromFile(self, filename):
        """ initialize the network from weights given by specified file """
        f = open(filename, 'r')
        inSize = int(f.readline())
        hiSize = int(f.readline())
        self.setupNetwork(inSize, hiSize)
        wts = f.readline().split(',')
        self.weights = [float(w) for w in wts[:-1]]
        for i in range(self.inputSize+1):
            hwts = f.readline().split(',')
            self.hiddenWeights[i] = [float(hw) for hw in hwts[:-1]]
        f.close()
    
    def printNetwork(self):
        """ print network state """
        print "==================== beginning ========================="
        print
        print self.input
        print
        print "=================== input to hidden ===================="
        print
        for key in iter(self.hiddenWeights):
            print self.hiddenWeights[key]
        print
        print "=================== hidden layer nodes ================="
        print
        print self.hidden
        print
        print "================ hidden to output layer ================"
        print
        print self.weights
        print
        print "==================== output layer ======================"
        print
        print self.output
        print
        print "===================== ending ==========================="
        
if __name__ == "__main__":
    net = NeuralNet(3, 5)
    net.loadFromFile('weights.txt')
    net.printNetwork()
#    net.printNetwork()
#    data = [[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]
#    classes = [0, 1, 1, 1]
#    
#    allCorrect = False
#    epsilon = 0.1
#    counter = 0
#    while not allCorrect:
##        if counter % 1000000 == 0:
#        allCorrect = True
#        for i in range(len(data)):
#            output = net.calculate(data[i])
#            if output - classes[i] > epsilon and classes[i] - output > epsilon:
#                allCorrect = False
#            
#            net.learnFromExample(data[i], classes[i])
#            counter += 1
#            
#    net.printNetwork()
#    net.saveToFile('weights.txt')
#    