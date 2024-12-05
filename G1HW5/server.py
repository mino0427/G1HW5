import socket
import threading
from queue import Queue
from datetime import datetime
import time

# 로그 파일 설정
log_file_path = "server.txt"
log_lock = threading.Lock()

def log_message(message):
    """로그 메시지를 파일과 콘솔에 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    formatted_message = f"[{timestamp}] {message}\n"
    print(formatted_message.strip())  # 콘솔 출력
    with log_lock:
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(formatted_message)  # 파일 기록

def send_messages(group, nicknames, send_queue):
    log_message('Send Thread Started')
    while True:
        try:
            message = send_queue.get()
            if isinstance(message, str) and message == 'Group Changed':
                log_message('Group Changed')
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
                    log_message(f"{target_nickname} has been kicked.")
                    for other_conn in group:
                        try:
                            other_conn.send(f"{target_nickname} has been kicked from the chat.".encode())
                        except:
                            pass
                else:
                    sender_conn.send(f"User '{target_nickname}' not found.".encode())
            elif isinstance(message, tuple) and message[0] == "SCHEDULED":  # 예약 메시지 처리
                _, sender_nickname, scheduled_message = message
                current_time = datetime.now().strftime("%H:%M")
                log_message(f"[Scheduled by {sender_nickname}] {scheduled_message}")
                for conn in group:
                    try:
                        conn.send(f'[{current_time}] [Scheduled by {sender_nickname}] {scheduled_message}'.encode())
                    except:
                        pass
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
                        log_message(f"[Whisper] {sender_nickname} -> {target_nickname}: {whisper_message}")
                    except:
                        sender_conn.send("Failed to send whisper.".encode())
                else:
                    sender_conn.send(f"User '{target_nickname}' not found.".encode())
            else:
                sender_nickname = nicknames.get(message[1], "Unknown")
                current_time = datetime.now().strftime("%H:%M")  # 현재 시간 가져오기
                log_message(f"{sender_nickname} >> {message[0]}")
                for conn in group:
                    if conn != message[1]:
                        try:
                            conn.send(f'[{current_time}] {sender_nickname} >> {message[0]}'.encode())
                        except:
                            pass
        except Exception as e:
            log_message(f"Error in send_messages: {e}")

def handle_scheduled_messages(schedule_queue, send_queue, nicknames):
    """예약 메시지를 처리하는 스레드"""
    while True:
        try:
            now = datetime.now().strftime("%H:%M")
            scheduled_tasks = list(schedule_queue.queue)
            for task in scheduled_tasks:
                if task[0] == now:
                    _, sender_conn, message = task
                    sender_nickname = nicknames.get(sender_conn, "Unknown")
                    send_queue.put(("SCHEDULED", sender_nickname, message))
                    schedule_queue.get()  # 작업 제거
            time.sleep(3)  # 3초마다 예약 확인
        except Exception as e:
            log_message(f"Error in handle_scheduled_messages: {e}")

def receive_messages(conn, client_id, nicknames, send_queue, group, schedule_queue):
    log_message(f'Receive Thread {client_id} Started')
    try:
        while True:
            nickname = conn.recv(1024).decode()  # 클라이언트로부터 닉네임 수신
            if nickname in nicknames.values():  # 닉네임 중복 확인
                conn.send("Nickname already taken. Please choose another.".encode())
            else:
                nicknames[conn] = nickname  # 닉네임 저장
                break

        log_message(f'Client {client_id} joined as "{nickname}"')
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
                if data.startswith("/schedule"):  # 예약 메시지 명령 처리
                    try:
                        _, scheduled_time, scheduled_message = data.split(maxsplit=2)
                        # 시간 형식 검증
                        datetime.strptime(scheduled_time, "%H:%M")
                        schedule_queue.put((scheduled_time, conn, scheduled_message))
                        conn.send(f"Message scheduled for {scheduled_time}".encode())
                        log_message(f'{nickname} scheduled a message at {scheduled_time}: {scheduled_message}')
                    except ValueError:
                        conn.send("Invalid time format. Use HH:MM.".encode())
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
                        log_message(f'User "{old_nickname}" changed their nickname to "{new_nickname}".')
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
                    log_message(f'{nickname} requested to kick {target_nickname}')
                else:
                    send_queue.put([data, conn])
            except (ConnectionAbortedError, ConnectionResetError):
                break
    except (ConnectionAbortedError, ConnectionResetError) as e:
        log_message(f"Connection error for client {client_id}: {e}")
    finally:
        # 연결 종료 처리
        if conn in nicknames:  # nicknames에 존재하는지 확인
            left_nickname = nicknames[conn]
            log_message(f'{left_nickname} disconnected.')
            if conn in group:  # group에 존재하는지 확인
                group.remove(conn)
            del nicknames[conn]  # 안전하게 삭제
            # 클라이언트 나간 사실 알림
            for other_conn in group:
                try:
                    other_conn.send(f'User "{left_nickname}" has left the chat.'.encode())
                except:
                    pass
        else:
            log_message(f"Connection {conn} was already removed.")
        conn.close()

if __name__ == '__main__':
    send_queue = Queue()
    schedule_queue = Queue()  # 예약 메시지 큐
    HOST = '0.0.0.0'
    PORT = 9000
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen(10)

    client_id = 0
    group = []
    nicknames = {}  # 닉네임을 저장할 딕셔너리

    # 예약 메시지 처리 스레드 시작
    threading.Thread(target=handle_scheduled_messages, args=(schedule_queue, send_queue, nicknames), daemon=True).start()

    while True:
        try:
            client_id += 1
            conn, addr = server_sock.accept()
            group.append(conn)
            log_message(f'Connected {addr}')

            if client_id > 1:
                send_queue.put('Group Changed')
                threading.Thread(target=send_messages, args=(group, nicknames, send_queue,)).start()
            else:
                threading.Thread(target=send_messages, args=(group, nicknames, send_queue,)).start()

            threading.Thread(target=receive_messages, args=(conn, client_id, nicknames, send_queue, group, schedule_queue)).start()
        except Exception as e:
            log_message(f"Server error: {e}")
