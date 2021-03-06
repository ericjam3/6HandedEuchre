# Now synced with Dev using ./copyFiles from 6HandedEuchre directory

import random
from ai import AI

# Global variables
players = []
numPlayers = 6
cardsPlayed = 0
prevCardWasNone = False
currentDeck = []
botDict = {}
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
    botTrackCardPlayed(card, playerInd)
    removeCard(card, playerInd)

def removeCard(card, playerInd):
    curBid = int(dicts["highBid"]["high"])

    if curBid < 9 or players[playerInd] not in botDict:
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

    # deck = ['d12', 'd14', 's14', 'd13', 'c12', 's10', 'h12', 'h11', 'd10', 'c13', 'h10', 's13', 'h10', 'c11', 's11', 'd14', 'c9', 'd11', 's12', 's12', 'h9', 'd10', 'h14', 'd12', 'c11', 's9', 'c14', 'c9', 'c10', 'h14', 's9', 's13', 'c10', 'h13', 'c14', 's14', 'd13', 'h11', 's11', 'd9', 'c12', 'd9', 'h9', 'h13', 's10', 'h12', 'c13', 'd11']
    # dicts["handInfo"]["dealer"] = 5
    # print(deck)

    currentDeck = deck
    setPlayerHands(deck)
    return deck

def setInitialHandInfo():
    global cardsPlayed

    cardsPlayed = 0
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

def addBot(name, skill, index):
    global botDict

    addPlayer(name)
    botDict[name] = AI(name, index, skill)

def dealCardsToBots(deck):
    global botDict
    global dicts

    for key in botDict:
        bot = botDict[key]

        botIndex = bot.getIndex()
        startCard = botIndex * 8
        stopCard = startCard + 8

        bot.dealCards(deck[startCard:stopCard])

def tryBotBidding(bidderInd):
    global dicts
    global bids

    for key in botDict:
        bot = botDict[key]

        botIndex = bot.getIndex()

        if (botIndex == bidderInd):
            botBidInfo = bot.tryBidding(bids, dicts["handInfo"])
            botBidInfo["currentBidder"] = botIndex
            botBidInfo["nextBidder"] = getNextPlayer(botIndex)
            botBidInfo["dicts"] = dicts

            return botBidInfo
    
    return -1

def getNextPlayer(currentPlayer):
    nextPlayer = currentPlayer + 1

    if nextPlayer > 5:
        nextPlayer = 0
    
    return nextPlayer

def startHandBot():
    global dicts

    for key in botDict:
        bot = botDict[key]

        bot.startHand(dicts["highBid"])

def playBotCard(curPlayerInd):
    global dicts
    global cardsPlayed
    global liveCards

    for key in botDict:
        bot = botDict[key]

        botIndex = bot.getIndex()

        if (botIndex == curPlayerInd):
            botPlayInfo = bot.playCard(dicts["handInfo"], cardsPlayed, dicts["trickInfo"])
            botPlayInfo["playerPosition"] = botIndex
            botPlayInfo["nextPlayer"] = getNextPlayer(botIndex)
            botPlayInfo["dicts"] = dicts

            return botPlayInfo

    return -1

def botTrackCardPlayed(card, playerInd):
    for key in botDict:
        bot = botDict[key]

        bot.recalculateCardsRemaining(card, playerInd, dicts["trickInfo"]["suitLead"])

def tryBotPassing(offset, bidderInd):
    global dicts

    passerInd = getPlayerIndBasedOnOffset(offset, bidderInd)

    for key in botDict:
        bot = botDict[key]

        botIndex = bot.getIndex()

        if botIndex == passerInd:
            botPassedCard = bot.passHorse()

            return botPassedCard

    return -1

def getPlayerIndBasedOnOffset(offset, bidderInd):
    pind = bidderInd + offset

    if pind > 5:
        pind = pind - 6

    return pind

def botHorseDrop(playerInd):
    global dicts

    for key in botDict:
        bot = botDict[key]

        botIndex = bot.getIndex()

        if botIndex == playerInd:
            botDropInfo = bot.dropHorse()
            botDropInfo["done"] = 1
            botDropInfo["dicts"] = dicts

            return botDropInfo

    return -1