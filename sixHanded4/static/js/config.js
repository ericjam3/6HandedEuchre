urlString = 'http://159.65.173.147:4444/';

$(document).ready(function(){
    $("#roomNumber").html("Room 4");

    var roomLinkString = '<div id="otherRooms">OTHER ROOMS</div>' +
    '<div><a href="http://159.65.173.147:6543/">6 Handed Room 1</a></div>' +
    '<div><a href="http://159.65.173.147:6542/">6 Handed Room 2</a></div>' +
    '<div><a href="http://159.65.173.147:3333/">6 Handed Room 3</a></div>' +
    '<div><a href="http://159.65.173.147:7771/">Pepper Room 1</a></div>' +
    '<div><a href="http://159.65.173.147:7772/">Pepper Room 2</a></div>';

    $("#roomLink").html(roomLinkString);
});