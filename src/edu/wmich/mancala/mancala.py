#coding:utf-8
'''
Created on Apr 23, 2010

@author: changwang
'''

class Pit(object):
    def __init__(self, player, isMancala, stones=4):
        self.player = player
        self.isMancala = isMancala
        if self.isMancala:
            self.stones = 0
        else:
            self.stones = stones
        self.clockwise = None
        self.counterclock = None
        self.across = None
    
    def pickup(self):
        """ remove all stones from current pit """
        tmp = self.stones
        self.stones = 0
        return tmp
    
    def drop(self):
        """ drop a stone into current pit """
        self.stones += 1
        
    def dropAll(self, stones):
        """ drop a handful of stones into current pit """
        self.stones += stones
    
    def isMyMancala(self, player):
        return (self.player == player) and self.isMancala
    
    def isOppMancala(self, player):
        return (self.player != player) and self.isMancala
    
    def isPlayersPit(self, player):
        return (self.player == player) and (not self.isMancala)

class MancalaBoard(object):
    def __init__(self, rowSize=6, stonePerPit=4):
        self.rowSize = rowSize
        self.stonePerPit = stonePerPit
        
        self.board = {} # FIXME
        self.bottom = []
        self.top = []
        
        self.mancala = {} # 2 mancala for each player
        self.topMancala = None
        self.bottomMancala = None
        
        self.resetBoard()
        
    def resetBoard(self):
        self.bottomMancala = Pit(0, True, 0)
        self.topMancala = Pit(1, True, 0)
        for i in range(self.rowSize):
            self.top.append(Pit(1, False, self.stonePerPit))
            self.bottom.append(Pit(0, False, self.stonePerPit))
        
        self.board[0] = self.bottom
        self.board[1] = self.top
        
        self.mancala[0] = self.bottomMancala
        self.mancala[1] = self.topMancala
        
        self.top[0].clockwise = self.bottomMancala
        self.bottomMancala.counterclock = self.top[0]
        self.bottom[0].clockwise = self.topMancala
        self.topMancala.counterclock = self.bottom[0]
        
        self.top[-1].counterclock = self.topMancala
        self.topMancala.clockwise = self.top[-1]
        self.bottom[-1].counterclock = self.bottomMancala
        self.bottomMancala.clockwise = self.bottom[-1]
        
        self.topMancala.across = self.bottomMancala
        self.bottomMancala.across = self.topMancala
        
        for i in range(self.rowSize):
            self.top[i].across = self.bottom[self.rowSize-1-i]
            self.bottom[i].across = self.top[self.rowSize-1-i]
            if i != (self.rowSize - 1):
                self.top[i].counterclock = self.top[i+1]
                self.bottom[i].counterclock = self.bottom[i+1]
            if i != 0:
                self.top[i].clockwise = self.top[i-1]
                self.bottom[i].clockwise = self.bottom[i-1]
    
    def mySide(self, player):
        side = []
        for i in range(self.rowSize):
            side.append(self.board[player][i].stones)
        return side
    
    def oppSide(self, player):
        side = []
        for i in range(self.rowSize):
            side.append(self.board[(player+1)%2][i].stones)
        return side
    
    def stonesInMyMancala(self, player):
        return self.mancala[player].stones
    
    def stonesInOppMancala(self, player):
        return self.mancala[(player+1)%2].stones
        
    def playPit(self, player, pitnum):
        pit = self.board[player][pitnum]
        if pit.stones == 0:
            return True
        for s in range(pit.pickup()):
            pit = pit.counterclock
            if pit.isOppMancala(player):
                pit = pit.clockwise
            pit.drop()
            
        if pit.stones == 1 and pit.isPlayersPit(player) and pit.across.stones > 0:
            self.mancala[player].dropAll(pit.pickup() + pit.across.pickup())
            
        if pit.isMyMancala(player):
            return True
        else:
            return False
        
    def inPlay(self, player):
        num = 0
        for i in range(self.rowSize):
            num += self.board[player][i].stones
        return num
    
    def isGameOver(self):
        plays = [self.inPlay(0), self.inPlay(1)]
        if plays[0] == 0 or plays[1] == 0:
            self.bottomMancala.dropAll(plays[0])
            self.topMancala.dropAll(plays[1])
            for i in range(self.rowSize):
                self.top[i].pickup()
                self.bottom[i].pickup()
            return True
        return False
    
    def winner(self):
        if self.stonesInMyMancala(0) > self.stonesInMyMancala(1):
            return 0
        elif self.stonesInMyMancala(0) < self.stonesInMyMancala(1):
            return 1
        else:
            return -1
        
    def printBoard(self):
        print "    index   ||      ||(6)||(5)||(4)||(3)||(2)||(1)||      ||"
        print "            ||============================================||"
        print "            ||      || " + str(self.top[5].stones) + " || " + str(self.top[4].stones) + " || " + str(self.top[3].stones) + " || " + str(self.top[2].stones) + " || " + str(self.top[1].stones) + " || " + str(self.top[0].stones) + " || " + "     ||"
        print "Opponent →  ||   " + str(self.topMancala.stones) + "  ||============================||   " + str(self.bottomMancala.stones)  + "  || ← You"
        print "            ||      || " + str(self.bottom[0].stones) + " || " + str(self.bottom[1].stones) + " || " + str(self.bottom[2].stones) + " || " + str(self.bottom[3].stones) + " || " + str(self.bottom[4].stones) + " || " + str(self.bottom[5].stones) + " || " + "     ||"
        print "            ||============================================||"
        print "    index   ||      ||(1)||(2)||(3)||(4)||(5)||(6)||      ||"
        
if __name__ == '__main__':
    board = MancalaBoard()
    
    move = 0
    while not board.isGameOver():
        getsTurn = True
        while getsTurn:
            board.printBoard()
            if board.isGameOver():
                break
            move = int(raw_input("Player one's turn, move is: "))
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
            move = int(raw_input("Player two's turn, move is: "))
            if move > 6 or move < 1:
                continue
            getsTurn = board.playPit(1, move - 1)
        if board.isGameOver():
            break

    if board.winner() == 0:
        print "Player one won"
    elif board.winner() == 1:
        print "Player two won"
    else:
        print "It is a tie"