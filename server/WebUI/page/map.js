let wsm = new WebSocketManager();
wsm.add_ws("odometer");
wsm.add_handler("odometer", (event) => {
    let data = JSON.parse(event.data);
    x = data[0];
    y = data[1];
    theta = data[2];
    parse_pos();
    set_rob_pos();
});

let rob = document.querySelector(".rob");

let x = 0, y = 0, theta = 0;

function parse_pos() {
    x = Math.min(parseFloat(x) * 4.9633, 1489); // Max width in pixels, adjusted to actual width
    y = Math.min(parseFloat(y) * 5.0, 1000); // Max height in pixels, adjusted to actual height
    theta = parseFloat(theta) * 180 / Math.PI; // Convert radians to degrees
}

function set_rob_pos() {
    if (rob) {
        rob.style.transformOrigin = "top left";
        rob.style.transform = `translate(${x}px, ${y}px) rotate(${theta}deg)`;
    } else {
        console.error('Robot element not found.');
    }
}

let buttons = document.querySelectorAll(".button");
buttons.forEach(button => {
    button.addEventListener("click", () => {
        button_click_effect(button);
    });
});
