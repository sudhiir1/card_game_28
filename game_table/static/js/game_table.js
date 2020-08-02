ACTIVE_PLAYER = 1;
NO_SEAT = -1;

selectedCard = null;
dragStart = 0;

total_seats = 0;
seats = [];
play_cards = [];

my_seat = NO_SEAT;
active_playing = false;

my_table = 0;
my_name = "";

bid_window = null;

const TurnOptions = {
    "NOT_MY_TURN": 1,
    "PLAY_CARD": 2,
    "KEEP_TRUMP": 3
};
my_turn = TurnOptions.NOT_MY_TURN;

function intializePage(table, num_seats, name) {
    my_table = table;
    my_name = name;
    // addNewCards("");
    setup_table(num_seats);
    setup_bid_window();

    initiate_connection(table, name);
    /*var my_cards = document.getElementById("my_cards");
    my_cards.addEventListener("touchstart", dragMyCard, false);
    my_cards.addEventListener("touchend", dropMyCard, false);
    */
}

function setup_bid_window() {
    bid_window = document.getElementById("bid_window");
    bid_pass = document.getElementById("bid_-1");
    row = 15;
    column = 15;
    for (var i=0; i<=14; i++) {
        newButton = bid_pass.cloneNode(true);
        newButton.id = "bid_" + (i + 14);
        newButton.innerHTML = i + 14
        newButton.style.width = "10%";
        newButton.style.left = column + "%";
        newButton.style.top = row + "%";
        bid_window.appendChild(newButton);

        column += 15;
        if (column > 80) {
            row += 20;
            column = 15;
        }
    }

}

function setup_table(num_seats) {
    total_seats = parseInt(num_seats);
    seat_ids = [];
    if (total_seats == 4) {
        seat_ids = ["seat_mine", "seat_left", "seat_facing", "seat_right"];
        play_cards_ids = ["pcard_mine", "pcard_left", "pcard_facing", "pcard_right"];
    }
    else {
        seat_ids = ["seat_mine", "seat_left_down", "seat_left_up", "seat_facing", "seat_right_up", "seat_right_down"];
        play_cards_ids = ["pcard_mine", "pcard_left_down", "pcard_left_up", "pcard_facing", "pcard_right_up", "pcard_right_down"];
    }
    for (i=0; i<seat_ids.length; i++) {
        seats[i] = document.getElementById(seat_ids[i]);
        seats[i].style.visibility = "visible";
        play_cards[i] = document.getElementById(play_cards_ids[i]);
        play_cards[i].style.visibility = "visible";
    }
}

function bid_button_click(bid_button) {
    gameSocket.send("bdpt:" + bid_button.id.substring(4));
    bid_window.style.visibility = "hidden";
}

function selectMyCard(card) {
    card.style.top = "0%";
    dragCard = document.getElementById("my_drag_card");
    dragCardShow = "hidden";

    if (selectedCard != null)
        selectedCard.style.top = "20%";
    if (selectedCard == card)
        selectedCard = null;
    else {
        selectedCard = card;
        dragCardShow = "visible";
        dragCard.style.left = selectedCard.style.left;
        dragCard.style.width = selectedCard.style.width;
    }
    dragCard.style.visibility = dragCardShow;
}

function dragMyCard(event) {
    event.dataTransfer.setData("Text", event.target.id);
}

function dropMyCard(event) {
    allowDrop(event);
    if (selectedCard == null)
        return;
    newNeighborCard = event.target.parentElement;
     
    newPos = parseInt(newNeighborCard.style.left.replace("%", ""));
    oldPos = parseInt(selectedCard.style.left.replace("%", ""));
    newzIndex = newNeighborCard.style.zIndex;
    oldzIndex = selectedCard.style.zIndex;

    moveDirection = 1; //1 for left, -1 for right
    if (newzIndex > oldzIndex)
        moveDirection = -1;

    cardShiftPos = ((newPos - oldPos)/ (newzIndex - oldzIndex)) * moveDirection;

    var children = newNeighborCard.parentElement.children;
    for (var i = 0; i < children.length; i++) {
      var card = children[i];
      if (card.id == "my_drag_card")
        continue;
      if ((card.style.zIndex >= newzIndex && card.style.zIndex < oldzIndex) || (card.style.zIndex <= newzIndex && card.style.zIndex > oldzIndex)) {
        card.style.left = (parseInt(card.style.left.replace("%", "")) + cardShiftPos) + "%";
        card.style.zIndex = parseInt(card.style.zIndex) + moveDirection;
      }
    }
    selectedCard.style.left = newPos + "%";
    selectedCard.style.zIndex = newzIndex;
    dragCard = document.getElementById("my_drag_card");
    dragCard.style.left = newPos + "%";
}

function allowDrop(event) {
    event.preventDefault();
}

function addCardsToHand(card_names) {
    cards = card_names.split(",");
    myCards = document.getElementById("my_cards");
    cardCount = myCards.children.length - 1;

    for (var i=0; i<cards.length; i++) {
        newCard = document.getElementById("card_template").cloneNode(true);
        newCard.id = "card_" + (cardCount + i + 1)
        newCard.style.left = "" + ((cardCount + i + 1) * 5) + "%";
        newCard.style.zIndex = "" + (i + 1);
        newCard.style.visibility = "visible";
        newCard.children[0].innerHTML = cards[i]
        myCards.appendChild(newCard);
    }
}

function createCard(card_name) {
    newCard = document.getElementById("card_template").cloneNode(true);
    newCard.children[0].innerHTML = card_name;
    newCard.style.visibility = "visible";

    return newCard
}

function addNewCards(cards) {
    myCards = document.getElementById("my_cards");
    cardCount = myCards.children.length - 1;
    //newCardHtml = '<div id="my_card_1" class="my_card_holder my_card_1" onclick="selectMyCard(this)" ondblclick="" ondrop="dropMyCard(event, this)" ondragover="allowDrop(event)"></div>';

    //newCard = document.createElement(newCardHtml);
    newCard = document.getElementById("card_BK").cloneNode(true);
    newCard.id = "card_1"
    newCard.style.left = "5%";
    newCard.style.zIndex = "1";
    newCard.style.visibility = "visible";
    myCards.appendChild(newCard);
    // newCard.children[0].innerHTML = "BA"
}

var dragCardClickTimeoutId = null;
function dragCardClick(event) {
    if (selectedCard == null)
        return;
    if (event.type == "dblclick") {
        window.clearTimeout(dragCardClickTimeoutId);
        dragCardClickTimeoutId = null;
        // putMyCard(selectedCard);
        if (my_turn == TurnOptions.KEEP_TRUMP)
            put_aside_trump_card()
        if (my_turn == TurnOptions.PLAY_CARD)
            put_card_in_table()
        else    
            return;
    }
    else if (event.type == "click" && dragCardClickTimeoutId == null)
        dragCardClickTimeoutId = setTimeout("selectMyCard(selectedCard); dragCardClickTimeoutId = null;", 500);

//document.getElementById("game_controls").innerHTML += event.type + "\n";
}

function put_aside_trump_card() {
    trump_holder = document.getElementById("trump_holder");
    gameSocket.send("trmd:" + selectedCard.children[0].innerHTML);
    myCards = document.getElementById("my_cards");
    trump_holder.appendChild(selectedCard);
    selectMyCard(selectedCard);    
    my_turn = TurnOptions.NOT_MY_TURN;
}

function put_card_in_table() {
    gameSocket.send("card:" + selectedCard.children[0].innerHTML);
    myCards = document.getElementById("my_cards");
    play_cards[0].appendChild(selectedCard);
    selectMyCard(selectedCard);
    my_turn = TurnOptions.NOT_MY_TURN;
}

function putMyCard(card) {
// player4Card = document.getElementById("player_4_card");
//cardImg = player4Card.getElementById("card_img");

// player4Card.removeChild(player4Card.children[0]);
// player4Card.appendChild(card);
cardCarrier_1 = document.getElementById("card_carrier_1");
player4Card = document.getElementById("player_4_card");
cardCarrier_1.source = card;
cardCarrier_1.destination = player4Card;

cardCarrier_1.addEventListener("animationstart", listener_animation, false);
cardCarrier_1.addEventListener("animationend", listener_animation, false);

cardCarrier_1.classList.toggle("drop_card_anim");
}

function listener_animation(event) {
switch(event.type) {
    case "animationstart":
        cardCarrier_1 = event.target;
        card = event.target.source;
        cardCarrier_1.innerHTML = "";
        cardCarrier_1.appendChild(card.children[0])
        cardPos = card.getBoundingClientRect()
        cardCarrier_1.style.top = cardPos.top + "px"
        cardCarrier_1.style.left = cardPos.left + "px"
        card.parentElement.removeChild(card)
        break
    case "animationend":
        player4Card = event.target.destination;
        player4Card.innerHTML = "";
        player4Card.appendChild(event.target.children[0]);

        //cardCarrier_1 = document.getElementById("card_carrier_1");
        event.target.classList.toggle("drop_card_anim");
    break;
}
}

function index_from_seat(seat_no) {
    player_index = seat_no - my_seat;
    if (player_index < 0)
        player_index = total_seats + player_index;

    return player_index;
}

function assign_player_to_seat(name, seat_no) {
    player_index = index_from_seat(seat_no);

    new_player = document.getElementById("player_template").cloneNode(true);
    new_player.children["player_name"].innerHTML = name;

    seats[player_index].appendChild(new_player);
    seats[player_index].name = name;

    display_message(`${name} is playing from seat ${seat_no + 1}`);
}

function keep_trump_card() {
    gameSocket.send("trmd:");
}

//---------------------------------------------------------------------------------
var gameSocket = null;
MSG_SEP = ":";
msg_handlers = {
    "chat": display_message,
    "newp": update_new_player,
    "seat": update_players_seating,
    "stat": show_status_popup,
    "deal": deal_cards,
    "shbd": bid_points,
    "ktrm": keep_trump_card,
    "play": play_card,
    "plyd": show_played_card,
    "rdwn": cleanup_round,
}

function initiate_connection(my_table, my_name) {
    gameSocket = new WebSocket("ws://ec2-3-134-97-118.us-east-2.compute.amazonaws.com:8000?player=" + my_name + "&table=" + my_table);

    gameSocket.onmessage = function (event) {
        onMessageRecievedSuccess(event.data);
    }
}

function sendChatMessage() {
    chat_msg = document.getElementById("chat_input").value;
    if (chat_msg[4] == ':')
        gameSocket.send(chat_msg);
    else
        gameSocket.send("chat:" + chat_msg);
    document.getElementById("chat_input").value = "";
}

function onMessageRecievedSuccess(data) {
    msg_type = data.slice(0, 4);
    if (msg_handlers[msg_type] != null) {
        msg_handlers[msg_type](data.slice(5).split(MSG_SEP));
    }
    else
        display_message(data);
}

function display_message(msg) {
    newMsg = "<span style='color:blue'>Game28:</span> <span style='color:black'>" + msg  + "</span><br>"
    msg_win = document.getElementById("new_messages")
    msg_win.innerHTML += newMsg;
    msg_win.scrollTop = msg_win.scrollHeight;
}

function save_my_seat(status, seat_no) {
    active = (status == ACTIVE_PLAYER);
    if (my_seat == seat_no && active_playing == active)
        return;
    active_playing = active;
    my_seat = seat_no;
    seats[0].name = my_name;
    if (active_playing)
        display_message(`Playing as ${my_name} in seat ${my_seat + 1}`)
    else
        display_message(`Viewing the game from seat ${my_seat + 1}`)
}

function update_new_player(newp_info) {
    new_player_name = newp_info[0];
    new_player_status = parseInt(newp_info[1])
    new_player_seat_no = parseInt(newp_info[2]);

    if (new_player_name == my_name) {
        if (new_player_status == ACTIVE_PLAYER)
            gameSocket.send("redy:");
        return save_my_seat(new_player_status, new_player_seat_no);
    }
    if (new_player_status != ACTIVE_PLAYER)
        return display_message(`${new_player_name} joined as a spectator`);
    assign_player_to_seat(new_player_name, new_player_seat_no);
}

function update_players_seating(seat_info) {
    for (i=0; i<seat_info.length; i+=3) {
        if (seat_info[i] == my_name) {
            save_my_seat(parseInt(seat_info[i+1]), parseInt(seat_info[i+2]));
            break;
        }
    }
    for (i=0; i<seat_info.length; i+=3) {
        if (seat_info[i] != my_name && parseInt(seat_info[i+1]) == ACTIVE_PLAYER)
            assign_player_to_seat(seat_info[i], parseInt(seat_info[i+2]));
    }
}

function show_status_popup(game_info) {
    gameSocket.send("strt:");
}

function deal_cards(game_info) {
    display_message(`Got cards: ${game_info[1]}. Animate from ${game_info[0]}`)
    addCardsToHand(game_info[1]);
    gameSocket.send("delt:");
}

function bid_points(game_info) {
    //todo: disable buttons
    bid_window.style.visibility = "visible";
    //display_message(`Bidding ${parseInt(game_info[0]) + 1} points`)
    //gameSocket.send("bdpt:" + (parseInt(game_info[0]) + 1));
}

function keep_trump_card(game_info) {
    my_turn = TurnOptions.KEEP_TRUMP;
    // display_message(`Keeping Trump card`)
    // gameSocket.send("trmd:");
}

function play_card(game_info) {
    my_turn = TurnOptions.PLAY_CARD;
    // display_message(`Keeping Trump card`)
    // gameSocket.send("trmd:");
}

function show_played_card(game_info) {
    seat_no = index_from_seat(parseInt(game_info[0]))
    // display_message(`${seats[seat_no].name} played ${game_info[1]} card`)
    if(seat_no != 0) //my seat
        play_cards[seat_no].appendChild(createCard(game_info[1]))
}

function cleanup_round(game_info) {
    seat_no = index_from_seat(parseInt(game_info[0]))
    display_message(`This round goes to ${seats[seat_no].name}`)

    for (i=0; i<play_cards.length; i++) {
        play_cards[i].removeChild(play_cards[i].childNodes[0])
    }
}
