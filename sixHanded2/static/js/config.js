urlString = 'http://159.65.173.147:6542/';

$(document).ready(function(){
    $("#roomNumber").html("Room 2");

    var roomLinkString =  '<div id="otherRooms">OTHER ROOMS</div>' +
    '<div><a href="http://159.65.173.147:6543/">Go To Room 1</a></div>' +
    '<div><a href="http://159.65.173.147:3333/">Go To Room 3</a></div>' +
    '<div><a href="http://159.65.173.147:4444/">Go To Room 4</a></div>' +
    '<div><a href="http://159.65.173.147:5555/">Go To Room 5</a></div>' +
    '<div><a href="http://159.65.173.147:7666/">Go To Room 6</a></div>' +
    '<div><a href="http://159.65.173.147:7777/">Go To Room 7</a></div>' +
    '<div><a href="http://159.65.173.147:8888/">Go To Room 8</a></div>';

    $("#roomLink").html(roomLinkString);
});