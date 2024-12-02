import socket
import threading
from queue import Queue
from datetime import datetime  # 현재 시간 출력을 위해 추가

def send_messages(group, nicknames, send_queue):
    print('Send Thread Started')
    while True:
        try:
            message = send_queue.get()
            if isinstance(message, str) and message == 'Group Changed':
                print('Group Changed')
                continue
            if isinstance(message, tuple) and message[0] == "KICK":  # 강퇴 처리
                sender_conn, target_nickname = message[1], message[2]
                sender_nickname = nicknames.get(sender_conn, "Unknown")
                if sender_nickname == target_nickname:  # 자기 자신 강퇴 방지
                    sender_conn.send("You cannot kick yourself.".encode())
                    continue
                # 강퇴 대상 소켓 찾기
                target_conn = None
                for conn, nickname in nicknames.items():
                    if nickname == target_nickname:
                        target_conn = conn
                        break
                if target_conn:
                    try:
                        target_conn.send("You have been kicked from the chat.".encode())
                        target_conn.close()
                    except:
                        pass
                    if target_conn in group:
                        group.remove(target_conn)
                    if target_conn in nicknames:  # nicknames에 존재하는지 확인
                        del nicknames[target_conn]
                    print(f"{target_nickname} has been kicked.")
                    for other_conn in group:
                        try:
                            other_conn.send(f"{target_nickname} has been kicked from the chat.".encode())
                        except:
                            pass
                else:
                    sender_conn.send(f"User '{target_nickname}' not found.".encode())
            elif isinstance(message, tuple) and message[0] == "WHISPER":  # 귓속말 처리
                sender_conn, target_nickname, whisper_message = message[1:]
                sender_nickname = nicknames.get(sender_conn, "Unknown")
                target_conn = None
                for conn, nickname in nicknames.items():
                    if nickname == target_nickname:
                        target_conn = conn
                        break
                if target_conn:
                    try:
                        current_time = datetime.now().strftime("%H:%M")
                        target_conn.send(f'[{current_time}] [Whisper from {sender_nickname}] {whisper_message}'.encode())
                        sender_conn.send(f'[{current_time}] [Whisper to {target_nickname}] {whisper_message}'.encode())
                    except:
                        sender_conn.send("Failed to send whisper.".encode())
                else:
                    sender_conn.send(f"User '{target_nickname}' not found.".encode())
            else:
                sender_nickname = nicknames.get(message[1], "Unknown")
                current_time = datetime.now().strftime("%H:%M")  # 현재 시간 가져오기
                for conn in group:
                    if conn != message[1]:
                        try:
                            conn.send(f'[{current_time}] {sender_nickname} >> {message[0]}'.encode())
                        except:
                            pass
        except Exception as e:
            print(f"Error in send_messages: {e}")

def receive_messages(conn, client_id, nicknames, send_queue, group):
    print(f'Receive Thread {client_id} Started')
    try:
        while True:
            nickname = conn.recv(1024).decode()  # 클라이언트로부터 닉네임 수신
            if nickname in nicknames.values():  # 닉네임 중복 확인
                conn.send("Nickname already taken. Please choose another.".encode())
            else:
                nicknames[conn] = nickname  # 닉네임 저장
                break

        print(f'Client {client_id} joined as "{nickname}"')
        conn.send(f'Welcome {nickname}! You can start chatting.'.encode())

        # 새로운 클라이언트 접속 알림
        for other_conn in group:
            if other_conn != conn:  # 본인 제외
                try:
                    other_conn.send(f'User "{nickname}" has joined the chat.'.encode())
                except:
                    pass

        while True:
            try:
                data = conn.recv(1024).decode()
                if data.startswith("/whisper"):  # 귓속말 명령 처리
                    _, target_nickname, whisper_message = data.split(maxsplit=2)
                    send_queue.put(("WHISPER", conn, target_nickname, whisper_message))
                elif data == "/user":  # 사용자 목록 조회 명령
                    user_list = ', '.join(nicknames.values())
                    conn.send(f'Users in chat: {user_list}'.encode())
                elif data.startswith("/rename"):  # 별명 변경 명령
                    _, new_nickname = data.split(maxsplit=1)
                    if new_nickname in nicknames.values():
                        conn.send("Nickname already taken. Please choose another.".encode())
                    else:
                        old_nickname = nicknames[conn]
                        nicknames[conn] = new_nickname
                        conn.send(f'Nickname successfully changed to "{new_nickname}".'.encode())
                        print(f'User "{old_nickname}" changed their nickname to "{new_nickname}".')
                        # 변경 사실을 다른 사용자들에게 알림
                        for other_conn in group:
                            if other_conn != conn:
                                try:
                                    other_conn.send(f'User "{old_nickname}" has changed their nickname to "{new_nickname}".'.encode())
                                except:
                                    pass
                elif client_id == 1 and data.startswith("/kick"):  # 클라이언트 1만 강퇴 가능
                    _, target_nickname = data.split(maxsplit=1)
                    send_queue.put(("KICK", conn, target_nickname))
                else:
                    send_queue.put([data, conn])
            except (ConnectionAbortedError, ConnectionResetError):
                break
    except (ConnectionAbortedError, ConnectionResetError) as e:
        print(f"Connection error for client {client_id}: {e}")
    finally:
        # 연결 종료 처리
        if conn in nicknames:  # nicknames에 존재하는지 확인
            left_nickname = nicknames[conn]
            print(f'{left_nickname} disconnected.')
            if conn in group:  # group에 존재하는지 확인
                group.remove(conn)
            del nicknames[conn]  # 안전하게 삭제
            # 클라이언트 나간 사실 알림
            for other_conn in group:
                try:
                    other_conn.send(f'User "{left_nickname}" has left the chat.'.encode())
                except:
                    pass
        conn.close()

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
        try:
            client_id += 1
            conn, addr = server_sock.accept()
            group.append(conn)
            print(f'Connected {addr}')

            if client_id > 1:
                send_queue.put('Group Changed')
                threading.Thread(target=send_messages, args=(group, nicknames, send_queue,)).start()
            else:
                threading.Thread(target=send_messages, args=(group, nicknames, send_queue,)).start()

            threading.Thread(target=receive_messages, args=(conn, client_id, nicknames, send_queue, group)).start()
        except Exception as e:
            print(f"Server error: {e}")
