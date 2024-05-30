from scapy.all import sr1, IP, ICMP
import socket
import time
import math

FILE_SIZE = {50: '50MB.zip', 100: '100MB.zip', 200: '200MB.zip', 250: '250MB.zip'}
STABILIZATION = {50: 20.5, 100: 20, 200: 19, 250: 18.75, 500: 17.75}
PING_HOST = 'google.com'
SERVER_IP = '127.0.0.1'
PORT = 80


def receive_data(my_socket):
    data = b''
    while True:
        data += my_socket.recv(1024)
        if b'\r\n\r\n' in data:
            break
    headers = data.split(b'\r\n')
    content_len = 0
    for i in range(len(headers)):
        if headers[i].startswith(b'Content-Length:'):
            content_len = int(headers[i].split(b' ')[1].decode())
    while len(data) <= content_len:
        data += my_socket.recv(1024 * 1024)
    end_time = time.perf_counter()
    return content_len, end_time


class NetworkDataCollector:

    def __init__(self, file_size, count=10):
        self.count = count
        self.file_size = file_size
        self.ping_results = []
        self.bandwidth_results = []

    def get_bandwidth_results(self):
        return self.bandwidth_results

    def ping(self):
        try:
            for i in range(self.count + 1):
                packet = IP(dst=PING_HOST) / ICMP()
                start_time = time.perf_counter()
                reply = sr1(packet, timeout=2, verbose=False)
                end_time = time.perf_counter()

                if reply:
                    delay = math.ceil((end_time - start_time) * 1000)
                    self.ping_results.append({'delay': delay, 'loss': 0})
                else:
                    self.ping_results.append({'delay': 0, 'loss': 1})
        except Exception as e:
            print(f'Error: {e}')

    def bandwidth(self):
        path = FILE_SIZE[self.file_size]
        for i in range(self.count):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.settimeout(10)
                start_time = time.perf_counter()
                s.connect((SERVER_IP, PORT))
                request = f'GET /{path} HTTP/1.1\r\nHost: {SERVER_IP}\r\n\r\n'
                s.sendall(request.encode())
                data_len, end_time = receive_data(s)
                download_speed = math.ceil((data_len / (end_time - start_time))
                                           / (math.pow(2, STABILIZATION[self.file_size])))
                self.bandwidth_results.append(download_speed)
            except Exception as e:
                print(f'Error: {e}')
            finally:
                s.close()

    def analyze_ping_results(self):
        total_delay = 0
        total_loss = 0

        for res in self.ping_results:
            total_delay += res['delay']
            total_loss += res['loss']

        average_delay = math.ceil(total_delay / len(self.ping_results))
        loss_percentage = math.ceil(total_loss / len(self.ping_results)) * 100
        analysis_results = {'average_delay': average_delay,
                            'total_loss': total_loss,
                            'loss_percentage': loss_percentage}
        return analysis_results

    def analyze_bandwidth_results(self):
        average_speed = math.ceil(sum(self.bandwidth_results) / len(self.bandwidth_results))
        max_speed = max(self.bandwidth_results)
        analysis_results = {'average_speed': average_speed, 'max_speed': max_speed}
        return analysis_results
