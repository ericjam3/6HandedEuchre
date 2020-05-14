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
        self.myCards = cards

    def tryBidding(self, bidsList, gameState):
        highestBidType = "high"
        highestBidNumber = self.calcHighBid(bidsList, gameState)

        clubsBid = self.calcSuitBid("c", bidsList, gameState)
        if clubsBid > highestBidNumber:
            highestBidType = "c"
            highestBidNumber = clubsBid

        diamondsBid = self.calcSuitBid("d", bidsList, gameState)
        if diamondsBid > highestBidNumber:
            highestBidType = "d"
            highestBidNumber = diamondsBid

        heartsBid = self.calcSuitBid("h", bidsList, gameState)
        if heartsBid > highestBidNumber:
            highestBidType = "h"
            highestBidNumber = heartsBid

        spadesBid = self.calcSuitBid("s", bidsList, gameState)
        if spadesBid > highestBidNumber:
            highestBidType = "s"
            highestBidNumber = spadesBid

        lowBid = self.calcLowBid(bidsList, gameState)
        if lowBid > highestBidNumber:
            highestBidType = "low"
            highestBidNumber = lowBid

        return {"bidNumber": round(highestBidNumber), "bidType": highestBidType}

    def calcHighBid(self, bidsList, gameState):
        howManyOfEachSuit = {"c": 0, "d": 0, "h": 0, "s": 0}
        points = {"c": 0, "d": 0, "h": 0, "s": 0}

        for card in self.myCards:
            suit = self.getSuit(card)
            rank = self.getRank(card)

            howManyOfEachSuit[suit] += 1
            
            if rank == 14:
                points[suit] += 100
            elif rank == 13:
                points[suit] += 40
            else:
                points[suit] += 1
            
        return getEstimatedTricksHighLow(points, howManyOfEachSuit)

    def getEstimatedTricksHighLow(points, howManyOfEachSuit):
        estimatedTricks = 0

        for key in points:
            pointsInSuit = points[key]

            if pointsInSuit >= 240:
                estimatedTricks += howManyOfEachSuit[key]
            elif pointsInSuit > 200:
                estimatedTricks += 2
            elif pointsInSuit > 100:
                if howManyOfEachSuit[key] > 1 or len(bidsList) > 4:
                    estimatedTricks += 1
                else:
                    estimatedTricks += .5

        return estimatedTricks

    def getSuit(self, card):
        return card[0:1]

    def getRank(self, card):
        return int(card[1:])

    def calcLowBid(self, bidsList, gameState):
        howManyOfEachSuit = {"c": 0, "d": 0, "h": 0, "s": 0}
        points = {"c": 0, "d": 0, "h": 0, "s": 0}

        for card in self.myCards:
            suit = self.getSuit(card)
            rank = self.getRank(card)

            howManyOfEachSuit[suit] += 1

            if rank == 9:
                points[suit] += 100
            elif rank == 10:
                points[suit] += 40
            else:
                points[suit] += 1
            
        return getEstimatedTricksHighLow(points, howManyOfEachSuit)

    def calcSuitBid(self, trump, bidsList, gameState):
        estimatedTricks = 0

        for card in self.myCards:
            suit = self.getSuit(card)
            rank = self.getRank(card)

            if suit == trump:
                if rank == 11:
                    estimatedTricks += 1
                else:
                    estimatedTricks += .5
            
            elif self.isLeftBower(rank, suit, trump):
                estimatedTricks += .75

            elif rank == 14:
                estimatedTricks += .45

        return estimatedTricks
        
    def isLeftBower(self, rank, suit, trump):
        if rank != 11:
            return False

        if suit == "c" and trump == "s":
            return True
        elif suit == "d" and trump == "h":
            return True
        elif suit == "h" and trump == "d":
            return True
        elif suit == "s" and trump == "c":
            return True

        return False

    def startHand(self, bidInfo):
        print("TODO")

    def playCard(self, handState, cardsPlayed):
        print("TODO")

    def dropHorse(self):
        print("TODO")

    def passHorse(self):
        print("TODO")

    

    
    