import socket
import threading
from queue import Queue

def send_messages(group, send_queue):
    print('Send Thread Started')
    while True:
        try:
            message = send_queue.get()
            if message == 'Group Changed':
                print('Group Changed')
                break
            for conn in group:
                msg = f'Client{message[2]} >> {message[0]}'
                if message[1] != conn:
                    conn.send(msg.encode())
        except:
            pass

def receive_messages(conn, client_id, send_queue):
    print(f'Receive Thread {client_id} Started')
    while True:
        data = conn.recv(1024).decode()
        send_queue.put([data, conn, client_id])

if __name__ == '__main__':
    send_queue = Queue()
    HOST = ''
    PORT = 9000
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen(10)
    client_id = 0
    group = []
    while True:
        client_id += 1
        conn, addr = server_sock.accept()
        group.append(conn)
        print(f'Connected {addr}')

        if client_id > 1:
            send_queue.put('Group Changed')
            threading.Thread(target=send_messages, args=(group, send_queue,)).start()
        else:
            threading.Thread(target=send_messages, args=(group, send_queue,)).start()

        threading.Thread(target=receive_messages, args=(conn, client_id, send_queue,)).start()
