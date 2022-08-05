import socket

PROTOCOL_TERMINATOR = "\r\n"

key_space = {}

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

                if command == "sadd":
                    new_set_members = request[2::]
                    try:
                        old_set_cardinality = len(key_space[key_name])
                        key_space[key_name].update(new_set_members)
                    except KeyError:
                        old_set_cardinality = 0
                        key_space[key_name] = set(new_set_members)

                    new_set_cardinality = len(key_space[key_name])

                    print(key_space[key_name])
                    response = f":{new_set_cardinality - old_set_cardinality}{PROTOCOL_TERMINATOR}"
                elif command == "sismember":
                    member_to_check = request[2]
                    is_member = 0

                    try:
                        if member_to_check in key_space[key_name]:
                            is_member = 1
                    except KeyError:
                        pass
                        
                    response = f":{is_member}{PROTOCOL_TERMINATOR}"
                elif command == "scard":
                    try:
                        set_cardinality = len(key_space[key_name])
                    except KeyError:
                        set_cardinality = 0

                    response = f":{set_cardinality}{PROTOCOL_TERMINATOR}"            
                else:
                    response = f"+OK{PROTOCOL_TERMINATOR}"


            print(f"sending: {response}")
            conn.sendall(bytes(response, 'UTF-8'))