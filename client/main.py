import multiprocessing

from pynput.keyboard import Key, Listener
import time

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

    try:
        async with ws.connect(f"ws://rc.local:8080/cmd", open_timeout=0.1) as websocket:
            await websocket.send(data, timeout=0.1)
            print(f"Data sent: {data}")
    except Exception as e:
        print(f"Error while sending data: {e}")


def on_press(key):
    if key not in current_key:
        current_key.append(key)
    else:
        return

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
        case Key.shift:
            power = 255
        case 'a':
            send_data_to_robot(f"self.robot.l_motor({power}, True)")
        case 'z':
            send_data_to_robot(f"self.robot.r_motor({power}, True)")
        case 'q':
            send_data_to_robot(f"self.robot.l_motor({power}, False)")
        case 's':
            send_data_to_robot(f"self.robot.r_motor({power}, False)")
            

def on_release(key):
    if key in current_key:
        current_key.remove(key)
    match key:
        case Key.esc:
            return False
        case Key.shift:
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
