import socket
import mmh3
import time
import unicornhat

PROTOCOL_TERMINATOR = "\r\n"
NUM_HASH_FUNCTIONS = 3
COLOR_BIT_SET = (255, 0, 0)
COLOR_BIT_WRITING = (0, 255, 0)
COLOR_BIT_QUERYING = (0, 0, 255) 
NUM_TRANSITIONS = 4

unicornhat.set_layout(unicornhat.AUTO)
unicornhat.rotation(180)
unicornhat.brightness(0.19)
unicorn_width, unicorn_height = unicornhat.get_shape()
unicornhat.off()

NUM_LEDS = unicorn_width * unicorn_height

def get_led_position(led):
    unicorn_width, unicorn_height = unicornhat.get_shape()
    return (led % unicorn_height, led // unicorn_width)

def toggle_leds(leds, transition_color, new_color):
    orig_colors = []

    for led in leds: 
        orig_colors.append(unicornhat.get_pixel(led[0], led[1]))

    for n in range(NUM_TRANSITIONS):
        for l in range(len(leds)):
            this_led = leds[l]
            unicornhat.set_pixel(this_led[0], this_led[1], transition_color[0], transition_color[1], transition_color[2])
        unicornhat.show()
        time.sleep(0.3)
       
        for l in range(len(leds)): 
            this_led = leds[l]
            this_orig_color = orig_colors[l]
            unicornhat.set_pixel(this_led[0], this_led[1], this_orig_color[0], this_orig_color[1], this_orig_color[2])
        unicornhat.show()
        time.sleep(0.3)

        if n == (NUM_TRANSITIONS - 1):
            for l in range(len(leds)):
                this_led = leds[l]
                unicornhat.set_pixel(this_led[0], this_led[1], new_color[0], new_color[1], new_color[2])
                unicornhat.show()

def query_led_status(led):
    pos = get_led_position(led)

    r, g, b = unicornhat.get_pixel(pos[0], pos[1])
    toggle_leds([pos], COLOR_BIT_QUERYING, (r, g, b))

    return not (r == 0 and g == 0 and b == 0) 

def set_led_status(leds):
    led_positions = []

    for led in leds:
        led_positions.append(get_led_position(led))

    toggle_leds(led_positions, COLOR_BIT_WRITING, COLOR_BIT_SET)

def add_to_filter(element):
    leds = []

    may_exist = exists_in_filter(element)

    for n in range(NUM_HASH_FUNCTIONS): 
        led = mmh3.hash(element, n) % NUM_LEDS 
        print(str(led))

        leds.append(led)

    set_led_status(leds)
    return may_exist

def exists_in_filter(element):
    for n in range(NUM_HASH_FUNCTIONS): 
        led = mmh3.hash(element, n) % NUM_LEDS
        print(str(led))

        if (query_led_status(led) == False):
            return False

    return True

def reset_filter():
    for n in range(2):
        unicornhat.set_all(0, 0, 255)
        unicornhat.show()
        time.sleep(0.3)
        unicornhat.off()
        time.sleep(0.3)

    unicornhat.off()
    return True

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 6379))
s.listen()

while True:
    conn, addr = s.accept()

    with conn:
        while True:
            data = conn.recv(2048)

            if not data:
                break
            
            print(data)
            request = data.decode().split(PROTOCOL_TERMINATOR)
            request.pop()
            request = request[2::]
            request = request[::2]
            print(request)

            command = request[0].lower()

            if command == "command":
                response = f"+OK{PROTOCOL_TERMINATOR}"
            else:
                key_name = request[1]

                if command == "bf.add":
                    new_member = request[2]
                    # Add new_member to the bloom filter
                    may_exist = add_to_filter(new_member)
                    # Return int 1 if new_member didn't exist, 0 otherwise
                    if may_exist:
                         response = f":0{PROTOCOL_TERMINATOR}"
                    else:
                        response = f":1{PROTOCOL_TERMINATOR}"
                elif command == "bf.exists":
                    member_to_check = request[2]
                    if exists_in_filter(member_to_check):
                        response = f":1{PROTOCOL_TERMINATOR}"
                    else:
                        response = f":0{PROTOCOL_TERMINATOR}"                                            
                elif command == "bf.madd":
                    new_members = request[2::]
                    may_exist = []

                    for new_member in new_members:
                        if (add_to_filter(new_member)):
                            may_exist.append(0)
                        else:
                            may_exist.append(1)

                    response = f"*{str(len(may_exist))}{PROTOCOL_TERMINATOR}"

                    for r in may_exist:
                        response = f"{response}:{str(r)}{PROTOCOL_TERMINATOR}"
                else:
                    response = f"+OK{PROTOCOL_TERMINATOR}"


            print(f"sending: {response}")
            conn.sendall(bytes(response, 'UTF-8'))