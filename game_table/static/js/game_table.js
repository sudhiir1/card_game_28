selectedCard = null;
dragStart = 0; 
seats = [];

function intializePage(my_table, num_seats, my_name) {
    //addNewCards("");
    setup_table(num_seats);

    initiate_connection(my_table, my_name);
    /*var my_cards = document.getElementById("my_cards"); 
    my_cards.addEventListener("touchstart", dragMyCard, false);
    my_cards.addEventListener("touchend", dropMyCard, false);
    */
}

function setup_table(num_seats) {
    seat_ids = [];
    if (num_seats == 4) {
        seat_ids = ["seat_mine", "seat_left", "seat_facing", "seat_right"];
    }
    else {
        seat_ids = ["seat_mine", "seat_left_down", "seat_left_up", "seat_facing", "seat_right_up", "seat_right_down"];
    }
    for (i=0; i<seat_ids.length; i++) {
        seats[i] = document.getElementById(seat_ids[i]);
        seats[i].style.visibility = "visible";
    }
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

function addNewCards(cards) {
    myCards = document.getElementById("my_cards");
    cardCount = myCards.children.length - 1;
    //newCardHtml = '<div id="my_card_1" class="my_card_holder my_card_1" onclick="selectMyCard(this)" ondblclick="" ondrop="dropMyCard(event, this)" ondragover="allowDrop(event)"></div>';

    //newCard = document.createElement(newCardHtml);
    newCard = document.getElementById("card_CA").cloneNode(true);
    newCard.id = "card_1"
    newCard.style.left = "5%";
    newCard.style.zIndex = "1";
    newCard.style.visibility = "visible";
    myCards.appendChild(newCard);
    
    newCard = document.getElementById("card_BK").cloneNode(true);
    newCard.id = "card_2"
    newCard.style.left = "15%";
    newCard.style.zIndex = "2";
    newCard.style.visibility = "visible";
    myCards.appendChild(newCard);
    
    newCard = document.getElementById("card_BK").cloneNode(true);
    newCard.id = "card_3"
    newCard.style.left = "25%";
    newCard.style.zIndex = "3";
    newCard.style.visibility = "visible";
    myCards.appendChild(newCard);
    
    newCard = document.getElementById("card_BK").cloneNode(true);
    newCard.id = "card_4"
    newCard.style.left = "35%";
    newCard.style.zIndex = "4";
    newCard.style.visibility = "visible";
    myCards.appendChild(newCard);
    
    newCard = document.getElementById("card_CA").cloneNode(true);
    newCard.id = "card_5"
    newCard.style.left = "45%";
    newCard.style.zIndex = "5";
    newCard.style.visibility = "visible";
    myCards.appendChild(newCard);
    
    newCard = document.getElementById("card_BK").cloneNode(true);
    newCard.id = "card_6"
    newCard.style.left = "55%";
    newCard.style.zIndex = "6";
    newCard.style.visibility = "visible";
    myCards.appendChild(newCard);
    
    newCard = document.getElementById("card_CA").cloneNode(true);
    newCard.id = "card_7"
    newCard.style.left = "65%";
    newCard.style.zIndex = "7";
    newCard.style.visibility = "visible";
    myCards.appendChild(newCard);
    
    newCard = document.getElementById("card_BK").cloneNode(true);
    newCard.id = "card_8"
    newCard.style.left = "75%";
    newCard.style.zIndex = "8";
    newCard.style.visibility = "visible";
    myCards.appendChild(newCard);
}

var dragCardClickTimeoutId = null;
function dragCardClick(event) {
    if (selectedCard == null)
        return;
    if (event.type == "dblclick") {
        window.clearTimeout(dragCardClickTimeoutId);
        dragCardClickTimeoutId = null;
        putMyCard(selectedCard);
    }
    else if (event.type == "click" && dragCardClickTimeoutId == null)
        dragCardClickTimeoutId = setTimeout("selectMyCard(selectedCard); dragCardClickTimeoutId = null;", 500);
        
    //document.getElementById("game_controls").innerHTML += event.type + "\n";
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
//---------------------------------------------------------------------------------
var gameSocket = null;

function initiate_connection(my_table, my_name) {
    gameSocket = new WebSocket("ws://ec2-3-134-97-118.us-east-2.compute.amazonaws.com:8000?player=" + my_name + "&table=" + my_table);

    gameSocket.onmessage = function (event) {
        onMessageRecievedSuccess(event.data);
    }
}

function sendChatMessage() { 
    chat_msg = document.getElementById("chat_input").value;
    gameSocket.send(chat_msg);
    document.getElementById("chat_input").value = "";
}
              
function onMessageRecievedSuccess(data) {
    newMsg = "<span style='color:blue'>Game28:</span> <span style='color:black'>" + data  + "</span><br>" 
    document.getElementById("new_messages").innerHTML += newMsg;
}
