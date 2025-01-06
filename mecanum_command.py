import bluetooth
import keyboard
import time
import argparse


def ascii_art():
    art = """
======================================================================================
                        🚗       M  E  C  A  N  U  M       🚗
======================================================================================
 ___      ___   _______   ______        __      _____  ___   ____  ____  ___      ___
 ___      ___   _______   ______        __      _____  ___   ____  ____  ___      ___ 
|"  \    /"  | /"     "| /" _  "\      /""\    (\    \|"  \ ("  _||_ " ||"  \    /"  |
 \   \  //   |(: ______)(: ( \___)    /    \   |.\    \    ||   (  ) : | \   \  //   |
 /\   \/.    | \/    |   \/ \        /' /\  \  |: \.   \   |(:  |  | . ) /\   \/.    |
|: \.        | // ___)_  //  \ _    //  __'  \ |.  \    \. | \  \__/ // |: \.        |
|.  \    /:  |(:      "|(:   _) \  /   /  \   \|    \    \ | /\  __ //\ |.  \    /:  |
|___|\__/|___| \_______) \_______)(___/    \___)\___|\____\)(__________)|___|\__/|___|
                                                                                                                                                      
======================================================================================
                        🚗    Ready to roll your robot!    🚗
======================================================================================
"""
    print(art)


def command_line(sock):
    print("\nBluetooth terminal (type 'exit' to quit).")
    while True:
        message = input("Enter a message: ")
        if message.lower() == "exit":
            break
        sock.send(f"{message}\n")
        print(f"Message sent: {message}")
    sock.close()
    print("Disconnected.")


def zqsd(sock):
    print("\nBluetooth terminal (type 'exit' to quit).")
    last_command = None

    while True:
        if keyboard.is_pressed("z") and last_command != "z":
            sock.send("forward\n")
            print("forward")
            last_command = "z"

        elif keyboard.is_pressed("s") and last_command != "s":
            sock.send("backward\n")
            print("backward")
            last_command = "s"

        elif keyboard.is_pressed("q") and last_command != "q":
            sock.send("left\n")
            print("left")
            last_command = "q"

        elif keyboard.is_pressed("d") and last_command != "d":
            sock.send("right\n")
            print("right")
            last_command = "d"

        elif keyboard.is_pressed("esc"):
            break

        else:
            if last_command != "stop":
                sock.send("stop\n")
                last_command = "stop"
        time.sleep(0.1)
    sock.close()
    print("Disconnected.")


MODES = [
    {"name": "Command line", "description": "", "function": command_line},
    {"name": "Z Q S D", "description": "", "function": zqsd},
]


def list_devices():
    print("Searching for Bluetooth devices...")
    for i in range(2):
        nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
        if i == 1 and not nearby_devices:
            print("No Bluetooth devices found.")
            return []
    print("\nDetected Bluetooth devices:")
    for i, (addr, name) in enumerate(nearby_devices, start=1):
        print(f"[{i}] {name} - {addr}")
    return nearby_devices


def ask_number(max: int) -> int:
    while 1:
        try:
            choice = int(
                input("\nEnter the number of the device to select (0 to cancel): ")
            )
            if choice == 0:
                print("Operation canceled.")
            if choice <= max:
                return choice
            else:
                print("Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def connect_to_device(address):
    port = 1
    try:
        print(f"Connecting to device at address {address}...")
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((address, port))
        print("Connection successful!")
        return sock
    except bluetooth.BluetoothError as e:
        print(f"Connection error: {e}")
        return None


def mode_choice(sock):
    for i, j in enumerate(MODES):
        print(f"{[i+1]} {j['name']}")
    choice = ask_number(len(MODES))
    MODES[choice - 1]["function"](sock)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Mecanum", description="Mecanum Bluetooth controller"
    )

    parser.add_argument(
        "-c",
        "--command-line",
        help="""
        Use command line to send messages to the robot.
        Commands:
        - 'forward' to move forward
        - 'backward' to move backward
        - 'left' to move left
        - 'right' to move right
        """,
    )

    parser.add_argument(
        "-z",
        "--zqsd",
        help="""
        Use Z Q S D to move the robot.
        Z: forward
        S: backward
        Q: left
        D: right
        """,
    )

    args = parser.parse_args()

    ascii_art()
    devices = list_devices()
    selected_device = devices[ask_number(len(devices)) - 1]
    if selected_device:
        address, name = selected_device
        print(f"You selected: {name} - {address}")
        sock = connect_to_device(address)
        if sock:
            if args.command_line:
                command_line(sock)
            elif args.zqsd:
                zqsd(sock)
            else:
                mode_choice(sock)
    else:
        print("No device selected. Exiting script.")
