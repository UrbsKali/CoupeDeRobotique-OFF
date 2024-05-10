import multiprocessing

from pynput.keyboard import Key, Listener
import time

power_l = 100
power_r = 100

power = 100

def send_data_to_robot(data):
    start_time = time.time()
    process = multiprocessing.Process(target=thread_send_data, args=(data,))
    process.start()


def thread_send_data(data):
    import asyncio

    asyncio.run(send_data(data))


async def send_data(data):
    import websockets as ws
    dat = '{ "msg":' + data + ', "type" : "eval", "sender" : "urbai"}'

    try:
        async with ws.connect(f"ws://rc.local:8080/cmd?sender=urbai", open_timeout=0.1) as websocket:
            await websocket.send(dat, timeout=0.1)
            print(f"Data sent: {dat}")
    except Exception as e:
        print(f"Error while sending data: {e}")


def on_press(key):
    if key not in current_key:
        current_key.append(key)
    else:
        return

    power_r = 200 if Key.shift in current_key else 100
    power_l = 200 if Key.shift in current_key else 100
    power = 255 if Key.shift in current_key else 100
    
    dir = [0,0]
    
        
    
    match key:
        case Key.esc:
            return False
        case Key.up:
            send_data_to_robot(f"self.robot.vroum({power}, True)")
        case Key.down:
            send_data_to_robot(f"self.robot.vroum({power}), False")
        case Key.left:
            send_data_to_robot(f"self.robot.rotate({power}, True)")
        case Key.right:
            send_data_to_robot(f"self.robot.rotate({power}, False)")
        case 'o':
            send_data_to_robot(f"self.robot.l_motor({power}, True)")
        case 'p':
            send_data_to_robot(f"self.robot.r_motor({power}, True)")
        case 'l':
            send_data_to_robot(f"self.robot.l_motor({power}, False)")
        case 'm':
            send_data_to_robot(f"self.robot.r_motor({power}, False)")
        
        case 'z':
            send_data_to_robot(f"self.robot.l_motor({power_l}, True)")
            send_data_to_robot(f"self.robot.r_motor({power_r}, True)")
        case 'q':
            send_data_to_robot(f"self.robot.l_motor({power_l}, True)")
            send_data_to_robot(f"self.robot.r_motor({power_r+50}, True)")
        case 's':
            send_data_to_robot(f"self.robot.l_motor({power_l}, False)")
            send_data_to_robot(f"self.robot.r_motor({power_r}, False)")
        case 'd':
            send_data_to_robot(f"self.robot.l_motor({power_l+50}, True)")
            send_data_to_robot(f"self.robot.r_motor({power_r}, True)")
            

def on_release(key):
    if key in current_key:
        current_key.remove(key)
    match key:
        case Key.esc:
            return False
        case Key.shift:
            power_l = 100
            power_r = 100
            power = 100
        case _:
            send_data_to_robot("self.robot.stop()")


if __name__ == "__main__":
    # Import from common
    current_key = []
    print("Press ESC to stop.")
    # Collect events until released
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
