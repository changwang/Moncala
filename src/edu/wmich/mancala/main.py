'''
Created on Apr 26, 2010

@author: changwang
'''
from neuralnet import MancalaBoard
from agent import PlayerAgent
  
if __name__ == '__main__':
    board = MancalaBoard()
    
    player0 = PlayerAgent('human', 0).createPlayer()
    player1 = PlayerAgent('nn', 1).createPlayer()
    
    move = 0
    while not board.isGameOver():
        getsTurn = True
        while getsTurn:
            board.printBoard()
            if board.isGameOver():
                break
            print
            #move = int(raw_input("It's your turn, move is: "))
            
            move = player0.getMove(board)
            print "It's your turn, move is: " + str(move)
            print
            print "---------------------------- seperator ----------------------------"
            print
            if move > 6 or move < 1:
                continue
            getsTurn = board.playPit(0, move - 1)
            
        if board.isGameOver():
            break
        getsTurn = True
        while getsTurn:
            board.printBoard()
            if board.isGameOver():
                break
            print
            #move = int(raw_input("It's neural network's turn, move is: "))
            move = player1.getMove(board)
            print "It's neural network's turn, move is: " + str(move)
            print
            print "---------------------------- seperator ----------------------------"
            print
            if move > 6 or move < 1:
                continue
            getsTurn = board.playPit(1, move - 1)
        if board.isGameOver():
            break

    if board.winner() == 0:
        print "You beat the neural network, WOW!"
    elif board.winner() == 1:
        print "The neural network beats you! :("
    else:
        print "It is a tie"