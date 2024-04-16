let ws = new WebSocketManager();
ws.add_ws("cmd");

let kp = document.querySelector("input[name='kp']");
let ki = document.querySelector("input[name='ki']");
let kd = document.querySelector("input[name='kd']");

pid_button = document.querySelector(".pid > .send")


pid_button.addEventListener("click", () => {
    ws.send("cmd", "eval", `self.rolling_basis.set_pid(${kp.value}, ${ki.value}, ${kd.value})`);
})

let x = document.querySelector("input[name='x']");
let y = document.querySelector("input[name='y']");
let z = document.querySelector("input[name='z']");

let max_speed = document.querySelector("input[name='max_speed']");
let npd = document.querySelector("input[name='npd']");
let aea = document.querySelector("input[name='aea']");
let traj_precision = document.querySelector("input[name='traj_precision']");
let correction = document.querySelector("input[name='correction']");
let accel_start_speed = document.querySelector("input[name='accel_start_speed']");
let accel_distance = document.querySelector("input[name='accel_distance']");
let deccel_end_speed = document.querySelector("input[name='deccel_end_speed']");
let deccel_distance = document.querySelector("input[name='deccel_distance']");

let motion_button = document.querySelector(".params > .send")

motion_button.addEventListener("click", () => {
    ws.send("cmd", "eval", `self.rolling_basis.set_motion_params(${x.value}, ${y.value}, ${z.value}, ${max_speed.value}, ${npd.value}, ${aea.value}, ${traj_precision.value}, ${correction.value}, ${accel_start_speed.value}, ${accel_distance.value}, ${deccel_end_speed.value}, ${deccel_distance.value})`);
})