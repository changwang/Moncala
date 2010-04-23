'''
Created on Apr 23, 2010

@author: changwang
'''

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
        pass