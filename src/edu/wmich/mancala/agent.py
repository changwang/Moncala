#coding:utf-8
'''
Created on Apr 23, 2010

@author: changwang
'''

from player import RandomPlayer, SimplePlayer, NNPlayer, HumanPlayer

class PlayerAgent(object):
    def __init__(self, type, id):
        self.player = None
        if type.startswith("random"):
            self.player = RandomPlayer(id)
        elif type.startswith("simple"):
            self.player = SimplePlayer(id)
        elif type.startswith("nn"):
            self.player = NNPlayer(id, 6, 4)
        elif type.startswith("human"):
            self.player = HumanPlayer(id)
        else:
            self.player = RandomPlayer(id)
            
    def createPlayer(self):
        return self.player