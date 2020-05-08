import dataModel

def setVars():
    dataModel.players = [1,2,3,4,5,6]
    dataModel.numPlayers = 8
    dataModel.dealer = 4
    dataModel.cardsPlayed = 5

def printVars():
    print(dataModel.players, dataModel.numPlayers, dataModel.dealer, dataModel.cardsPlayed)



if __name__ == '__main__':
    array = [None] * 6
    array[5] = 1
    print(array)