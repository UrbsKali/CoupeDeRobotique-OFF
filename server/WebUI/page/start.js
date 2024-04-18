let wsm = new WebSocketManager();
wsm.add_ws("cmd");

let blue = document.querySelectorAll(".blue");
let yellow = document.querySelectorAll(".yellow");

let blue_pos = [[380, 30], [1670, 430], [380, 820]];
let yellow_pos = [[1670, 30], [380, 430], [1670, 820]];

yellow[0].addEventListener("click", function (event) {
    console.log("click on yellow n°" + 2);
    wsm.send("cmd", "zone", 2);
});

yellow[1].addEventListener("click", function (event) {
    console.log("click on yellow n°" + 4);
    wsm.send("cmd", "zone", 4);
});

yellow[2].addEventListener("click", function (event) {
    console.log("click on yellow n°" + 0);
    wsm.send("cmd", "zone", 0);
});


blue[0].addEventListener("click", function (event) {
    console.log("click on blue n°" + 5);
    wsm.send("cmd", "zone", 5);
});

blue[1].addEventListener("click", function (event) {
    console.log("click on blue n°" + 1);
    wsm.send("cmd", "zone", 1);
});

blue[2].addEventListener("click", function (event) {
    console.log("click on blue n°" + 3);
    wsm.send("cmd", "zone", 3);
});

for (let i = 0; i < blue_pos.length; i++) {
    // set the initial position
    blue[i].style.left = blue_pos[i][0] + "px";
    blue[i].style.top = blue_pos[i][1] + "px";
    yellow[i].style.left = yellow_pos[i][0] + "px";
    yellow[i].style.top = yellow_pos[i][1] + "px";
}