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
            
        return self.adjustBid(self.getEstimatedTricksHighLow(points, howManyOfEachSuit), "high", bidsList)

    def adjustBid(self, baseBidNumber, baseBidType, bidsList):
        sameBids = {"us": 0, "them": 0}
        highBids = {"us": 0, "them": 0}
        nextSuitBids = {"us": 0, "them": 0}

        for i in range(len(bidsList)):
            bid = bidsList[i]

            if bid is None:
                continue

            if bid["bidType"] == baseBidType:
                if (self.getIndex() % 2) == (i % 2):
                    sameBids["us"] = max(sameBids["us"], bid["bidNumber"])
                else:
                    sameBids["them"] = max(sameBids["them"], bid["bidNumber"])

            elif self.isNextSuit(bid["bidType"], baseBidType):
                if (self.getIndex() % 2) == (i % 2):
                    nextSuitBids["us"] = max(nextSuitBids["us"], bid["bidNumber"])
                else:
                    nextSuitBids["them"] = max(nextSuitBids["them"], bid["bidNumber"])
                
            if bid["bidType"] == "high":
                if (self.getIndex() % 2) == (i % 2):
                    highBids["us"] = max(highBids["us"], bid["bidNumber"])
                else:
                    highBids["them"] = max(highBids["them"], bid["bidNumber"])

        finalBid = baseBidNumber + sameBids["us"] - (sameBids["them"] * .5)
        if baseBidType != "low" and baseBidType != "high":
            finalBid += (highBids["us"] * .4) - (highBids["them"] * .5)
            finalBid += (nextSuitBids["us"] * .25) - (nextSuitBids["them"] * .45)

        if sameBids["us"] > 2:
            finalBid -= (.3 * sameBids["us"])

        return finalBid

    def getEstimatedTricksHighLow(self, points, howManyOfEachSuit):
        estimatedTricks = 0

        for key in points:
            pointsInSuit = points[key]

            if pointsInSuit >= 240:
                estimatedTricks += howManyOfEachSuit[key]
            elif pointsInSuit > 200:
                estimatedTricks += 2
            elif pointsInSuit > 100:
                if howManyOfEachSuit[key] > 1 or howManyPreviousBidders(bidsList) >= 4:
                    estimatedTricks += 1
                else:
                    estimatedTricks += .5

        return estimatedTricks

    def howManyPreviousBidders(bidsList):
        numBidders = 0

        for bid in bidsList:
            if bid is not None:
                numBidders += 1

        return numBidders

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
            
        return self.adjustBid(self.getEstimatedTricksHighLow(points, howManyOfEachSuit), "low", bidsList)

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
                estimatedTricks += .4

        return self.adjustBid(estimatedTricks, trump, bidsList)
        
    def isLeftBower(self, rank, suit, trump):
        if rank != 11:
            return False

        return self.isNextSuit(suit, trump)

    def isNextSuit(self, suit, trump):
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