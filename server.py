import socket
import threading
from queue import Queue

def send_messages(group, nicknames, send_queue):
    print('Send Thread Started')
    while True:
        try:
            message = send_queue.get()
            if message == 'Group Changed':
                print('Group Changed')
                break
            sender_nickname = nicknames[message[1]]
            for conn in group:
                if conn != message[1]:  # 보내는 클라이언트를 제외
                    conn.send(f'{sender_nickname} >> {message[0]}'.encode())
        except:
            pass

def receive_messages(conn, client_id, nicknames, send_queue):
    print(f'Receive Thread {client_id} Started')
    nickname = conn.recv(1024).decode()  # 클라이언트가 보낸 닉네임 수신
    nicknames[conn] = nickname  # 닉네임 저장
    print(f'Client {client_id} joined as "{nickname}"')
    conn.send(f'Welcome {nickname}! You can start chatting.'.encode())

    while True:
        try:
            data = conn.recv(1024).decode()
            send_queue.put([data, conn])  # 메시지와 연결 정보 추가
        except:
            # 클라이언트가 연결을 끊으면 그룹에서 제거
            print(f'{nickname} disconnected.')
            del nicknames[conn]
            group.remove(conn)
            conn.close()
            break

if __name__ == '__main__':
    send_queue = Queue()
    HOST = ''
    PORT = 9000
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen(10)

    client_id = 0
    group = []
    nicknames = {}  # 닉네임을 저장할 딕셔너리

    while True:
        client_id += 1
        conn, addr = server_sock.accept()
        group.append(conn)
        print(f'Connected {addr}')

        if client_id > 1:
            send_queue.put('Group Changed')
            threading.Thread(target=send_messages, args=(group, nicknames, send_queue,)).start()
        else:
            threading.Thread(target=send_messages, args=(group, nicknames, send_queue,)).start()

        threading.Thread(target=receive_messages, args=(conn, client_id, nicknames, send_queue,)).start()
