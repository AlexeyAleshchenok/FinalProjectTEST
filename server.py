import socket
import os
import threading

IP = '0.0.0.0'
PORT = 80
QUEUE_SIZE = 10
SOCKET_TIMEOUT = 5
OK = 'HTTP/1.1 200 OK\r\nContent-Length: '
HEADER_END = '\r\n\r\n'
FILE_SIZES = {"50MB.zip": 50, "100MB.zip": 100, "200MB.zip": 200, "250MB.zip": 250}


def create_test_file(file, size):
    file_name = file
    with open(file_name, "wb") as f:
        f.write(os.urandom(size * 1024 * 1024))
    with open(file_name, "rb") as f:
        file_data = f.read()
    return file_data


def receive(client_socket):
    data = b''
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        data += chunk
        if len(chunk) < 1024:
            break
    return data


def handle_client(client_socket):
    print('Client connected')
    while True:
        try:
            client_request = receive(client_socket)
            if client_request != b'':
                file = client_request.split(b' ')[1][1:].decode()
                test_file = create_test_file(file, FILE_SIZES[file])
                http_headers = OK + str(len(test_file)) + HEADER_END
                client_socket.sendall(http_headers.encode() + test_file)
            else:
                break
        except socket.timeout:
            break
    print('Closing connection')
    client_socket.close()


def main():
    """Main function"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)
        while True:
            client_socket, client_address = server_socket.accept()
            print(f'New connection with {client_address}')
            client_socket.settimeout(SOCKET_TIMEOUT)
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except socket.error as err:
        print('Received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
