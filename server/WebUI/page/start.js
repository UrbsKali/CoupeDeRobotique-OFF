let wsm = new WebSocketManager();
wsm.add_ws("cmd");

let blue = document.querySelectorAll(".blue");
let yellow = document.querySelectorAll(".yellow");

let blue_pos = [[380, 30], [1670, 430], [380, 820]];
let yellow_pos = [[1670, 30], [380, 430], [1670, 820]];

for (let i = 0; i < blue_pos.length; i++) {

    blue[i].addEventListener("click", function (event) {
        console.log("click on blue n°" + i);
        wsm.send("cmd", "zone", i);
    });
    yellow[i].addEventListener("click", function (event) {
        console.log("click on yellow n°" + i);
        wsm.send("cmd", "zone", i+3);
    });

    // set the initial position
    blue[i].style.left = blue_pos[i][0] + "px";
    blue[i].style.top = blue_pos[i][1] + "px";
    yellow[i].style.left = yellow_pos[i][0] + "px";
    yellow[i].style.top = yellow_pos[i][1] + "px";
}