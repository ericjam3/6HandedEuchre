import math

class AI:
    def __init__(self, name, playerIndex, riskLevel):
        self.name = name
        self.playerIndex = playerIndex
        self.riskLevel = riskLevel
        self.suits = ["c", "d", "h", "s"]

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

        highestBidNumber = self.trueRound(highestBidNumber)
        return {"bidNumber": self.finalBidNumber(bidsList, highestBidNumber), "bidType": highestBidType}

    def finalBidNumber(self, bidsList, highestBidNumber):
        for bid in bidsList:
            if bid is None:
                continue

            if int(bid["bidNumber"]) >= highestBidNumber:
                return "0"
            
        return str(int(highestBidNumber))

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
            
        return self.adjustBid(self.getEstimatedTricksHighLow(points, howManyOfEachSuit, bidsList), "high", bidsList)

    def adjustBid(self, baseBidNumber, baseBidType, bidsList):
        sameBids = {"us": 0, "them": 0}
        highBids = {"us": 0, "them": 0}
        nextSuitBids = {"us": 0, "them": 0}

        for i in range(len(bidsList)):
            bid = bidsList[i]

            if bid is None:
                continue

            otherBidNumber = int(bid["bidNumber"])

            if bid["bidType"] == baseBidType:
                if (self.getIndex() % 2) == (i % 2):
                    sameBids["us"] = max(sameBids["us"], otherBidNumber)
                else:
                    sameBids["them"] = max(sameBids["them"], otherBidNumber)

            elif self.isNextSuit(bid["bidType"], baseBidType):
                if (self.getIndex() % 2) == (i % 2):
                    nextSuitBids["us"] = max(nextSuitBids["us"], otherBidNumber)
                else:
                    nextSuitBids["them"] = max(nextSuitBids["them"], otherBidNumber)
                
            if bid["bidType"] == "high":
                if (self.getIndex() % 2) == (i % 2):
                    highBids["us"] = max(highBids["us"], otherBidNumber)
                else:
                    highBids["them"] = max(highBids["them"], otherBidNumber)

        finalBid = baseBidNumber + sameBids["us"] - (sameBids["them"] * .5)
        if baseBidType != "low" and baseBidType != "high":
            finalBid += (highBids["us"] * .4) - (highBids["them"] * .5)
            finalBid += (nextSuitBids["us"] * .25) - (nextSuitBids["them"] * .45)

        if sameBids["us"] > 2:
            finalBid -= (.3 * sameBids["us"])

        return finalBid

    def getEstimatedTricksHighLow(self, points, howManyOfEachSuit, bidsList):
        estimatedTricks = 0

        for key in points:
            pointsInSuit = points[key]

            if pointsInSuit >= 240:
                estimatedTricks += howManyOfEachSuit[key]
            elif pointsInSuit >= 200:
                estimatedTricks += 2
            elif pointsInSuit >= 100:
                if howManyOfEachSuit[key] > 1 or self.howManyPreviousBidders(bidsList) >= 4:
                    estimatedTricks += 1
                else:
                    estimatedTricks += .5

        return estimatedTricks

    def howManyPreviousBidders(self, bidsList):
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
            
        return self.adjustBid(self.getEstimatedTricksHighLow(points, howManyOfEachSuit, bidsList), "low", bidsList)

    def calcSuitBid(self, trump, bidsList, gameState):
        howManyTrump = 0
        howManyOffSuitAces = 0
        points = 0

        for card in self.myCards:
            suit = self.getSuit(card)
            rank = self.getRank(card)

            if suit == trump:
                howManyTrump += 1

                if rank == 11:
                    points += 100
                else:
                    points += 1
            
            elif self.isLeftBower(rank, suit, trump):
                howManyTrump += 1

                points += 40

            elif rank == 14:
                howManyOffSuitAces += 1

        estimatedTricks = self.calcSuitPoints(points, howManyTrump, howManyOffSuitAces)

        return self.adjustBid(estimatedTricks, trump, bidsList)

    def calcSuitPoints(self, points, howManyTrump, howManyOffSuitAces):
        estimatedTricks = 0

        if points >= 280 or (points >= 240 and howManyTrump > 4) or points == 240:
            estimatedTricks = howManyTrump + howManyOffSuitAces
        elif points > 240:
            estimatedTricks = howManyTrump + howManyOffSuitAces - .5
        elif points >= 200:
            estimatedTricks = 2 + (.5 * (howManyTrump - 2)) + (.5 * howManyOffSuitAces) + .1
        elif points >= 180:
            estimatedTricks = 2.5 + (.6 * (howManyTrump - 3)) + (.6 * howManyOffSuitAces) + .1
        elif points >= 140:
            estimatedTricks = 1.5 + (.5 * (howManyTrump - 2)) + (.3 * howManyOffSuitAces)
        elif points >= 100:
            estimatedTricks = 1 + (.5 * (howManyTrump - 1)) + (.3 * howManyOffSuitAces)
        else:
            estimatedTricks = (.5 * howManyTrump) + (.3 * howManyOffSuitAces)

        return estimatedTricks            
        
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
        self.bid = bidInfo
        self.cardsRemaining = {}

        self.initializeCardsRemaining()

        if self.bid["type"] != "high" and self.bid["type"] != "low":
            self.initializeCardsRemainingSuit()
        
    def initializeCardsRemaining(self):
        for suit in suits:
            self.cardsRemaining[suit] = 280
            self.highCards[suit] = suit + "14"

    def initializeCardsRemainingSuit(self):
        trump = self.bid["type"]

        self.cardsRemaining[trump] = 290
        self.highCards[trump] = trump + "11"

    def playCard(self, handState, cardsPlayed, liveCards):
        cardPlayedInfo = {}

        if cardsPlayed == 0:
            card = self.startTrick(handState)
            cardPlayedInfo["cardPlayed"] = card
            cardPlayedInfo["suitLead"] = self.getSuitRespectingTrump(card)
        else:
            cardPlayedInfo["cardPlayed"] = self.chooseCard(handState)

        return cardPlayedInfo

    def startTrick(self, handState):
        if self.bid["type"] == "high":
            self.startTrickHigh()
        elif self.bid["type"] == "low":
            self.startTrickLow()
        else:
            self.startTrickSuit()

    def startTrickHigh(self):
        print("TODO")

    def startTrickLow(self):
        print("TODO")

    def startTrickSuit(self):
        print("TODO")

    def getSuitRespectingTrump(self, card, trump):
        rank = self.getRank(card)
        suit = self.getSuit(card)

        if suit == trump or self.isLeftBower(rank, suit, trump):
            return trump
        
        return suit

    def chooseCard(self, handState):
        print("TODO")

    def recalculateCardsRemaining(self, card):
        if self.bid["type"] == "high":
            self.recalculateHighRemaining(card)
        elif self.bid["type"] == "low":
            self.recalculateLowRemaining(card)
        else:
            self.recalculateSuitRemaining(card, self.bid["type"])

    def recalculateHighRemaining(self, card):
        suit = self.getSuit(card)
        rank = self.getRank(card)

        if rank == 14:
            self.cardsRemaining[suit] -= 100
        elif rank == 13:
            self.cardsRemaining[suit] -= 40

    def recalculateLowRemaining(self, card):
        suit = self.getSuit(card)
        rank = self.getRank(card)

        if rank == 9:
            self.cardsRemaining[suit] -= 100
        elif rank == 10:
            self.cardsRemaining[suit] -= 40

    def recalculateSuitRemaining(self, card, trump):
        suit = self.getSuit(card)
        rank = self.getRank(card)

        if suit == trump:
            if rank == 11:
                self.cardsRemaining[trump] -= 100
            else:
                self.cardsRemaining[trump] -= 1
        
        elif self.isLeftBower(rank, suit, trump):
            self.cardsRemaining[trump] = -40

        else:
            recalculateHighRemaining(card)

    def dropHorse(self):
        print("TODO")

    def passHorse(self):
        print("TODO")

    def trueRound(self, number):
        if (number % 1) > .5:
            return math.ceil(number)
        else:
            return math.floor(number)