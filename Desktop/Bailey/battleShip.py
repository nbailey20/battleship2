# battleShip.py
#
# author: Nick Bailey, 12/24/2014
#
# defines a battleship game node, implements
# probability density search for coordinate that is most likely a ship

from random import randrange

class Battleship :
    boardLetters = "ABCDEFGHIJ"
    boardNumbers = " 1 2 3 4 5 6 7 8 9 10 "

    def __init__ (self, width, height) :
        self.width = width
        self.height = height
        WIDTH = self.width
        HEIGHT = self.height
        self.data = [ ["."]*WIDTH for row in range(HEIGHT) ]
        self.legalMoves()
        self.ships = [2, 3, 3, 4, 5]
        self.bestMove()
        ## also have self.moves, defined in legalMoves(self)


    def __repr__(self):
        """creates a string representation of the board, which is now thankfully a list"""
        WIDTH = self.width
        HEIGHT = self.height
        let = Battleship.boardLetters
        board = "  " + Battleship.boardNumbers[0:21] + "\n"
        for row in range(HEIGHT):
            board += let[row:row+1] + " |"
            for col in range(WIDTH):
                board += self.data[row][col] + "|"
            board += "\n"
        return board
        

    def move(self, symbol, col) :
        # make move of form 'A3', then reset available moves
        row = ord(symbol) % 65
        self.data[row][int(col) - 1] = "X"       
        self.legalMoves()




    def legalMoves(self) :
        # sets list of empty positions, self.moves
        moves = []
        WIDTH = self.width
        for row in range(len(self.data)):
            for col in range(len(self.data[0])):
                if (self.data[row][col] == "."):
                    moves += [(row * WIDTH + col)]

        self.moves = moves


    def allowsMove(self, symbol, col):
        # checks to see whether a desired move is allowed
        row = ord(symbol) % 65
        WIDTH = self.width
        for i in range(len(self.moves)):
            if (self.moves[i] == int(row * WIDTH + (col - 1))):
                return True
        else:
            return False
        


 
 
    def playGame(self):
        """hosts a rather lopsided version of battleship """
        
        print
        print "Let's fuck some shit up... \n"
        print self
        print
        
        gameType = raw_input("Want to play Manual or Guided? : ")  # choose where you shoot, or apply algorithm
         
        if gameType == "Manual":
            while True:
                if (len(self.moves) == 0):
                    print "Game over, there are no more moves!"
                    break
                nextMove = raw_input("Next move: ").split(',')
                
                while (self.allowsMove(nextMove[0], int(nextMove[1])) == False):
                    nextMove = raw_input("Nice try. Next move: ").split(',')
            
                self.move(nextMove[0], nextMove[1])
                print
                print self
                print


        if gameType == "Guided":
 
            while True:
                if len(self.moves) == 0 or len(self.ships) == 0:
                    print "Game over."
                    break
                print "Enter moves such as G,6, and when you are done, enter Z "
                print
                nextMove = raw_input("Next move: ").split(',')

                if nextMove[0] == "Z":
                
                    while True:
                        if len(self.moves) == 0:
                            print "Well I assume you lost..."
                            break

                        ## algorithm called:
                        self.bestMove()
                        symbol = self.convertNumtoMove(self.bestMove()[0], self.bestMove()[1])[0]
                        col = self.convertNumtoMove(self.bestMove()[0], self.bestMove()[1])[1:]


                        ## provide user with best move and information about the move
                        print "I recommend you make this move: " + symbol + col
                        print "It has a shipCount of: " + str(self.bestMove()[2])
                        print

                        #conditionals in case there aren't any more moves for specific ship types
                        if self.bestMove()[4] == 0:
                            print "Length 2 Boat chance: NA"
                        else:
                            print "Length 2 Boat chance: " + \
                                  str((float(self.bestMove()[8]) / float(self.bestMove()[4] / 2)) * 100) + "%"
                        if self.bestMove()[5] == 0:
                            print "Length 3 Boat chance: NA"
                        else:
                            print "Length 3 Boat chance: " + \
                                  str((float(self.bestMove()[9]) / float(self.bestMove()[5] / 3)) * 100) + "%"
                        if self.bestMove()[6] == 0:
                            print "Length 4 Boat chance: NA"
                        else:
                            print "Length 4 Boat chance: " + \
                                  str((float(self.bestMove()[10]) / float(self.bestMove()[6] / 4)) * 100) + "%"
                        if self.bestMove()[7] == 0:
                            print "Length 5 Boat chance: NA"
                        else:
                            print "Length 5 Boat chance: " + \
                                  str((float(self.bestMove()[11]) / float(self.bestMove()[7] / 5)) * 100) + "%"
                            
                        print "Chance of hitting ANY ship: "+ \
                              str((float(self.bestMove()[2]) / self.bestMove()[3]) * 100) + "%"
        
                        hitShip = raw_input("Keep guiding? y/n/sunk: ")
                        if (hitShip == "n"):
                            break
                        if (hitShip == "sunk"):
                            shipType = int(raw_input("What was the length of the sunken ship (ie 3)? :"))
                            self.removeShip(shipType)
                            print "Ships left: "
                            print self.ships
                            break
                        self.move(symbol, col)
                        print
                        print self
                        print

                else:

                    while (self.allowsMove(nextMove[0], int(nextMove[1])) == False):
                        nextMove = raw_input("Nice try. Next move: ").split(',')
            
                    self.move(nextMove[0], nextMove[1])
                    print
                    print self
                    print
                
                
                    
                             



    def bestMove(self):
        """algorithm to calculate the best "guessing" move of a battleship
           game (when ship locations aren't known)"""
        WIDTH = self.width
        HEIGHT = self.height
        
        bestSoFar = [0, 0, 0] # holds [row,col,shipCount, totalCount] of the highest shipCount cell thus far
        totalCount = 0  # cumulative shipCount for all cells, used to calculate probability
        totTwoShipCount = 0   # cumulative shipCount for ships of particular size, used for individual probabilities
        totThreeShipCount = 0
        totFourShipCount = 0
        totFiveShipCount = 0

        for row in range(HEIGHT):
                for col in range(WIDTH):
                    if (self.data[row][col] == "."):  # only look at open cells
                        shipCount = 0
                        neighbors = self.cellNeighbors(row, col)
                        twoAway = self.twoAway(row, col)
                        threeAway = self.threeAway(row,col)
                        fourAway = self.fourAway(row, col)
        
                        ## size 2 ship
                        twoShipCount = 0
                        # check if there are size 2 ships left in play
                        if self.shipInPlay(2) == True:
                            # loop through neighbors, every open neighbor adds to shipCount
                            for i in range(len(neighbors)):
                                if neighbors[i] != "-":
                                    shipCount += 1  # every open neighbor adds to size_2 shipCount
                                    totTwoShipCount += 1
                                    twoShipCount += 1
                            totalCount += float(twoShipCount) / 2 # compensate for double counting

                                    

                        ## size 3 ships
                        threeShipCount = 0
                        if self.shipInPlay(3) == True:
                            for j in range(len(neighbors)):
                                if neighbors[j] == twoAway[j] and neighbors[j] != "-": # end of ship could be at current cell
                                    threeShipCount += 1

                            # if the current cell is instead the middle of the ship
                            if neighbors[0] != "-" and neighbors[3] != "-": 
                                threeShipCount += 1
                            if neighbors[1] != "-" and neighbors[2] != "-":
                                threeShipCount += 1

                            shipCount += threeShipCount
                            totalCount += (float(threeShipCount) / 3)
                            totThreeShipCount += (float(threeShipCount))
                        
                            




                        ## size 4 ships
                        fourShipCount = 0
                        if self.shipInPlay(4) == True:
                            for k in range(len(neighbors)):       # check if end of ship could be at current cell first
                                if neighbors[k] == twoAway[k] and neighbors[k] == threeAway[k] and neighbors[k] != "-":
                                    shipCount += 1
                                    totFourShipCount += 1
                                    fourShipCount += 1

                            # check if middle of ship could be at current cell
                            if neighbors[0] != "-" and neighbors[3] != "-" and twoAway[0] != "-":
                                shipCount += 1
                                totFourShipCount += 1
                                fourShipCount += 1
                            if neighbors[0] != "-" and neighbors[3] != "-" and twoAway[3] != "-":
                                shipCount += 1
                                totFourShipCount += 1
                                fourShipCount += 1

                            if neighbors[1] != "-" and neighbors[2] != "-" and twoAway[1] != "-":
                                shipCount += 1
                                totFourShipCount += 1
                                fourShipCount += 1
                            if neighbors[1] != "-" and neighbors[2] != "-" and twoAway[2] != "-":
                                shipCount += 1
                                totFourShipCount += 1
                                fourShipCount += 1
                                
                            totalCount += float(fourShipCount) / 4





                        ## size 5 ships
                        fiveShipCount = 0
                        if self.shipInPlay(5) == True:
                            for n in range(len(neighbors)):
                                if neighbors[n] == twoAway[n] and neighbors[n] == threeAway[n] and \
                                                   neighbors[n] == fourAway[n] and neighbors[n] != "-":
                                    shipCount += 1
                                    totFiveShipCount += 1
                                    fiveShipCount += 1

                            if neighbors[0] != "-" and neighbors[3] != "-" and twoAway[0] != "-" and twoAway[3] != "-":
                                shipCount += 1
                                totFiveShipCount += 1
                                fiveShipCount += 1
                            if neighbors[0] != "-" and neighbors[3] != "-" and twoAway[0] != "-" and threeAway[0] != "-":
                                shipCount += 1
                                totFiveShipCount += 1
                                fiveShipCount += 1
                            if neighbors[0] != "-" and neighbors[3] != "-" and twoAway[3] != "-" and threeAway[3] != "-":
                                shipCount += 1
                                totFiveShipCount +=1
                                fiveShipCount += 1

                            if neighbors[1] != "-" and neighbors[2] != "-" and twoAway[1] != "-" and twoAway[2] != "-":
                                shipCount += 1
                                totFiveShipCount += 1
                                fiveShipCount += 1
                            if neighbors[1] != "-" and neighbors[2] != "-" and twoAway[1] != "-" and threeAway[1] != "-":
                                shipCount += 1
                                totFiveShipCount += 1
                                fiveShipCount += 1
                            if neighbors[1] != "-" and neighbors[2] != "-" and twoAway[2] != "-" and threeAway[2] != "-":
                                shipCount += 1
                                totFiveShipCount += 1
                                fiveShipCount += 1

                            totalCount += float(fiveShipCount) / 5


                        # if new best shipCount, save the cell as the best move thus far!
                        if shipCount > bestSoFar[2]:
                            bestSoFar = [row, col, shipCount, twoShipCount, threeShipCount, \
                                         fourShipCount, fiveShipCount]
                            
                        elif shipCount == bestSoFar[2]:
                            split = randrange(0,1)
                            if split == 0:
                                bestSoFar = [row, col, shipCount, twoShipCount, threeShipCount, \
                                         fourShipCount, fiveShipCount]
                        
                            
        bestResult = [bestSoFar[0], bestSoFar[1], bestSoFar[2], totalCount, totTwoShipCount, \
                      totThreeShipCount, totFourShipCount, totFiveShipCount, bestSoFar[3], \
                      bestSoFar[4], bestSoFar[5], bestSoFar[6]]
        return bestResult
                                    
                                    
                                     
            
                        
            
            





    def shipInPlay(self, size):
        """helper function for bestMove, determines whether a ship of length 'size' is still in play"""
        for i in range(len(self.ships)):
            if self.ships[i] == size:
                return True
        return False



    def cellNeighbors(self, row, col):
        """returns a string of the form "NEWS", or "----", where letters are when the
           cell has an open neighbor in the given direction"""
        WIDTH = self.width
        HEIGHT = self.height
        result = ""

        ## north neighbor
        if row == 0:
            result += "-"
        elif self.data[row - 1][col] == "X":
            result += "-"
        else:
            result += "N"


        ## east neighbor
        if col == WIDTH-1:
            result += "-"
        elif self.data[row][col + 1] == "X":
            result += "-"
        else:
            result += "E"


        ## west neighbor
        if col == 0:
            result += "-"
        elif self.data[row][col - 1] == "X":
            result += "-"
        else:
            result += "W"



        ## south neighbor
        if row == HEIGHT-1:
            result += "-"
        elif self.data[row + 1][col] == "X":
            result += "-"
        else:
            result += "S"


        return result



    def twoAway(self, row, col):
        """same as cellNeighbors, except now looking two cells
           away instead of 1 in each direction"""
    
        WIDTH = self.width
        HEIGHT = self.height
        result = ""

        ## north 
        if row == 0 or (row - 1) == 0:
            result += "-"
        elif self.data[row - 2][col] == "X":
            result += "-"
        else:
            result += "N"


        ## east 
        if col == WIDTH-1 or col == WIDTH - 2:
            result += "-"
        elif self.data[row][col + 2] == "X":
            result += "-"
        else:
            result += "E"


        ## west 
        if col == 0 or col == 1:
            result += "-"
        elif self.data[row][col - 2] == "X":
            result += "-"
        else:
            result += "W"



        ## south 
        if row == HEIGHT-1 or row == HEIGHT - 2:
            result += "-"
        elif self.data[row + 2][col] == "X":
            result += "-"
        else:
            result += "S"


        return result




    def threeAway(self, row, col):
        """same as above, looking three cells away"""
        WIDTH = self.width
        HEIGHT = self.height
        result = ""

        ## north 
        if row == 0 or (row - 1 == 0) or (row - 2 == 0):
            result += "-"
        elif self.data[row - 3][col] == "X":
            result += "-"
        else:
            result += "N"


        ## east 
        if col == WIDTH-1 or col == WIDTH - 2 or col == WIDTH - 3:
            result += "-"
        elif self.data[row][col + 3] == "X":
            result += "-"
        else:
            result += "E"


        ## west 
        if col == 0 or col == 1 or col == 2:
            result += "-"
        elif self.data[row][col - 3] == "X":
            result += "-"
        else:
            result += "W"



        ## south 
        if row == HEIGHT-1 or row == HEIGHT - 2 or row == HEIGHT - 3:
            result += "-"
        elif self.data[row + 3][col] == "X":
            result += "-"
        else:
            result += "S"


        return result

        
    
    
    
        
    def fourAway(self, row, col):
        """same as above, looking four cells away"""
        WIDTH = self.width
        HEIGHT = self.height
        result = ""

        ## north 
        if row == 0 or (row - 1 == 0) or (row - 2 == 0) or (row - 3 == 0):
            result += "-"
        elif self.data[row - 4][col] == "X":
            result += "-"
        else:
            result += "N"


        ## east 
        if col == WIDTH-1 or col == WIDTH - 2 or col == WIDTH - 3 or col == WIDTH - 4:
            result += "-"
        elif self.data[row][col + 4] == "X":
            result += "-"
        else:
            result += "E"


        ## west 
        if col == 0 or col == 1 or col == 2 or col == 3:
            result += "-"
        elif self.data[row][col - 4] == "X":
            result += "-"
        else:
            result += "W"



        ## south 
        if row == HEIGHT-1 or row == HEIGHT - 2 or row == HEIGHT - 3 or row == HEIGHT - 4:
            result += "-"
        elif self.data[row + 4][col] == "X":
            result += "-"
        else:
            result += "S"


        return result




    def convertNumtoMove(self, row, col):
        """take a row and col and converts the numbers into
           standard battleship coordinates, ie "G",6, etc"""
        result = ""
        symbol = chr(row + 65)
        result += symbol
        result += str(col + 1)
        return result



    def removeShip(self, shipType):
        """removes the specified ship length from the list of stored ships,
           which are taken into account by the algorithm"""
        for i in range(len(self.ships)):
            if self.ships[i] == shipType:
                if i == len(self.ships) - 1:
                    self.ships = self.ships[:i]
                    break
                else:
                    self.ships = self.ships[:i] + self.ships[i+1:]
                    break


    def numThreeShips(self):
        """ returns the number of ships of length 3 still in play"""
        threeCount = 0
        for i in range(len(self.ships)):
            if self.ships[i] == 3:
                threeCount += 1
        return threeCount
                
 
        

