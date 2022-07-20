import socket

HOST = "0.0.0.0"
PORT = 6379
BLOOM_FILTER_KEY = "matrix"
RESPONSE_TERMINATOR="\r\n"
OK_RESPONSE = f"+OK{RESPONSE_TERMINATOR}"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    # This only listens in a way that one client can connect...
    while True:
        conn, addr = s.accept()

        with conn:
            while True:
                data = conn.recv(2048)

                if not data:
                    break

                request = data.decode().split(RESPONSE_TERMINATOR)
                print(request)

                # We don't need the first two parts.
                request = request[2::]

                # We don't need the final part.
                request.pop()

                # We don't need every other item.
                request = request[::2]

                print(request)

                # Which Redis command is this?
                command = request[0].lower()

                print(command)

                if command == "command":
                    # redis-cli sends command with no arguments when it first connects.
                    if len(request) == 1:
                        response = OK_RESPONSE
                    else:
                        response = f"-ERR wrong number of arguments for 'command' command{RESPONSE_TERMINATOR}"
                elif command == "bf.add":
                    # Key needs to be BLOOM_FILTER_KEY and we need one item.
                    if len(request) == 3 and request[1] == BLOOM_FILTER_KEY:
                        response = OK_RESPONSE
                    elif len(request) == 3:
                        # Wrong key...
                        response = f":0{RESPONSE_TERMINATOR}"
                    else:
                        response = f"-ERR wrong number of arguments for 'bf.add' command{RESPONSE_TERMINATOR}"
                elif command == "bf.exists":
                    # Key needs to be BLOOM_FILTER_KEY and we need one item.
                    if len(request) == 3 and request[1] == BLOOM_FILTER_KEY:
                        response = OK_RESPONSE
                    elif len(request) == 3:
                        # Wrong key...
                        response = f":0{RESPONSE_TERMINATOR}"
                    else:
                        response = f"-ERR wrong number of arguments for 'bf.exists' command{RESPONSE_TERMINATOR}"               
                elif command == "del":
                    # Clear the filter if the key was BLOOM_FILTER_KEY otherwise return 0.
                    if len(request) == 2 and request[1] == BLOOM_FILTER_KEY:
                        response = f":1{RESPONSE_TERMINATOR}"
                    elif len(request) == 2:
                        response = f":0{RESPONSE_TERMINATOR}"
                    else:
                        response = f"-ERR wrong number of arguments for 'del' command{RESPONSE_TERMINATOR}"   
                else:
                    response = f"-ERR unknown command '{command}'{RESPONSE_TERMINATOR}"

                print(f"sending: {response}")
                conn.sendall(bytes(response, 'UTF-8'))