import socket
import threading

def send_messages(client_sock):
    while True:
        message = input()
        client_sock.send(message.encode())

def receive_messages(client_sock):
    while True:
        data = client_sock.recv(1024).decode()
        print(data)

if __name__ == '__main__':
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Host = 'localhost'
    Port = 9000
    client_sock.connect((Host, Port))
    print(f'Connecting to {Host} {Port}')

    threading.Thread(target=send_messages, args=(client_sock,)).start()
    threading.Thread(target=receive_messages, args=(client_sock,)).start()
