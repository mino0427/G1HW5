import socket
import threading
from datetime import datetime

def log_message(nickname, message):
    """채팅 내용을 로그 파일에 기록"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_filename = f"{nickname}_chat_log.txt"  # 닉네임 기반 로그 파일 생성
    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def send_messages(client_sock, nickname):
    while True:
        message = input()
        client_sock.send(message.encode())
        log_message(nickname, f"Me: {message}")  # 보낸 메시지를 로그에 기록

def receive_messages(client_sock, nickname):
    while True:
        try:
            data = client_sock.recv(1024).decode()
            print(data)
            log_message(nickname, data)  # 받은 메시지를 로그에 기록
        except:
            print("Disconnected from server.")
            client_sock.close()
            break

if __name__ == '__main__':
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Host = '34.68.170.234'
    # Host = '127.0.0.1'
    Port = 9000
    client_sock.connect((Host, Port))
    print(f'Connecting to {Host} {Port}')

    nickname = input("Enter your nickname: ")  # 닉네임 입력
    client_sock.send(nickname.encode())  # 서버에 닉네임 전송

    threading.Thread(target=send_messages, args=(client_sock, nickname)).start()
    threading.Thread(target=receive_messages, args=(client_sock, nickname)).start()
