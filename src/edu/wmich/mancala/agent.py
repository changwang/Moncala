'''
Created on Apr 23, 2010

@author: changwang
'''

from player import *

class PlayerAgent(object):
    def __init__(self, type, id):
        self.player = None
        if type.startswith("random"):
            self.player = RandomPlayer(id)
        elif type.startswith("simple"):
            self.player = SimplePlayer(id)
        elif type.startswith("nn"):
            self.player = NNPlayer(id, 6, 4)
            
            
    def createPlayer(self):
        return self.player
    
if __name__ == '__main__':
    player1 = PlayerAgent('nn').createPlayer()
    player2 = PlayerAgent('nn').createPlayer()
    
    nnTrainning = False