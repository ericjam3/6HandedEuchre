# Now synced with Dev using ./copyFiles from 6HandedEuchre directory

import random
from ai import AI

# Global variables
players = []
numPlayers = 6
cardsPlayed = 0
currentDeck = []
botDict = {}
bidsList = []
dicts = {"highBid": {}, "handInfo": {}, "trickInfo": {}}

# Info needed for when a player reconnects
currentStage = "signIn"
bids = [None] * numPlayers
liveCards = [None] * numPlayers
playerTurn = 0
playersHands = []
passedCards = []

##########################################################

def addPlayer(username):
    global players
    global playersHands

    players.append(username)
    playersHands.append([])

def setPlayerHands(deck):
    for i in range(len(playersHands)):
        startInd = i * 8
        endInd = startInd + 8
        playersHands[i] = deck[startInd:endInd]

def setCurrentPlayer(player):
    global playerTurn
    playerTurn = player

def getCurrentPlayer():
    return playerTurn

def setBid(bidInfo):
    bids[bidInfo["currentBidder"]] = {"bidNumber": bidInfo["bidNumber"], "bidType": bidInfo["bidType"]}

def trackCardPlayed(card, playerInd):
    liveCards[playerInd] = card
    removeCard(card, playerInd)

def removeCard(card, playerInd):
    playersHands[playerInd].remove(card)

def getState(playerInd):
    state = {}
    state["currentStage"] = currentStage
    state["myCards"] = playersHands[playerInd]
    state["playerTurn"] = playerTurn
    state["players"] = players
    state["passedCards"] = passedCards

    if currentStage == "bidding":
        state["bids"] = bids
    elif currentStage == "playCards":
        state["liveCards"] = liveCards
        state["cardsPlayed"] = cardsPlayed

    return state

def updateHandAfterHorseDrop(newHand):
    global playersHands

    playersHands[dicts["highBid"]["playerInd"]] = newHand

def updateHandAfterHorsePass(newCard):
    global playersHands

    playersHands[dicts["highBid"]["playerInd"]].append(newCard)



##########################################################

def changeDealer():
    dicts["handInfo"]["dealer"] += 1

    if dicts["handInfo"]["dealer"] > 5:
        dicts["handInfo"]["dealer"] = 0

def resetGame():
    global dicts
    global players
    global currentStage
    global bids
    global liveCards
    global playerTurn
    global playersHands
    global passedCards
    global cardsPlayed
    global currentDeck
    global botDict
    global bidsList

    dicts = {"highBid": {}, "handInfo": {}, "trickInfo": {}}
    botDict = {}
    players = []

    currentStage = "signIn"
    bids = [None] * numPlayers
    liveCards = [None] * numPlayers
    playerTurn = 0
    playersHands = []
    passedCards = []

    cardsPlayed = 0
    bidsList = []
    currentDeck = []

def resetHand():
    global bids
    global liveCards
    global playerTurn
    global passedCards

    dicts["highBid"] = {}
    dicts["trickInfo"] = {}

    bids = [None] * numPlayers
    liveCards = [None] * numPlayers
    playerTurn = dicts["handInfo"]["dealer"]
    passedCards = []


def setInitialGameInfo():
    dicts["handInfo"]["handsLeft"] = 12
    dicts["handInfo"]["orangeScore"] = 0
    dicts["handInfo"]["blueScore"] = 0
    dicts["handInfo"]["dealer"] = 0

def getShuffledDeck():
    global currentDeck

    deck = []

    for i in range(2):
        for number in range(9, 15):
            for letter in ["c", "d", "h", "s"]:
                deck.append(letter + str(number))

    random.shuffle(deck)
    currentDeck = deck

    setPlayerHands(deck)

    return deck

def setInitialHandInfo():
    global cardsPlayed
    global bidsList

    cardsPlayed = 0
    bidsList = []
    dicts["handInfo"]["orangeTricks"] = 0
    dicts["handInfo"]["blueTricks"] = 0
    dicts["handInfo"]["tricksPlayed"] = 0

def setNewHandInfo():
    setInitialHandInfo()
    changeDealer()
    resetHand()

def startNewTrick():
    global cardsPlayed
    global liveCards
    global playerTurn
    global passedCards

    playerTurn = dicts["trickInfo"]["highPlayer"]
    liveCards = [None] * numPlayers
    passedCards = []

    cardsPlayed = 0
    dicts["trickInfo"] = {}
    

def getTrump():
    return dicts["highBid"]["type"]

###############################################################

def addBot(name, index):
    global botDict

    addPlayer(name)
    botDict[name] = AI(name, index, 5)

def dealCardsToBots(deck):
    global botDict
    global dicts

    for key in botDict:
        bot = botDict[key]

        botIndex = bot.getIndex()
        startCard = botIndex * 8
        stopCard = startCard + 8

        bot.dealCards(deck[startCard:stopCard])

def tryBotBidding(bidderInd, bidsList):
    global dicts

    for key in botDict:
        bot = botDict[key]

        botIndex = bot.getIndex()

        if (botIndex == bidderInd):
            botBidInfo = bot.tryBidding(bidsList, dicts["handInfo"])
            botBidInfo["currentBidder"] = botIndex
            botBidInfo["nextBidder"] = getNextBidder(botIndex)
            botBidInfo["dicts"] = dicts
            return botBidInfo
    
    return -1

def getNextBidder(currentBidder):
    nextBidder = currentBidder + 1

    if nextBidder > 5:
        nextBidder = 0
    
    return nextBidder