// Now synced with Dev using ./copyFiles from 6HandedEuchre directory

// variables
var socket = io.connect(urlString);
var username = "";
var playerPosition = -1;
var playersArray;
var myCards;
var dealer;
var currentStage = "Opening";
var dicts = {};
var dropCount = 0;
var passedCards = [];

/////////////////////////////////////////////////////////////////////

socket.on( 'connect', function() {
    username = sessionStorage.getItem("username");

    socket.emit( 'connection', {
        data: username
    } )

    setupUI();
} )

function submitName(){
    username = $( '#username' ).val();
    sessionStorage.setItem("username", username);

    socket.emit( 'signin', {
        user_name : username
    } )

    setUIToWaiting();
}

function addBot(){
    showBotScreen();
}

function showBotScreen(){
    $("#botForm").show();
    $("#signinScreen").hide();
    $("#roomLink").hide();
    
    $("#botName").focus();
}

function hideBotScreen(){
    $("#botName").val("");
    $("#botForm").hide();
    $("#signinScreen").show();
    $("#roomLink").show();
}

function submitBot(){
    let botName = $("#botName").val();
    let botSkill = $('input[name="botSkill"]:checked').val();

    if (botName){
        addBotPlayer(botName, botSkill);
        hideBotScreen();
    }
}

function addBotPlayer(botName, botSkill){
    socket.emit('add bot', {
        botName: botName,
        botSkill: botSkill
    })
}

socket.on('reconnection', function(data){
    if (data.user == username){
        dicts = data.dicts;
        setReconnectData(data);

        if (currentStage != "signIn"){
            setReconnectUI();
        }

        setGameState(data);
    }
})

socket.on('playersIn', function(data){
    if (data.players.length > 0){
        showLoggedInPlayers(data.players);
    }
})

function showLoggedInPlayers(loggedInPlayers){
    let orangeHtmlString = "";
    let blueHtmlString = "";

    for (let i = 0; i < loggedInPlayers.length; i++){
        if (i % 2){     // blue
            blueHtmlString += "<div id='loggedInPlayer" + i + "' class='bluePlayer'>" +
            loggedInPlayers[i] + "</div>";
        }else{          // orange
            orangeHtmlString += "<div id='loggedInPlayer" + i + "' class='orangePlayer'>" +
            loggedInPlayers[i] + "</div>";
        }
    }

    $("#orangePlayersLoggedIn").html(orangeHtmlString);
    $("#bluePlayersLoggedIn").html(blueHtmlString);

    if (loggedInPlayers.length < 6){
        $("#clearPlayersButtonContainer").show();
    }else{
        $("#clearPlayersButtonContainer").hide();
        $("#roomFullDiv").show();
    }
}

socket.on('disconnect', function(reason){
    console.log(reason);
})

function setReconnectData(data){
    currentStage = data.gameState.currentStage;
    myCards = data.gameState.myCards;
    
    // Setup playersArray
    players = data.gameState.players
    playerPosition = players.indexOf(username);
    players = players.concat(players.splice(0, playerPosition));
    playersArray = players;
}

function setReconnectUI(){
    $("#signinScreen").hide();
    $("#roomLink").hide();
    placePlayers();
    $("#gametable").show();

    let hideBid = false;
    if (currentStage == "signIn" || currentStage == "bidding"){
        hideBid = true;
    }

    updateScoreboard(true, hideBid);

    sortCards();
    showCards();
}

function setGameState(data){
    if (currentStage == "bidding"){
        setupBidding(data);
        tryBidding(data.gameState.playerTurn, dicts.highBid.high);
    }else if (currentStage == "playCards"){
        setupPlayCards(data);
        if (!isMyTurn(dicts.highBid.playerInd) && data.gameState.cardsPlayed == 0){
            showWhoLead(dicts.highBid.playerInd);
        }
    }else if (currentStage == "signIn"){
        setUIToWaiting();
    }else if (currentStage == "dropHorse"){
        if (dicts.highBid.playerInd == playerPosition){
            dropTwoCardsHorse();
        }else{
            showDropping(dicts.highBid.playerInd);
            currentStage = "waiting";
        }
    }else if (currentStage == "passHorse"){
        if (playerPosition == getPlayerIndBasedOnOffset(data.gameState.playerTurn, dicts.highBid.playerInd)){
            passedCards = data.gameState.passedCards;
            passCardHorse();
        }else{
            showPassing(getPlayerIndBasedOnOffset(data.gameState.playerTurn, dicts.highBid.playerInd));
            currentStage = "waiting";
        }
    }
}

function setupBidding(data){
    showWhoBidder(data.gameState.playerTurn);
    placeBids(data.gameState.bids);
}

function placeBids(bids){
    bids = bids.concat(bids.splice(0, playerPosition));

    for (let i = 0; i < bids.length; i++){
        if (bids[i] != null){
            $("#player" + i).html($("#player" + i).html() + convertBidToHtml(bids[i]));
        }
    }
}

function setupPlayCards(data){
    placeLiveCards(data.gameState.liveCards);
    let firstCard = checkIfLeading(data.gameState.cardsPlayed);
    tryPlayCard(data.gameState.playerTurn, firstCard);
}

function placeLiveCards(liveCards){
    for (let i = 0; i < liveCards.length; i++){
        if (liveCards[i] != null){
            placeLiveCard(liveCards[i], i);
        }
    }
}

function checkIfLeading(cardsPlayed){
    if (cardsPlayed == 0){
        return true;
    }

    return false;
}

$(document).ready(function(){
    let usernameInput = document.getElementById("username");

    usernameInput.addEventListener("keyup", function(event){
        if (event.keyCode === 13){
            submitName();
        }
    });
});

//////////////////////////////////////////////////////////

function setUIToWaiting(){
    $( '#signin' ).hide();
    $('#roomLink').hide();
    $( '#waiting' ).show();
}

 // Set up the UI
function setupUI(){
    $("#gametable").hide();
    $("#username").focus();
}

function setupBidNumberChange(){
    if ($("#bidNumber").val() == "0"){
        $("#bidType").hide();
        $("#submitBid").prop('disabled', false);
    }else{
        $("#bidType").show();
        
        if ($("#bidType").val() == ""){
            $("#submitBid").prop('disabled', true);
        }
    }
}

function setupBidTypeChange(){
    if ($("#bidType").val() == ""){
        $("#submitBid").prop('disabled', true);
    }else{
        $("#submitBid").prop('disabled', false);
    }
}

socket.on( 'begin', function( players ) {
    $( '#signinScreen' ).hide();
    $("#roomLink").hide();

    // Setup playersArray
    playerPosition = players.indexOf(username);
    players = players.concat(players.splice(0, playerPosition));
    playersArray = players;

    placePlayers();

    $("#gametable").show();
})

function placePlayers(){
    for (let i = 0; i < playersArray.length; i++){
        let ind = i;
        $("#player" + ind).html(playersArray[i]);

        // Assign colors to players
        let colorA = "#174887";
        let colorB = "#f28a1b";
        if (playerPosition % 2){
            colorA = "#f28a1b";
            colorB = "#174887";
        }
        if (i % 2){
            $("#player" + ind).css("color", colorA);
        }else{
            $("#player" + ind).css("color", colorB);
        }
    }
}

//#region UI (User Interface)

function sortCards(){
    myCards.sort(cardSortComparator);
}

function cardSortComparator(a, b){
    let rankA = getRankRespectingTrump(getSuit(a), getRank(a));
    let rankB = getRankRespectingTrump(getSuit(b), getRank(b));

    let suitA = convertSuitToNumber(getSuitRespectingTrump(getSuit(a), getRank(a)));
    let suitB = convertSuitToNumber(getSuitRespectingTrump(getSuit(b), getRank(b)));

    if (suitA - suitB != 0){
        return suitA - suitB;
    }else{
        return rankA - rankB;
    }
}

function getTrump(){
    return dicts.highBid["type"]
}

// Shows all the cards currently in your hand
function showCards(){
    cardsHtml = "";
    for (let i = 0; i < myCards.length; i++){
        let cardCharacteristics = getCardRankAndSuit(myCards[i]);

        cardsHtml += "<div id='card" + i + "' class='card myCard' value=" + myCards[i] + " onclick='playCard(this)' style='color: " +
            cardCharacteristics["color"] + "'>" + cardCharacteristics["rank"] + "<br>" + convertSuitToImageHtml(cardCharacteristics["suit"]) + "</div>";
    }
    $("#myCards").html(cardsHtml);
}

function convertSuitToNumber(suit){
    switch (suit){
        case "c":
            return 1;
        case "d":
            return 2;
        case "h":
            return 4;
        case "s":
            return 3;
        default:
            return 0;
    }
}

function getSuit(card){
    return card.slice(0,1);
}

function getSuitRespectingTrump(suit, rank){
    trump = getTrump();
    
    if (isTrumpHighOrLow(trump)){
        return suit;
    }

    switch (suit){
        case "c":
            if (trump == "s" && rank == "11"){
                return "s";
            }
            break;
        case "d":
            if (trump == "h" && rank == "11"){
                return "h";
            }
            break;
        case "h":
            if (trump == "d" && rank == "11"){
                return "d";
            }
            break;
        case "s":
            if (trump == "c" && rank == "11"){
                return "c";
            }
            break;
        default:
            return suit;
    }

    return suit;
}

function getRankRespectingTrump(suit, rank){
    trump = getTrump();

    if (isTrumpHighOrLow(trump)){
        return rank;
    }

    if (rank == "11"){
        switch (suit){
            case "c":
                if (trump == "s"){
                    return "15";
                }else if (trump == "c"){
                    return "16";
                }
                break;
            case "d":
                if (trump == "h"){
                    return "15";
                }else if (trump == "d"){
                    return "16";
                }
                break;
            case "h":
                if (trump == "d"){
                    return "15";
                }else if (trump == "h"){
                    return "16";
                }
                break;
            case "s":
                if (trump == "c"){
                    return "15";
                }else if (trump == "s"){
                    return "16";
                }
                break;
            default:
                return rank;
        }
    }

    return rank;
}

function getRank(card){
    return card.slice(1);
}

function getColor(suit){
    if (suit == "c" || suit == "s"){
        return "black";
    }else{
        return "red";
    }
}

// Get rank, suit, and color of a given card
function getCardRankAndSuit(card){
    let suit = getSuit(card);
    let rank = getRank(card);
    var color;

    color = getColor(suit);

    switch (rank){
        case "11":
            rank = "J";
            break;
        case "12":
            rank = "Q";
            break;
        case "13":
            rank = "K";
            break;
        case "14":
            rank = "A";
            break;
        default:
            break;
    }

    return {"rank": rank, "suit": suit, "color": color};
}

//#endregion

//#region Gameplay

socket.on( 'deal', function( json ) {
    clearPlayedCards();
    showBidHtml();
    dicts = json.dicts;

    currentStage = "bidding";

    myCards = json.deck.slice(playerPosition * 8, (playerPosition + 1) * 8);

    sortCards();
    showCards();

    dealer = dicts.handInfo.dealer;

    updateScoreboard(true);
    tryBidding(dealer, 0);
})

// Start the bidding if it is my turn
function tryBidding(bidderInd, bidNumber){
    hideBidding();
    showWhoBidder(bidderInd);

    if (bidderInd == playerPosition){
        presentBids(bidNumber);
    }
}

// Present player with options for bid
function presentBids(currentBid){
    hideBidHtml(currentBid);
    $("#bidding").show();
}

// Hide bids less than or equal to current bid
function hideBidHtml(currentBid){
    let bidNumber = parseInt(currentBid);
    for (let i = 1; i <= bidNumber; i++){
        // $("#bidNumber").children("option[value=" + i + "]").hide();
        $("#bidNumber").children("option[value=" + i + "]").attr('disabled', 'disabled').hide();
    }
}

// Show all bids for a new hand
function showBidHtml(){
    for (let i = 0; i <= 10; i++){
        $("#bidNumber").children("option[value=" + i + "]").removeAttr('disabled').show();
    }

    $("#bidNumber").val("0");
    $("#bidType").val("");
    $("#bidType").hide();
}

// Hide bidding display
function hideBidding(){
    $("#bidding").hide();
    $(".bidder").remove();
}

function showWhoBidder(bidderInd){
    let htmlString = "<div class='bidder'>Bidding...</div>";
    $(".bidder").remove();
    $("#player" + getPlayerIndInPlayersArray(bidderInd)).append(htmlString);
}

// Submit your bid
function submitBid(){
    if (currentStage != "bidding"){
        return;
    }

    hideBidding();
    let nextBidder = playerPosition + 1;
    if (nextBidder > 5){
        nextBidder = 0;
    }

    socket.emit('submit bid', {
        bidNumber : $("#bidNumber").val(),
        bidType : $("#bidType").val(),
        nextBidder: nextBidder,
        currentBidder: playerPosition,
        dicts: dicts
    })
}

socket.on('bid placed', function(bidInfo){
    dicts = bidInfo.dicts;

    placePreviousBidHtml(bidInfo);
    tryBidding(bidInfo.nextBidder, bidInfo.high);
})

function placePreviousBidHtml(bidInfo){
    let previousBidder = getPlayerPos(bidInfo.currentBidder);

    $("#player" + previousBidder).html($("#player" + previousBidder).html() + convertBidToHtml(bidInfo));
}

function getPlayerPos(rawInd){
    let pos = rawInd - playerPosition;
    if (pos < 0){
        pos = 6 + pos;
    }

    return pos;
}

function convertBidToHtml(bidInfo){
    let html = "<div class='playerBid'>";

    switch (bidInfo.bidNumber){
        case "0":
            html += "Pass</div>";
            return html;
        case "9":
            html += "Horse";
            break;
        case "10":
            html += "Pepper";
            break;
        default:
            html += bidInfo.bidNumber;
            break;
    }

    html += " " + convertSuitToImageHtml(bidInfo.bidType) + "</div>";

    return html;
}

socket.on('done bidding', function(bidInfo){
    dicts = bidInfo.dicts;

    hideBidding();
    $(".leader").remove();

    if ((dicts.highBid.playerInd == playerPosition) && bidInfo.passedCards){
        myCards.push(bidInfo.passedCards[0]);
        myCards.push(bidInfo.passedCards[1]);
    }

    sortCards();
    showCards();
    updateScoreboard(true);

    hideStuffAfterBidding();
    highBid = dicts.highBid;
    handInfo = dicts.handInfo;

    if (!isMyTurn(highBid.playerInd)){
        showWhoLead(highBid.playerInd);
        return;
    }

    startTrick();
})

function updateScoreboard(showScoreboard, hideBid){
    dealer = dicts.handInfo.dealer;

    $("#dealer").html(playersArray[getPlayerIndInPlayersArray(dealer)]);
    $("#orangeTricksTaken").html(dicts.handInfo.orangeTricks);
    $("#blueTricksTaken").html(dicts.handInfo.blueTricks);

    $("#handsLeft").html(dicts.handInfo.handsLeft);
    $("#orangeScore").html(dicts.handInfo.orangeScore);
    $("#blueScore").html(dicts.handInfo.blueScore);

    if (!hideBid){
        if (dicts.highBid.high){
            $("#bid").html(playersArray[getPlayerIndInPlayersArray(dicts.highBid.playerInd)] +
            ": " + getBidNumberFormat(dicts.highBid.high) + " " + convertSuitToImageHtml(dicts.highBid.type));
        }else{
            $("#bid").html("--");
        }
    }

    if (showScoreboard){
        $("#scoreboard").show();
    }
}

function getPlayerIndInPlayersArray(ind){
    let pos = ind - playerPosition;
    
    if (pos < 0){
        pos = 6 + pos;
    }

    return pos;
}

function getBidNumberFormat(bidNumber){
    if (parseInt(bidNumber) == 9){
        return "Horse";
    }else if (parseInt(bidNumber) == 10){
        return "Pepper";
    }else{
        return bidNumber;
    }
}

socket.on('new trick', function(currentInfo){
    dicts = currentInfo.dicts;

    updateScoreboard(true);
    newTrick(currentInfo);
})

function newTrick(currentInfo){
    clearPlayedCards();
    highBid = dicts.highBid;
    handInfo = dicts.handInfo;
    let leadPlayerInd = currentInfo.leadPlayerInd

    if (!isMyTurn(leadPlayerInd)){
        showWhoLead(leadPlayerInd);
        return;
    }

    startTrick();
}

function showWhoLead(leaderInd){
    let htmlString = "<div class='leader'>Lead</div>";
    $(".leader").remove();
    $("#player" + getPlayerIndInPlayersArray(leaderInd)).append(htmlString);
}

function hideStuffAfterBidding(){
    $(".playerBid").remove();
    $("#bidding").hide();
}

function clearPlayedCards(){
    $(".liveCard").css("background-color", "transparent");
    $(".liveCard").css("box-shadow", "none");
    $(".liveCard").html("");
}

function isMyTeamHorse(bidInfo){
    if (parseInt(bidInfo.high) == 9 && isPlayerOnMyTeam(bidInfo.playerInd)){
        return true;
    }
    return false;
}

function isPlayerOnMyTeam(player){
    return ((player + playerPosition) % 2 == 0);
}

function dropTwoCardsHorse(){
    currentStage = "dropHorse";

    dropCount = 2;

    let htmlString = "<div class='turnMarker'>Select 2 cards to drop</div>";
    $(".turnMarker").remove();
    $("#player0").append(htmlString);
}

function passCardHorse(){
    currentStage = "passHorse";

    let htmlString = "<div class='turnMarker'>Select 1 card to pass</div>";
    $(".turnMarker").remove();
    $("#player0").append(htmlString);
}



// My turn to play
function isMyTurn(turnInd){
    return (turnInd == playerPosition);
}

function startTrick(){
    showPlayCard("startTrick");
}

function showPlayCard(stage){
    currentStage = stage;

    let htmlString = "<div class='turnMarker'>YOUR TURN</div>";
    $(".turnMarker").remove();
    $("#player0").append(htmlString);
}

// Play a card from my hand
function playCard(card){
    card = card.attributes.value.value;
    let nextPlayer = getNextPlayerInd();

    if (currentStage == "dropHorse" && dropCount > 0){
        dropCard(card);
        dropCount--;

        if (dropCount == 0){
            $(".turnMarker").remove();
            socket.emit('done drop horse', {
                done: 1,
                dicts: dicts,
                myCardsHorse: myCards
            })
        }
        return;

    }else if (currentStage == "passHorse"){
        dropCard(card);
        $(".turnMarker").remove();
        passedCards.push(card);

        socket.emit('done drop horse', {
            passedCards: passedCards,
            dicts: dicts,
            singlePassedCard: card
        })

        passedCards = [];
        currentStage = "waiting";

        return;
    }else if (currentStage == "playCard"){
        // Don't allow them to make an illegal play
        if (illegalPlay(card)){
            return;
        }

        dropCard(card);
        currentStage = "waiting";

        $(".turnMarker").remove();

        socket.emit( 'play card', {
            playerPosition : playerPosition,
            cardPlayed : card,
            nextPlayer : nextPlayer,
            dicts: dicts
        } )
    }else if (currentStage == "startTrick"){
        dropCard(card);
        currentStage = "waiting";

        $(".turnMarker").remove();

        socket.emit( 'play card', {
            playerPosition : playerPosition,
            cardPlayed : card,
            suitLead : getSuitRespectingTrump(getSuit(card), getRank(card)),
            nextPlayer : nextPlayer,
            dicts: dicts
        } )
    }
}

function getNextPlayerInd(){
    let nextPlayer = playerPosition + 1;
    if (nextPlayer > 5){
        nextPlayer = 0;
    }

    return nextPlayer;
}

function dropCard(card){
    let indexToRemove = myCards.indexOf(card);
    myCards.splice(indexToRemove, 1);
    showCards();
}

function illegalPlay(card){
    let rank = getRank(card);
    let suit = getSuitRespectingTrump(getSuit(card), rank);
    let suitLead = dicts.trickInfo.suitLead;

    if (!hasSuit(suitLead)){
        return false;   // legal
    }else if (suit == suitLead){
        return false;   // legal
    }else{
        return true;    // illegal
    }
} 

function isTrumpHighOrLow(trump){
    if (trump == "high" || trump == "low"){
        return true;
    }

    return false;
}

function hasSuit(suit){
    for (let i = 0; i < myCards.length; i++){
        let myCardRank = getRank(myCards[i]);
        let myCardSuit = getSuitRespectingTrump(getSuit(myCards[i]), myCardRank);
        
        if (suit == myCardSuit){
            return true;
        }
    }
    
    return false;
}

// Place a played card on the table
socket.on( 'place card', function( cardInfo ) {
    if (cardInfo.dicts){
        dicts = cardInfo.dicts;
    }

    $(".leader").remove();

    if (cardInfo.cardPlayed){
        placeLiveCard(cardInfo.cardPlayed, cardInfo.playerPosition);
    }

    if (dicts.trickInfo.cardsPlayed < 6){
        if (isMyTurn(cardInfo.nextPlayer) && skipTurnHorsePepper()){
            let nextPlayer = getNextPlayerInd();
    
            socket.emit( 'play card', {
                playerPosition : playerPosition,
                cardPlayed : null,
                nextPlayer : nextPlayer,
                dicts: dicts
            } )
            return;
        }

        tryPlayCard(cardInfo.nextPlayer);
    }
})

function placeLiveCard(card, playerInd){
    let cardPosition = getPlayerPos(playerInd);
    let cardCharacteristics = getCardRankAndSuit(card); 

    $("#liveCard" + cardPosition).val(card);
    $("#liveCard" + cardPosition).css("color", cardCharacteristics["color"]);
    $("#liveCard" + cardPosition).css("background-color", "white");
    $("#liveCard" + cardPosition).css("box-shadow", "0 1px 0 1px rgba(0, 0, 0, 0.08), 0 1px 0 2px rgba(0, 0, 0, 0.05), 0 1px 0 3px rgba(0, 0, 0, 0.02)");
    $("#liveCard" + cardPosition).html(cardCharacteristics["rank"] + "<br>" + convertSuitToImageHtml(cardCharacteristics["suit"]));
    $("#liveCard" + cardPosition).show();
}

function skipTurnHorsePepper(){
    if (dicts.highBid.playerInd == playerPosition){
        return false;
    }

    if ((dicts.highBid.high == "10" || dicts.highBid.high == "9") && ((dicts.highBid.playerInd + playerPosition) % 2 == 0)){
        return true;
    }

    return false;
}

function convertSuitToImageHtml(suit){
    switch (suit){
        case "c":
            return "<img class='suitImage' src='../static/images/clubs.png'></img>"
        case "d":
            return "<img class='suitImage' src='../static/images/diamonds.png'></img>"
        case "h":
            return "<img class='suitImage' src='../static/images/hearts.png'></img>"
        case "s":
            return "<img class='suitImage' src='../static/images/spades.png'></img>"
        default:
            return suit;
    }
}

function tryPlayCard(playerInd, firstCard){
    if (isMyTurn(playerInd)){
        if (firstCard){
            showPlayCard("startTrick");
        }else{
            showPlayCard("playCard");
        }
    }
}

socket.on('horse drop', function(bidInfo){
    dicts = bidInfo.dicts;

    hideBidding();

    updateScoreboard(true);
    hideStuffAfterBidding();

    highBid = dicts.highBid;

    sortCards();
    showCards();

    if (highBid.playerInd == playerPosition){
        dropTwoCardsHorse();
    }else{
        showDropping(highBid.playerInd);
    }
})

function showDropping(dropperInd){
    let htmlString = "<div class='leader'>Dropping...</div>";
    $(".leader").remove();
    $("#player" + getPlayerIndInPlayersArray(dropperInd)).append(htmlString);
}

socket.on('pass horse', function(bidInfo){
    dicts = bidInfo.dicts;

    sortCards();
    showCards();

    let bidderInd = dicts.highBid.playerInd;
    $(".leader").remove();

    if (playerPosition == getPlayerIndBasedOnOffset(bidInfo.dropper, bidderInd)){
        passedCards = bidInfo.passedCards;
        passCardHorse();
    }else{
        showPassing(getPlayerIndBasedOnOffset(bidInfo.dropper, bidderInd));
    }
})

function getPlayerIndBasedOnOffset(offset, bidderInd){
    let pind = bidderInd + offset;

    if (pind > 5){
        pind = pind - 6;
    }

    return pind;
}

function showPassing(passerInd){
    let htmlString = "<div class='leader'>Passing...</div>";
    $(".leader").remove();
    $("#player" + getPlayerIndInPlayersArray(passerInd)).append(htmlString);
}

//#endregion

socket.on('gameover', function(json){
    sessionStorage.clear();
    $("#gameover").show();
    dicts = json.dicts;
    updateScoreboard(true);
})

function endGameButton(){
    $("#endGameDiv").show();
}

function keepPlayingButton(){
    $("#endGameDiv").hide();
}

function endGame(){
    socket.emit('end game');
}

socket.on('reset game', function(){
    sessionStorage.clear();
    window.location.href = urlString;
})