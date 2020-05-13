# Now synced with Dev using ./copyFiles from 6HandedEuchre directory

import smtplib, ssl

from flask import Flask, render_template
from flask import jsonify
from flask_socketio import SocketIO
import random
import time
import dataModel
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'notsosecretkey'
socketio = SocketIO(app)

@app.route('/')
def sessions():
    return render_template('session.html')

@socketio.on('connection')
def handle_connection(json, methods=['GET', 'POST']):
    if (json["data"] is not None and json["data"] in dataModel.players):
        reconnectPlayer(json["data"])
    else:
        socketio.emit('playersIn', {"players": dataModel.players})

def reconnectPlayer(username):
    reconnectData = {"user": username}
    reconnectData["dicts"] = dataModel.dicts
    reconnectData["gameState"] = dataModel.getState(dataModel.players.index(username))

    socketio.emit('reconnection', reconnectData)

@socketio.on('signin')
def handle_signin(json, methods=['GET', 'POST']):
    if (len(dataModel.players) < dataModel.numPlayers) and (json['user_name'] not in dataModel.players):
        dataModel.addPlayer(json['user_name'])
        socketio.emit('playersIn', {"players": dataModel.players})
        tryStartingGame()
    
    elif (json['user_name'] in dataModel.players):
        reconnectPlayer(json['user_name'])

@socketio.on('add bot')
def handle_add_bot(json, methods=['GET', 'POST']):
    if (len(dataModel.players) < dataModel.numPlayers) and (json['botName'] not in dataModel.players):
        dataModel.addBot(json['botName'], len(dataModel.players))
        socketio.emit('playersIn', {"players": dataModel.players})
        tryStartingGame()

def tryStartingGame():
    if len(dataModel.players) == dataModel.numPlayers:
        socketio.emit('begin', dataModel.players)

        dataModel.setInitialGameInfo()
        dealCards()

def dealCards():
    dataModel.currentStage = "bidding"
    deck = dataModel.getShuffledDeck()
    socketio.emit('deal', {"deck": deck, "dicts": dataModel.dicts})
    dataModel.dealCardsToBots(deck)

@socketio.on('submit bid')
def handle_submit_bid(json, methods=['GET', 'POST']):
    determineHighBid(json)

    dataModel.setBid(json)

    if json['nextBidder'] == dataModel.dicts["handInfo"]["dealer"] or dataModel.dicts["highBid"]["high"] == "10":        
        dataModel.setInitialHandInfo()
        
        json = {"dicts": dataModel.dicts}

        if int(dataModel.dicts["highBid"]["high"]) == 9:
            dataModel.currentStage = "dropHorse"
            dataModel.setCurrentPlayer(dataModel.dicts["highBid"]["playerInd"])

            socketio.emit('horse drop', json)
            return

        dataModel.currentStage = "playCards"
        dataModel.setCurrentPlayer(dataModel.dicts["highBid"]["playerInd"])

        socketio.emit('done bidding', json)  
    else:
        json["dicts"] = dataModel.dicts
        dataModel.setCurrentPlayer(json["nextBidder"])

        socketio.emit('bid placed', json)

# Determine who has the highest bid and what it is
def determineHighBid(bidInfo):
    if "high" not in dataModel.dicts["highBid"] or dataModel.dicts["highBid"]["high"] < bidInfo["bidNumber"]:
        dataModel.dicts["highBid"]["high"] = bidInfo["bidNumber"]
        dataModel.dicts["highBid"]["type"] = bidInfo["bidType"]
        dataModel.dicts["highBid"]["playerInd"] = bidInfo["currentBidder"]

    # HTML is being dumb, so I had to make Pepper 'p' instead of '10'
    if bidInfo["bidNumber"] == "p":
        dataModel.dicts["highBid"]["high"] = "10"
        dataModel.dicts["highBid"]["type"] = bidInfo["bidType"]
        dataModel.dicts["highBid"]["playerInd"] = bidInfo["currentBidder"]

    if "high" in dataModel.dicts["highBid"]:
        bidInfo["high"] = dataModel.dicts["highBid"]["high"]
    else:
        bidInfo["high"] = "0"


# Play a card
@socketio.on('play card')
def handle_card_played(json, methods=['GET', 'POST']):
    if json["cardPlayed"]:
        trackWhoWinningTrick(json)

    if json["cardPlayed"] is not None:
        dataModel.trackCardPlayed(json["cardPlayed"], json["playerPosition"])

    updateTrickInfo()
    dataModel.dicts["trickInfo"]["cardsPlayed"] = dataModel.cardsPlayed
    json["dicts"] = dataModel.dicts

    if dataModel.cardsPlayed > 5:
        json["lastCard"] = 1

    dataModel.setCurrentPlayer(json["nextPlayer"])
    socketio.emit('place card', json)

    if dataModel.cardsPlayed > 5:
        handleEndOfTrick()

def trackWhoWinningTrick(playInfo):
    if "suitLead" in playInfo:
        dataModel.dicts["trickInfo"]["highCard"] = playInfo["cardPlayed"]
        dataModel.dicts["trickInfo"]["suitLead"] = playInfo["suitLead"]
        dataModel.dicts["trickInfo"]["highPlayer"] = playInfo["playerPosition"]
    elif compareCards(playInfo["cardPlayed"], dataModel.dicts["trickInfo"]["highCard"]):
        dataModel.dicts["trickInfo"]["highCard"] = playInfo["cardPlayed"]
        dataModel.dicts["trickInfo"]["highPlayer"] = playInfo["playerPosition"]

# Returns true if first card is better than second
def compareCards(cardA, cardB):
    if dataModel.dicts["highBid"]["type"] == "high":
        return compareCardsHigh(cardA, cardB)
    elif dataModel.dicts["highBid"]["type"] == "low":
        return compareCardsLow(cardA, cardB)
    else:
        return compareCardsSuit(cardA, cardB)

# Returns true if first card is better than second
def compareCardsHigh(cardA, cardB):
    suitA = getSuit(cardA)
    suitB = getSuit(cardB)

    rankA = getRank(cardA)
    rankB = getRank(cardB)

    suitLead = dataModel.dicts["trickInfo"]["suitLead"]

    if suitA == suitLead:
        if suitB == suitLead:
            return rankA > rankB
        else:
            return True
    else:
        if suitB == suitLead:
            return False
        else:
            return rankA > rankB

# Returns true if first card is better than second
def compareCardsLow(cardA, cardB):
    suitA = getSuit(cardA)
    suitB = getSuit(cardB)

    rankA = getRank(cardA)
    rankB = getRank(cardB)

    suitLead = dataModel.dicts["trickInfo"]["suitLead"]

    if suitA == suitLead:
        if suitB == suitLead:
            return rankA < rankB
        else:
            return True
    else:
        if suitB == suitLead:
            return False
        else:
            return rankA < rankB

# Returns true if first card is better than second
def compareCardsSuit(cardA, cardB):
    trump = dataModel.getTrump()

    suitA = getSuit(cardA)
    suitB = getSuit(cardB)

    rankA = getRankRespectingBowers(getRank(cardA), suitA, trump)
    rankB = getRankRespectingBowers(getRank(cardB), suitB, trump)

    suitA = getSuitRespectingBowers(rankA, suitA, trump)
    suitB = getSuitRespectingBowers(rankB, suitB, trump)

    suitLead = dataModel.dicts["trickInfo"]["suitLead"]

    # Do the dirty work
    if suitA == trump:
        if suitB == trump:
            return rankA > rankB
        else:
            return True
    elif suitA == suitLead:
        if suitB == trump:
            return False
        elif suitB == suitLead:
            return rankA > rankB
        else:
            return True
    else:
        if suitB == trump or suitB == suitLead:
            return False
        else:
            return rankA > rankB


# Get suit of card
def getSuit(card):
    return card[0]

# Get rank of card
def getRank(card):
    return int(card[1:])

def getRankRespectingBowers(rank, suit, trump):
    if suit == trump and rank == 11:
        return 16
    elif isSuitNext(suit, trump) and rank == 11:
        return 15
    else:
        return rank


def isSuitNext(suit, trump):
    if suit == "c" and trump == "s":
        return True
    elif suit == "d" and trump == "h":
        return True
    elif suit == "h" and trump == "d":
        return True
    elif suit == "s" and trump == "c":
        return True
    
    return False

def getSuitRespectingBowers(rank, suit, trump):
    if (rank == 15):
        return trump
    else:
        return suit

def updateTrickInfo():
    dataModel.cardsPlayed += 1

def handleEndOfTrick():
    dataModel.dicts["handInfo"]["tricksPlayed"] += 1

    if dataModel.dicts["trickInfo"]["highPlayer"] % 2 == 0:
        dataModel.dicts["handInfo"]["orangeTricks"] += 1
    else:
        dataModel.dicts["handInfo"]["blueTricks"] += 1

    if dataModel.dicts["handInfo"]["tricksPlayed"] == 8:
        beginNewHand()
        return

    startAnotherTrick()

def startAnotherTrick():
    currentHandInfo = {"leadPlayerInd": dataModel.dicts["trickInfo"]["highPlayer"]}
    dataModel.startNewTrick()

    currentHandInfo["dicts"] = dataModel.dicts

    socketio.sleep(3)
    socketio.emit('new trick', currentHandInfo)


def beginNewHand():
    dataModel.dicts["handInfo"]["handsLeft"] -= 1
    
    calcNewScore()
    dataModel.setNewHandInfo()

    socketio.sleep(4)

    if (dataModel.dicts["handInfo"]["handsLeft"] == 0):
        if dataModel.dicts["handInfo"]["orangeScore"] != dataModel.dicts["handInfo"]["blueScore"]:
            emailScores()
            json = {}
            json["dicts"] = dataModel.dicts
            socketio.emit('gameover', json)
            dataModel.resetGame()
            return
        else:
            dataModel.dicts["handInfo"]["handsLeft"] = 1

    dealCards()

def calcNewScore():
    bidNumber = int(dataModel.dicts["highBid"]["high"])
    horse = False
    pepper = False
    
    if bidNumber == 9:
        bidNumber = 8
        horse = True
    elif bidNumber == 10:
        bidNumber = 8
        pepper = True

    biddingTeam = "orange"
    nonBiddingTeam = "blue"

    if dataModel.dicts["highBid"]["playerInd"] % 2:
        biddingTeam = "blue"
        nonBiddingTeam = "orange"

    dataModel.dicts["handInfo"][nonBiddingTeam + "Score"] += dataModel.dicts["handInfo"][nonBiddingTeam + "Tricks"]

    if dataModel.dicts["handInfo"][biddingTeam + "Tricks"] >= bidNumber:
        if horse:
            dataModel.dicts["handInfo"][biddingTeam + "Score"] += 15
        elif pepper:
            dataModel.dicts["handInfo"][biddingTeam + "Score"] += 30
        else:
            dataModel.dicts["handInfo"][biddingTeam + "Score"] += dataModel.dicts["handInfo"][biddingTeam + "Tricks"]

    else:
        if horse:
            dataModel.dicts["handInfo"][biddingTeam + "Score"] -= 15
        elif pepper:
            dataModel.dicts["handInfo"][biddingTeam + "Score"] -= 30
        else:
            dataModel.dicts["handInfo"][biddingTeam + "Score"] -= bidNumber

def emailScores():
    password = "cottagekeys"
    smtp_server = "smtp.gmail.com"
    senderEmail = "6handedeuchre@gmail.com"
    receiverEmail = "6handedeuchre@gmail.com"
    emailPort = 587

    if "handInfo" not in dataModel.dicts or "orangeScore" not in dataModel.dicts["handInfo"]:
        return

    orangeScore = dataModel.dicts["handInfo"]["orangeScore"]
    blueScore = dataModel.dicts["handInfo"]["blueScore"]

    orangePlayers = ""
    bluePlayers = ""

    for ind in range(len(dataModel.players)):
        if ind % 2 == 0:
            orangePlayers += dataModel.players[ind] + ", "
        else:
            bluePlayers += dataModel.players[ind] + ", "

    orangePlayers = orangePlayers[:-2]
    bluePlayers = bluePlayers[:-2]

    message="""\
    Subject: Game Score

    """

    message += orangePlayers + ": " + str(orangeScore)
    message += """
    
    """ + bluePlayers + ": " + str(blueScore)

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, emailPort) as server:
        server.starttls(context=context)
        server.login(senderEmail, password)
        server.sendmail(senderEmail, receiverEmail, message)

@socketio.on('done drop horse')
def handle_done_drop_horse(json, methods=['GET', 'POST']):
    # Save stuff for people who disconnect
    if "done" in json:
        dataModel.updateHandAfterHorseDrop(json["myCardsHorse"])
    else:
        dataModel.updateHandAfterHorsePass(json["singlePassedCard"])

    if "done" in json:
        json["dropper"] = 2
        json["passedCards"] = []
    else:
        json["dropper"] = 4

    dataModel.passedCards = json["passedCards"]

    if len(json["passedCards"]) == 2:
        dataModel.currentStage = "playCards"
        dataModel.setCurrentPlayer(dataModel.dicts["highBid"]["playerInd"])

        socketio.emit('done bidding', json)
    else:
        dataModel.currentStage = "passHorse"
        dataModel.setCurrentPlayer(json["dropper"])

        socketio.emit('pass horse', json)


@socketio.on('end game')
def handle_end_game(methods=['GET', 'POST']):
    emailScores()
    dataModel.resetGame()
    socketio.emit('reset game')
    





# Tests
def runTests():
    trickInfo = {}
    trickInfo["suitLead"] = "d"

    if (compareCardsLow("d12", "d9", trickInfo)):
        print("TestFailed: 1")

    if (compareCardsSuit("d14", "c11", "s", trickInfo)):
        print("TestFailed: 2")

    if (compareCardsSuit("d14", "d11", "d", trickInfo)):
        print("TestFailed: 3")  

    if (compareCardsHigh("d9", "d12", trickInfo)):
        print("TestFailed: 4") 

    if (compareCardsHigh("c14", "d9", trickInfo)):
        print("TestFailed: 5")     

    if (compareCardsSuit("d11", "h11", "h", trickInfo)):
        print("TestFailed: 6")


if __name__ == '__main__':
    # runTests()
    socketio.run(app, host='0.0.0.0', port=config.port, debug=False)