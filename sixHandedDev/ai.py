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

#############################################################################

    def startHand(self, bidInfo):
        self.bid = bidInfo
        self.cardsRemaining = {}

        self.initializeCardsRemaining()

        if self.bid["type"] != "high" and self.bid["type"] != "low":
            self.initializeCardsRemainingSuit()
        
    def initializeCardsRemaining(self):
        self.highCards = {}
        for suit in self.suits:
            self.cardsRemaining[suit] = 280
            self.highCards[suit] = suit + "14"

    def initializeCardsRemainingSuit(self):
        trump = self.bid["type"]

        self.cardsRemaining[trump] = 290
        self.highCards[trump] = trump + "11"

    def playCard(self, handState, cardsPlayed, trickInfo):
        cardPlayedInfo = {}

        if cardsPlayed == 0:
            card = self.startTrick(handState)
            cardPlayedInfo["cardPlayed"] = card
            cardPlayedInfo["suitLead"] = self.getSuitRespectingTrump(card, self.bid["type"])
        else:
            cardPlayedInfo["cardPlayed"] = self.chooseCard(handState, trickInfo)

        self.removePlayedCard(cardPlayedInfo["cardPlayed"])
        return cardPlayedInfo

    def removePlayedCard(self, card):
        self.myCards.remove(card)

    def startTrick(self, handState):
        if self.bid["type"] == "high":
            return self.startTrickHigh()
        elif self.bid["type"] == "low":
            return self.startTrickLow()
        else:
            return self.startTrickSuit(self.bid["type"])

    def startTrickHigh(self):
        bestLead = self.checkAcesNines(14)
        if bestLead is not None:
            return bestLead

        bestLead = self.checkRunner(13, True)

        if bestLead is not None:
            return bestLead

        return self.getWorstCardTrumpHigh()

    def checkAcesNines(self, bestRank):
        for card in self.myCards:
            rank = self.getRank(card)
            suit = self.getSuit(card)

            if rank == bestRank:
                return card
        
        return None

    def checkRunner(self, secondRank, isHigh):
        for card in self.myCards:
            rank = self.getRank(card)
            suit = self.getSuit(card)

            if self.highCards[suit] == None:
                return self.bestOfSuit(suit, isHigh)
            elif (self.highCards[suit] == suit + str(secondRank)) and (rank == secondRank):
                return card
            else:
                return None

    def bestOfSuit(self, checkSuit, isHigh):
        bestCard = None
        for card in self.myCards:
            rank = self.getRank(card)
            suit = self.getSuit(card)

            if suit == checkSuit:
                if bestCard == None:
                    bestCard = card
                elif isHigh and (rank > self.getRank(bestCard)):
                    bestCard = card
                elif not isHigh and (rank < self.getRank(bestCard)):
                    bestCard = card

        return bestCard

    def startTrickLow(self):
        bestLead = self.checkAcesNines(9)
        if bestLead is not None:
            return bestLead

        bestLead = self.checkRunner(10, False)

        if bestLead is not None:
            return bestLead

        return self.getWorstCardLow()

    def startTrickSuit(self, trump):
        bestLead = self.checkForBestTrump(trump)

        if bestLead is not None:
            return bestLead

        bestLead = self.checkForOffAces(trump)

        if bestLead is not None:
            return bestLead

        return self.getWorstCardTrumpHigh()

    def checkForBestTrump(self, trump):
        for card in self.myCards:
            if self.highCards[trump] == None:
                continue
            if card == self.highCards[trump]:
                return card

        return None

    def checkForOffAces(self, trump):
        nextSuit = self.getNextSuit(trump)

        nextSuitAce = None

        for card in self.myCards:
            rank = self.getRank(card)
            suit = self.getSuit(card)

            if (rank == 14) and (suit != trump) and (suit != nextSuit):
                return card
            elif (rank == 14) and (suit == nextSuit):
                nextSuitAce = card

        return nextSuitAce

    def getNextSuit(self, trump):
        if trump == "c":
            return "s"
        elif trump == "d":
            return "h"
        elif trump == "h":
            return "d"
        elif trump == "s":
            return "c"

        return None
    
    def getWorstCardTrumpHigh(self):
        lowCard = None

        for card in self.myCards:
            if lowCard == None:
                lowCard = card
            else:
                lowCard = self.getWorseCardCompare(lowCard, card)

        return lowCard

    def getWorstCardLow(self):
        highCard = None
        
        for card in self.myCards:
            if highCard == None:
                highCard = card
            else:
                highCard = self.getBestCardCompare(highCard, card)

        return highCard
    
    def getWorseCardCompare(self, cardA, cardB, suitLead = None):
        trump = self.bid["type"]

        suitA = self.getSuitRespectingTrump(cardA, trump)
        suitB = self.getSuitRespectingTrump(cardB, trump)

        rankA = self.getRank(cardA)
        rankB = self.getRank(cardB)

        if suitA == trump and suitB != trump:
            return cardB
        elif suitA != trump and suitB == trump:
            return cardA
        elif suitA == trump and suitB == trump:
            if cardA == trump + "11":
                return cardB
            elif cardB == trump + "11":
                return cardA
            elif self.isLeftBower(rankA, suitA, trump):
                return cardB
            elif self.isLeftBower(rankB, suitB, trump):
                return cardA
            elif rankA > rankB:
                return cardB
            else:
                return cardA
        elif suitA == suitLead and suitB != suitLead:
            return cardB
        elif suitA != suitLead and suitB == suitLead:
            return cardA
        else:
            if rankA > rankB:
                return cardB
            else:
                return cardA

    def getBestCardCompare(self, cardA, cardB):
        tempCard = self.getWorseCardCompare(cardA, cardB)
        if (cardA == tempCard):
            return cardB
        else:
            return cardA
    
    def isFirstCardBetter(self, cardA, cardB):
        betterCard = self.getBestCardCompare(cardA, cardB)

        return (betterCard == cardA)

    def getSuitRespectingTrump(self, card, trump):
        rank = self.getRank(card)
        suit = self.getSuit(card)

        if suit == trump or self.isLeftBower(rank, suit, trump):
            return trump
        
        return suit

    def chooseCard(self, handState, trickInfo):
        myTeamWinning = False
        if (trickInfo["highPlayer"] % 2) == (self.getIndex() % 2):
            myTeamWinning = True

        tempCards = self.myCards
        cardToPlay = None

        if myTeamWinning:
            cardToPlay = self.chooseCardWinningTrick(trickInfo)
        else:
            cardToPlay = self.chooseCardLosingTrick(trickInfo)
        
        self.myCards = tempCards
        return cardToPlay

    def chooseCardWinningTrick(self, trickInfo):
        suitLead = self.getSuitRespectingTrump(trickInfo["highCard"], self.bid["type"])

        legalCards = self.getCardsOfSuit(suitLead)
        if len(legalCards) == 0:
            legalCards = self.myCards

        if self.highCards[suitLead] == None or trickInfo["highCard"] == self.highCards[suitLead] or self.isFirstCardBetter(trickInfo["highCard"], self.highCards[suitLead]):
            if self.bid["type"] == "low":
                return self.getWorstCardLow()
            else:
                return self.getWorstCardTrumpHigh()
        else:
            if self.bid["type"] == "low":
                return self.startTrickLow()
            elif self.bid["type"] == "high":
                return self.startTrickHigh()
            else:
                return self.startTrickSuit(self.bid["type"])

    def getCardsOfSuit(self, suitLead):
        legalCards = []

        for card in self.myCards:
            if self.getSuitRespectingTrump(card, self.bid["type"]) == suitLead:
                legalCards.append(card)

        return legalCards

    def chooseCardLosingTrick(self, trickInfo):
        suitLead = self.getSuitRespectingTrump(trickInfo["highCard"], self.bid["type"])

        legalCards = self.getCardsOfSuit(suitLead)
        if len(legalCards) == 0:
            legalCards = self.myCards

        if self.bid["type"] == "low":
            return self.startTrickLow()
        elif self.bid["type"] == "high":
            return self.startTrickHigh()
        else:
            return self.startTrickSuit(self.bid["type"])

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
            if self.cardsRemaining[suit] < 100:
                self.highCards[suit] = suit + "13"

        elif rank == 13:
            self.cardsRemaining[suit] -= 40
            if self.cardsRemaining[suit] < 40:
                self.highCards[suit] = None

    def recalculateLowRemaining(self, card):
        suit = self.getSuit(card)
        rank = self.getRank(card)

        if rank == 9:
            self.cardsRemaining[suit] -= 100
            if self.cardsRemaining[suit] < 100:
                self.highCards[suit] = suit + "10"

        elif rank == 10:
            self.cardsRemaining[suit] -= 40
            if self.cardsRemaining[suit] < 40:
                self.highCards[suit] = None

    def recalculateSuitRemaining(self, card, trump):
        suit = self.getSuit(card)
        rank = self.getRank(card)

        if suit == trump:
            if rank == 11:
                self.cardsRemaining[trump] -= 100
                if self.cardsRemaining[trump] < 100:
                    self.highCards[trump] = self.getLeftBower(trump)
            else:
                self.cardsRemaining[trump] -= 1
        
        elif self.isLeftBower(rank, suit, trump):
            self.cardsRemaining[trump] = -40
            if self.cardsRemaining[trump] < 40:
                self.highCards[trump] = None

        else:
            self.recalculateHighRemaining(card)

    def getLeftBower(self, trump):
        if trump == "c":
            return "s11"
        elif trump == "d":
            return "h11"
        elif trump == "h":
            return "d11"
        elif trump == "s":
            return "c11"

        return None

    def dropHorse(self):
        print("TODO")

    def passHorse(self):
        print("TODO")

    def trueRound(self, number):
        if (number % 1) > .5:
            return math.ceil(number)
        else:
            return math.floor(number)