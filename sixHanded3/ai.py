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

    def calcPointSpread(self, gameState):
        self.handsLeft = gameState["handsLeft"]

        if self.getIndex() % 2: # Blue Team
            self.pointSpread = gameState["blueScore"] - gameState["orangeScore"]
        else:
            self.pointSpread = gameState["orangeScore"] - gameState["blueScore"]

    def tryBidding(self, bidsList, gameState):
        self.calcPointSpread(gameState)

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
        return {"bidNumber": self.finalBidNumber(bidsList, highestBidNumber, highestBidType, gameState), "bidType": highestBidType}

    def finalBidNumber(self, bidsList, myBidNumber, myBidType, gameState):
        highestPrevBid = None
        highestBidderInd = None
        highestBidType = None
        numBids = 0
        counter = 0

        if myBidNumber > 9:
            return "p"

        for bid in bidsList:
            counter += 1
            if bid is None:
                continue
            
            numBids += 1

            if int(bid["bidNumber"]) >= myBidNumber:
                return "0"

            if highestPrevBid == None:
                highestPrevBid = int(bid["bidNumber"])
                highestBidderInd = counter - 1
                highestBidType = bid["bidType"]
            elif int(bid["bidNumber"]) > highestPrevBid:
                highestPrevBid = int(bid["bidNumber"])
                highestBidderInd = counter - 1
                highestBidType = bid["bidType"]

        if numBids == 5 and myBidNumber < 9:
            if (highestBidderInd % 2 == self.getIndex() % 2) and (myBidType == highestBidType):
                return "0"
            else:
                myBidNumber = highestPrevBid + 1

        return str(int(myBidNumber))

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

        estimatedTricks = self.getEstimatedTricksHighLow(points, howManyOfEachSuit, bidsList)

        shouldPepper = self.checkForHighLowPepper(estimatedTricks, bidsList)
        if shouldPepper:
            return 10

        shouldHorse = self.checkForHighLowHorse(estimatedTricks, bidsList)
        if shouldHorse:
            return 9
            
        return self.adjustBid(estimatedTricks, "high", bidsList)

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

    def checkForHighLowHorse(self, estimatedTricks, bidsList):
        if estimatedTricks >= 5.5 and self.pointSpread < -14:
            return True
        elif estimatedTricks >= 5 and self.handsLeft == 1 and self.pointSpread < -8:
            return True
        elif estimatedTricks >= 3.5 and self.handsLeft == 1 and self.pointSpread < -8 and self.howManyPreviousBidders(bidsList) >= 4:
            return True
        
        return False

    def checkForHighLowPepper(self, estimatedTricks, bidsList):
        if estimatedTricks >= 6.5 and self.pointSpread < -29:
            return True
        elif estimatedTricks >= 6 and self.handsLeft == 1 and self.pointSpread < -15:
            return True
        elif estimatedTricks >= 4.5 and self.handsLeft == 1 and self.pointSpread < -15 and self.howManyPreviousBidders(bidsList) >= 4:
            return True
        
        return False

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

        estimatedTricks = self.getEstimatedTricksHighLow(points, howManyOfEachSuit, bidsList)

        shouldPepper = self.checkForHighLowPepper(estimatedTricks, bidsList)
        if shouldPepper:
            return 10

        shouldHorse = self.checkForHighLowHorse(estimatedTricks, bidsList)
        if shouldHorse:
            return 9
            
        return self.adjustBid(estimatedTricks, "low", bidsList)

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

        shouldPepper = self.checkForSuitPepper(estimatedTricks, trump, points, bidsList)
        if shouldPepper:
            return 10

        shouldHorse = self.checkForSuitHorse(estimatedTricks, trump, points, bidsList)
        if shouldHorse:
            return 9

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

    def checkForSuitHorse(self, estimatedTricks, trump, points, bidsList):
        numLosers = self.getNumLosers(trump)

        if self.pointSpread < -24 and estimatedTricks > 4 and numLosers < 4:
            return True
        elif self.pointSpread < -14 and estimatedTricks > 5 and numLosers < 3:
            return True
        elif estimatedTricks >= 5.5 and numLosers < 3 and points >= 240:
            return True
        elif estimatedTricks >= 5.5 and numLosers < 3 and points > 202:
            return True
        elif estimatedTricks >= 5 and numLosers < 4 and self.pointSpread < -8 and self.handsLeft == 1:
            return True
        elif estimatedTricks >= 4 and numLosers < 5 and self.handsLeft == 1 and self.pointSpread < -8 and self.howManyPreviousBidders(bidsList) >= 4:
            return True

        return False

    def checkForSuitPepper(self, estimatedTricks, trump, points, bidsList):
        numLosers = self.getNumLosers(trump)

        if self.pointSpread < -35 and estimatedTricks > 6 and numLosers < 2:
            return True
        elif self.pointSpread < -20 and estimatedTricks > 6.5 and numLosers == 0:
            return True
        elif estimatedTricks >= 7 and numLosers == 0 and points >= 240:
            return True
        elif estimatedTricks >= 7 and numLosers == 0 and points > 202:
            return True
        elif estimatedTricks >= 5 and numLosers < 3 and self.pointSpread < -15 and self.handsLeft == 1:
            return True
        elif estimatedTricks >= 4 and numLosers < 4 and self.handsLeft == 1 and self.pointSpread < -15 and self.howManyPreviousBidders(bidsList) >= 4:
            return True

        return False
            
    def getNumLosers(self, trump):
        numLosers = 0

        for card in self.myCards:
            suit = self.getSuitRespectingTrump(card, trump)
            rank = self.getRank(card)

            if rank != 14 and suit != trump:
                numLosers += 1

        return numLosers
        
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

        if self.bid["type"] == "high":
            self.initializeCardsRemainingHigh()
        elif self.bid["type"] == "low":
            self.initializeCardsRemainingLow()
        else:
            self.initializeCardsRemainingHigh()
            self.initializeCardsRemainingSuit()
        
    def initializeCardsRemainingHigh(self):
        self.highCards = {}
        for suit in self.suits:
            self.cardsRemaining[suit] = 280
            self.highCards[suit] = suit + "14"

    def initializeCardsRemainingLow(self):
        self.highCards = {}
        for suit in self.suits:
            self.cardsRemaining[suit] = 280
            self.highCards[suit] = suit + "9"

    def initializeCardsRemainingSuit(self):
        trump = self.bid["type"]

        self.cardsRemaining[trump] = 290
        self.highCards[trump] = trump + "11"

    def playCard(self, handState, cardsPlayed, trickInfo):
        cardPlayedInfo = {}

        if (self.bid["high"] == "9" or self.bid["high"] == "10") and ((self.bid["playerInd"] % 2) == (self.getIndex() % 2)) and (self.bid["playerInd"] != self.getIndex()):
            cardPlayedInfo["cardPlayed"] = None
            return cardPlayedInfo

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

        return self.getWorstCard()

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

        return self.getWorstCard()

    def startTrickSuit(self, trump):
        bestLead = self.checkForBestTrump(trump)

        if bestLead is not None:
            return bestLead

        bestLead = self.checkForOffAces(trump)

        if bestLead is not None:
            return bestLead

        return self.getWorstCard()

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

    def getWorstCard(self):
        worstCard = None

        for card in self.myCards:
            if worstCard == None:
                worstCard = card
            else:
                worstCard = self.getWorseCardCompare(worstCard, card)

        return worstCard        
    
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
            elif self.isLeftBower(rankA, self.getSuit(cardA), trump):
                return cardB
            elif self.isLeftBower(rankB, self.getSuit(cardB), trump):
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
            if trump != "low":
                if rankA > rankB:
                    return cardB
                else:
                    return cardA
            else:
                if rankA > rankB:
                    return cardA
                else:
                    return cardB

    def getBestCardCompare(self, cardA, cardB, suitLead = None):
        tempCard = self.getWorseCardCompare(cardA, cardB, suitLead)
        if (cardA == tempCard):
            return cardB
        else:
            return cardA
    
    def isFirstCardBetter(self, cardA, cardB, suitLead = None):
        if cardA == cardB:
            return False

        betterCard = self.getBestCardCompare(cardA, cardB, suitLead)

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
            cardToPlay = self.chooseCardBasedOnPlayedCards(trickInfo, False)
        else:
            cardToPlay = self.chooseCardBasedOnPlayedCards(trickInfo, True)
        
        self.myCards = tempCards
        return cardToPlay

    def chooseCardBasedOnPlayedCards(self, trickInfo, isLosing):
        suitLead = trickInfo["suitLead"]

        tryTrumpIn = isLosing
        if (self.bid["type"] == "high") or (self.bid["type"] == "low"):
            tryTrumpIn = False

        legalCards = self.getCardsOfSuit(suitLead)
        if len(legalCards) > 0:
            self.myCards = legalCards
            tryTrumpIn = False

        if not self.hasTrump():
            tryTrumpIn = False

        if self.highCards[suitLead] != None and (trickInfo["highCard"] == self.highCards[suitLead] or self.isFirstCardBetter(trickInfo["highCard"], self.highCards[suitLead])):
            if not isLosing or tryTrumpIn == False:
                return self.getWorstCard()
            else:
                return self.tryTrumpingIn(trickInfo)
        else:
            if tryTrumpIn:
                return self.tryTrumpingIn(trickInfo)

            cardToPlay = self.getBestCard(suitLead)
            if self.isFirstCardBetter(cardToPlay, trickInfo["highCard"], suitLead):
                return cardToPlay
            else:
                return self.getWorstCard()

    def hasTrump(self):
        trump = self.bid["type"]

        for card in self.myCards:
            suit = self.getSuitRespectingTrump(card, trump)

            if suit == trump:
                return True

        return False

    def getBestCard(self, suitLead = None):
        cardToPlay = None
        for card in self.myCards:
            if cardToPlay == None:
                cardToPlay = card
            elif self.isFirstCardBetter(card, cardToPlay, suitLead):
                cardToPlay = card
        
        return cardToPlay

    def getCardsOfSuit(self, suitLead):
        legalCards = []

        for card in self.myCards:
            if self.getSuitRespectingTrump(card, self.bid["type"]) == suitLead:
                legalCards.append(card)

        return legalCards

    def tryTrumpingIn(self, trickInfo):
        cardToBeat = trickInfo["highCard"]
        trump = self.bid["type"]
        cardToPlay = None

        for card in self.myCards:
            suit = self.getSuitRespectingTrump(card, trump)

            if suit != trump:
                continue

            if self.isFirstCardBetter(card, cardToBeat):
                if cardToPlay == None:
                    cardToPlay = card
                elif self.isFirstCardBetter(cardToPlay, card):
                    cardToPlay = card

        if cardToPlay == None:
            return self.getWorstCard()

        return cardToPlay

###################################################################        

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
            if self.cardsRemaining[suit] < 40:
                self.highCards[suit] = None
            elif self.cardsRemaining[suit] < 100:
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
            if self.cardsRemaining[suit] < 40:
                self.highCards[suit] = None
            elif self.cardsRemaining[suit] < 100:
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
            elif rank == 14:
                self.cardsRemaining[trump] -= 5

            self.setHighCardTrump(trump)
        
        elif self.isLeftBower(rank, suit, trump):
            self.cardsRemaining[trump] -= 40
            self.setHighCardTrump(trump)

        else:
            self.recalculateHighRemaining(card)

    def setHighCardTrump(self, trump):
        if self.cardsRemaining[trump] <= 0:
            self.highCards[trump] = None
        elif self.cardsRemaining[trump] < 40:
            self.highCards[trump] = trump + "14"
        elif self.cardsRemaining[trump] < 100:
            self.highCards[trump] = self.getLeftBower(trump)

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
        if self.bidIsSuit(self.bid["type"]):
            self.removePlayedCard(self.getWorstCard())
            self.removePlayedCard(self.getWorstCard())
        elif self.bid["type"] == "high":
            self.dropHighHorse()
            self.dropHighHorse()
        else:
            self.dropLowHorse()
            self.dropLowHorse()
        
        return {"myCardsHorse": self.myCards}

    def bidIsSuit(self, bidType):
        if bidType == "low" or bidType == "high":
            return False

        return True

    def dropHighHorse(self):
        points = self.getPointsHigh()
        return self.getCardToDropHighLow(points, 14)
        

    def getCardToDropHighLow(self, points, rankHighLow):
        weakCards = []

        for card in self.myCards:
            rank = self.getRank(card)
            suit = self.getSuit(card)

            if (points[suit] not in [100, 200, 240, 280]) and (rank != rankHighLow):
                weakCards.append(card)
        
        if len(weakCards) == 0:
            weakCards = self.myCards

        worstCard = None
        for card in weakCards:
            rank = self.getRank(card)
            suit = self.getSuit(card)

            if worstCard == None:
                worstCard = card
            elif points[suit] < points[self.getSuit(worstCard)]:
                worstCard = card

        self.removePlayedCard(worstCard)
        return worstCard

    def getPointsHigh(self):
        points = {"c": 0, "d": 0, "h": 0, "s": 0}

        for card in self.myCards:
            suit = self.getSuit(card)
            rank = self.getRank(card)

            if rank == 14:
                points[suit] += 100
            elif rank == 13:
                points[suit] += 40
            else:
                points[suit] += 1
        
        return points

    def dropLowHorse(self):
        points = self.getPointsLow()
        return self.getCardToDropHighLow(points, 9)

    def getPointsLow(self):
        points = {"c": 0, "d": 0, "h": 0, "s": 0}

        for card in self.myCards:
            suit = self.getSuit(card)
            rank = self.getRank(card)

            if rank == 9:
                points[suit] += 100
            elif rank == 10:
                points[suit] += 40
            else:
                points[suit] += 1
        
        return points

    def passHorse(self):
        return self.getBestCard()

    def trueRound(self, number):
        if (number % 1) > .5:
            return int(math.ceil(number))
        else:
            return int(math.floor(number))