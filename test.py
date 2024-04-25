import socket
import time

host = 'speedtest.tele2.net'
port = 80
path = '/50MB.zip'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
request = f'GET /{path} HTTP/1.1\r\nHost: {host}\r\n\r\n'

send_time_start = time.perf_counter()
sock.sendall(request.encode())
send_time_end = time.perf_counter()
send_time = send_time_end - send_time_start

time_list = []
for i in range(50):
    download_time_start = time.perf_counter()
    chunk = sock.recv(1024 * 1024)
    download_time_end = time.perf_counter()
    time_list.append(download_time_end - download_time_start)
sock.close()
time = sum(time_list) / len(time_list) + send_time
speed = 1 / time * 8
print(time)
print(speed)
