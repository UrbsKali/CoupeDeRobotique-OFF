import multiprocessing
from websockets.client import connect
from pynput.keyboard import Key, Listener
import time

power_l = 100
power_r = 100

power = 100

# create ws


async def send_data(data, ws):
    dat = '{ "data": "' + data + '", "msg" : "eval", "sender" : "urbai", "ts":"12334"}'
    print(dat)

    try:
        await ws.send(dat)
        print(f"Data sent: {dat}")
    except Exception as e:
        print(f"Error while sending data: {e}")


def on_press(key):
    if key not in current_key:
        current_key.append(key)
    if key == Key.esc:
        return False

def on_release(key):
    if key in current_key:
        current_key.remove(key)
    if key == Key.esc:
        # Stop listener
        return False



async def mainloop():
    websocket = await connect("ws://rc.local:8080/cmd?sender=urbai")
    while True:
        power_r = 200 if Key.shift in current_key else 100
        power_l = 200 if Key.shift in current_key else 100
        power = 255 if Key.shift in current_key else 100

        dir = [0, 0]
        
        

        for key in current_key:
            if key not in old_current_key:
                print(f"Key pressed: {key}")
                old_current_key.append(key)
            else: 
                continue
            match key:
                case Key.esc:
                    return False
                case Key.up:
                    await send_data(f"self.robot.vromm({power}, True)", websocket)
                case Key.down:
                    await send_data(f"self.robot.vromm({power}), False", websocket)
                case Key.left:
                    await send_data(f"self.robot.rotate({power}, True)", websocket)
                case Key.right:
                    await send_data(f"self.robot.rotate({power}, False)", websocket)
                case "o":
                    await send_data(f"self.robot.l_motor({power}, True)", websocket)
                case "p":
                    await send_data(f"self.robot.r_motor({power}, True)", websocket)
                case "l":
                    await send_data(f"self.robot.l_motor({power}, False)", websocket)
                case "m":
                    await send_data(f"self.robot.r_motor({power}, False)", websocket)

                case "z":
                    await send_data(f"self.robot.l_motor({power_l}, True)", websocket)
                    await send_data(f"self.robot.r_motor({power_r}, True)", websocket)
                case "q":
                    await send_data(f"self.robot.l_motor({power_l}, True)", websocket)
                    await send_data(f"self.robot.r_motor({power_r+50}, True)", websocket)
                case "s":
                    await send_data(f"self.robot.l_motor({power_l}, False)", websocket)
                    await send_data(f"self.robot.r_motor({power_r}, False)", websocket)
                case "d":
                    await send_data(f"self.robot.l_motor({power_l+50}, True)", websocket)
                    await send_data(f"self.robot.r_motor({power_r}, True)", websocket)
                    
                case Key.ctrl_l:
                    await send_data(f"self.robot.stop()", websocket)
        for key in old_current_key:
            if key not in current_key:
                print(f"Key released: {key}")
                old_current_key.remove(key)
                await send_data(f"self.robot.stop()", websocket)

if __name__ == "__main__":
    import asyncio
    # Import from common
    current_key = []
    old_current_key = []
    print("Press ESC to stop.")
    # Collect events until released
    with Listener(on_press=on_press, on_release=on_release) as listener:
        asyncio.run(mainloop())
        listener.join()


