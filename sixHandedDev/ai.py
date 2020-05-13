class AI:
    def __init__(self, name, playerIndex, riskLevel):
        self.name = name
        self.playerIndex = playerIndex
        self.riskLevel = riskLevel

    def getName(self):
        return self.name

    def getIndex(self):
        return self.playerIndex

    def dealCards(self, cards):
        self.hand = cards

    def tryBidding(self, bidsList, gameState):
        print("TODO")

    def startHand(self, bidInfo):
        print("TODO")

    def playCard(self, handState, cardsPlayed):
        print("TODO")

    def dropHorse(self):
        print("TODO")

    def passHorse(self):
        print("TODO")

    

    
    