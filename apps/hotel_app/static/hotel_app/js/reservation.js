var theForm = document.forms["reservation_form"];

var room_prices = newArray();
room_prices["King"] = 280.00;
room_prices["Queen"] = 280.00;
room_prices["Deluxe"] = 450.00;

function get_subtotal()
{
    var room_prices = 0;
    var theForm = document.forms["reservation_form"];
    var selectedRoom = theForm.elements["room_type"];
    subtotal = room_prices[selectedRoom.value];
    return subtotal;
}