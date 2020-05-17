from ai import AI

def testBidding1():
    bot = AI("bot", 0, 5)

    bot.dealCards(["c9", "c9", "c10", "c14", "d9", "s9", "s9", "h11"])
    botBid = bot.tryBidding([], {})
    
    checkBid(botBid, "low", "6", "1")

def testBidding2():
    bot = AI("bot", 0, 5)

    bot.dealCards(["c14", "c14", "c13", "c9", "d14", "s14", "s14", "h11"])
    botBid = bot.tryBidding([], {})
    
    checkBid(botBid, "high", "6", "2")

def testBidding3():
    bot = AI("bot", 0, 5)

    bot.dealCards(["c14", "c14", "c13", "c9", "d11", "d11", "h11", "d13"])
    botBid = bot.tryBidding([], {})
    
    checkBid(botBid, "d", "5", "3")

def testBidding4():
    bot = AI("bot", 0, 5)

    bot.dealCards(["c13", "s11", "c11", "c11", "d11", "d14", "s14", "h9"])
    botBid = bot.tryBidding([], {})
    
    checkBid(botBid, "c", "5", "4")
    

def checkBid(botBid, expectedType, expectedNumber, testNumber):
    assert botBid["bidType"] == expectedType, "Test " + testNumber + ": bid should be in " + expectedType + " not " + botBid["bidType"]
    assert botBid["bidNumber"] == expectedNumber, "Test " + testNumber + ": bid number should be " + expectedNumber + " not " + botBid["bidNumber"]


#######################################################################

def testLeading1():
    bot = AI("bot", 0, 5)

    bot.dealCards(["c10", "s11", "c11", "d10", "s12", "s13", "h11"])
    bot.startHand({"type": "c"})
    botPlay = bot.playCard({}, 0, {})

    checkPlay(botPlay["cardPlayed"], "c11", "1")
    checkPlay(botPlay["cardPlayed"], "c11", "1")
    checkPlay(botPlay["cardPlayed"], "s11", "1")


def checkPlay(botPlay, expectedCard, testNumber):
    assert botPlay == expectedCard, "Test " + testNumber + ": Should have led " + expectedCard + " not " + botPlay

if __name__ == '__main__':
    testBidding1()
    testBidding2()
    testBidding3()
    testBidding4()

    testLeading1()