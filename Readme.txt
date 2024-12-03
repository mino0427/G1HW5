1조 조원 구성 및 역할

20203043 권수현 - 알고리즘 설계, 구현, 아이디어 제공 및 기능 구현

20203058 남태인 - 알고리즘 설계, 구현, 아이디어 제공 및 기능 구현

20203072 안민호 – 알고리즘 설계, 구현, 아이디어 제공 및 기능 구현

1. 프로그램 구성요소 : server.py, client.py

◆ server.py 구성요소
① send_messages
역할: send_queue에서 메시지를 가져와 전송
기능: 일반 메시지, 강퇴 알림, 예약 메시지, 귓속말 처리

② receive_messages
역할: 클라이언트가 보낸 메시지를 읽고 처리
기능: 일반 메시지 처리, 특수 메시지 처리
- 특수 메시지(/whisper, /kick, /schedule, /user, /rename)

③ handle_scheduled_messages
역할: 예약된 메시지를 확인하고 정해진 시간에 메시지 전송
동작: schedule_queue를 주기적으로 확인하여 예약 시간이 된 메시지를 send_queue로 전달

④ 큐 (send_queue, schedule_queue)
- send_queue: 일반 메시지, 귓속말, 강퇴 알림 등 처리
- schedule_queue: 예약 메시지 저장, 처리

⑤ 딕셔너리 (nicknames)
- 키 : 클라이언트 소켓, 값: 닉네임
- 사용자 식별, 관리

⑥ 리스트 (group)
- 현재 연결된 클라이언트 소켓 저장
- 메시지를 브로드캐스트할 때 사용

◆ client.py 구성요소
① 소켓 설정 (서버와 연결 설정)

② nickname = input(), client_sock.send()
- 닉네임 설정, 고유 닉네임 입력 및 서버에 전송

③ 메시지 송수신 (send_message(client_sock), receive_message(client_sock) )
-send_message(client_sock): 사용자 입력 메시지를 서버로 전송
-receive_message(client_sock): 서버에서 전송된 메시지 수신 및 출력

④ 멀티스레드
- 메시지 송수신을 비동기적으로 처리


2. 소스코드 컴파일 방법 (GCP 사용)

① 구글 클라우드에 접속하여 VM instance를 생성한다.
	지역 : us-central1로 설정
	머신 유형 : e2-micro
	부팅 디스크 : Debian

② 방화벽 규칙을 추가한다
	대상 : 모든 인스턴스 선택
	소스 IP 범위 : 0.0.0.0/0  (모든 IP 주소 허용)
	프로토콜 및 포트 : TCP와 해당 포트를 지정 (port : 9999)

③ 생성된 인스턴스의 SSH를 실행한다.

④ Python과 개발 도구의 패키지들을 설치한다 (Debian 기준)
	sudo apt update
	sudo apt install python3
	sudo apt install python3-pip
	pip install numpy
	pip install numpy scipy
	pip install loguru //Python에서 로그(logging)기능을 제공하는 라이브러리

⑤ 가상환경을 생성하고 활성화한다.
	python3 -m venv myenv(가상환경 이름)
	source myenv/bin/activate //가상환경 활성화

⑥ UPLOAD FILE을 클릭하여 server.py를 업로드한다.
	server.py가 업로드된 디렉터리에서 python3 server.py로 server를 실행한다.

⑦ 로컬에서 powershell 터미널 4개를 열어 python3 client.py로 client 4개를 실행한다. (vscode 터미널에서 실행해도 됨)
	
⑧ server에 4개의 client가 모두 연결되면 프로그램이 실행된다.

☆주의할 점 : 서버의 host 값이 연결하려는 외부 IP값인지 확인
		  꼭 클라이언트가 4개일 필요는 없다(여러개 가능)

3. 프로그램 실행환경 및 실행방법 설명
(실행방법 - 2번 참고)
외부 서버 - 구글 클라우드 (파이썬 3.11.2버전, 0.25-2 vCPU (1 shared core)
		메모리 1GB, Boot disk size 20GB, interface type: SCSI
로컬 실행 환경 - 프로세서 12th Gen Intel(R) Core(TM) i5-12500H 2.50 GHz
		      RAM 16GB, 64bit 운영체제, x64기반 프로세서


4. 구현한 최적의 알고리즘 제시 및 설명
▶ 비동기 메시지 처리
- 메시지를 처리하는 스레드와 큐를 사용하여, 메시지의 수신과 전송을 분리
- send_queue를 사용해 수신된 메시지를 큐에 저장 후, 별도의 스레드가 이를 처리

장점) 각 클라이언트의 메시지를 처리하는 스레드와 메시지 전송 스레드가 독립적으로 작동 및 메시지 전송 지연이나 병목현상이 발생하지 않음.
메시지 수신과 전송 작업의 충돌을 방지.

동작 원리) 클라이언트에서 메시지를 전송하면, 이를 receive_messages 스레드가 처리하여 send_queue에 저장.
send_messages 스레드가 큐에서 메시지를 가져와 적절한 방식으로 클라이언트들에게 전송.

▶ 명령어 기반 처리
- 클라이언트가 명령어를 사용하면, 이를 문자열로 파싱하여 각 명령에 대한 처리 로직 수행.
- /whisper, /kick, /schedule, /user, /rename 등의 명령을 처리.

장점) 명령어 처리 로직이 분리되어 가독성과 유지보수성 향상.
새로운 명령어를 쉽게 추가

동작 원리) 클라이언트가 명령어를 입력하면 receive_messages가 이를 파싱.
특정 명령어에 대한 로직(if-elif 구조)으로 전달.

▶ 예약 메시지 처리
- schedule_queue를 사용해 예약 메시지를 저장.
- 별도의 handle_scheduled_messages 스레드가 현재 시각을 지속적으로 확인.
- 예약된 시간과 현재 시간이 일치하면 예약 메시지를 send_queue로 이동하여
전송

장점) 예약된 메시지가 지정된 시간에 정확히 전송.
schedule_queue와 send_queue를 분리하여 예약 메시지와 일반 메시지의 충돌을 방지.

동작 원리) /schedule <HH:MM> <메시지> 명령으로 예약 메시지를 등록.
예약 시간이 되면 handle_scheduled_messages가 메시지를 전송.

▶ 사용자 관리
- nicknames 딕셔너리를 사용하여 클라이언트 소켓과 닉네임 매핑.
- 'group'이라는 리스트로 현재 연결된 클라이언트를 관리.

장점) 닉네임 중복을 방지하고, 소켓을 기준으로 클라이언트를 식별.
그룹 관리로 브로드캐스트와 강퇴 기능 구현이 간단.

동작 원리) 클라이언트 연결 시 닉네임 중복 여부를 확인하고 등록.
연결 종료 또는 강퇴 시 nicknames와 group에서 제거.


5. Error or Additional Message Handling 
▶ Additional Message Handling
⊙ Server
① /kick <닉네임> (클라이언트 1만 가능 - 방장)
▷동작: /kick <닉네임> 명령을 클라이언트 1번이 실행하면, 타겟 닉네임(target_nickname)에 해당하는 소켓(target_conn)을 찾음.
강퇴 대상이 확인되면, 강퇴 메시지 전송("You have been kicked from the chat.")
강퇴 대상 소켓 닫기 및 그룹(group)과 닉네임(nicknames)에서 제거 후 모든 사용자에게 강퇴 알림 전송
- 강퇴 대상이 없으면 발신자에게 알림: "User '<닉네임>' not found.".
- 클라이언트1이 자기 자신을 강퇴하려 하면 알림: "You cannot kick yourself.".

② /schedule <HH:MM> <메시지> (예약 메시지 처리)
▷동작: /schedule <HH:MM> <메시지> 명령을 클라이언트가 실행.
예약 시간과 메시지를 schedule_queue에 저장.
handle_scheduled_messages 스레드가 주기적으로 현재 시각을 확인.
현재 시각과 예약된 시각이 일치하면 send_queue에 메시지를 추가.
예약 메시지가 적시에 모든 사용자에게 전송
- 형태 : ([HH:MM] [Scheduled by 닉네임] 메시지)

③ /whisper <닉네임> <메시지> (귓속말/개인 메시지)
▷동작: /whisper <닉네임> <메시지> 명령을 발신자가 실행.
타겟 닉네임(target_nickname)에 해당하는 소켓(target_conn)을 찾음.
타겟 소켓이 확인되면 타겟 사용자에게 비공개 메시지 전송
- 타겟 사용자에게 뜨는 창 : [HH:MM] [Whisper from 발신자] 메시지
- 발신자에게 뜨는 창 : [HH:MM] [Whisper to 닉네임] 메시지
- 타겟 닉네임이 없는 경우 발신자에게 "User '<닉네임>' not found." 알림

④ /user (채팅방 참여자 목록 조회)
▷동작: /user 명령을 발신자가 실행.
현재 연결된 모든 사용자의 닉네임을 nicknames에서 추출
사용자 목록을 해당 명령어를 사용한 클라이언트(발신자)에게 전송
- 형태: Users in chat: 닉네임1, 닉네임2, ...

⑤ /rename (닉네임 변경 - 채팅방에 처음 들어와서 설정한 닉네임 수정)
▷동작: /rename <새 닉네임> 명령을 발신자가 실행
중복 안되면, 닉네임 변경 후 발신자에게 성공 메시지 전송 후 다른 모든 사용자들에게 닉네임 변경 사실을 알림
- 형태 : User "기존 닉네임" has changed their nickname to "새 닉네임".
- 닉네임 중복 시: User "기존 닉네임" has changed their nickname to "새 닉네임".

▶ Error Handling (Exception 처리 포함)

⊙ Server
① 메시지 전송 관련 에러 핸들링 (send_messages)
닫힌 소켓으로 데이터를 전송하려고 하면 발생하는 에러 핸들링
- 예외를 무시하고 다음 작업 진행
- 에러가 발생한 클라이언트에 대해서는 추가 작업 중단

② 클라이언트 연결 종료 처리 (receive_messages)
소켓이 이미 닫혔거나, nicknames 또는 group 리스트에 존재하지 않는 경우
딕셔너리에 존재하지 않는 키 삭제 시 발생하는 예외 처리
- if conn in nicknames 조건으로 소켓 존재 여부 확인 후 삭제
- group 리스트에서도 삭제 전 존재 여부 확인
- 이미 삭제된 경우 별도 처리 없이 로그 출력

③ 명령어 처리 에러 핸들링 (receive_messages)
- 잘못된 명령어 형식(/schedule 명령에서 시간 형식 오류)
- /kick, /whisper, /rename 명령에서 파싱 실패 시 에러 핸들링
- 명령어 파싱에 실패 시 발신자에게 오류 메시지 전송
- 중복 닉네임이나 닉네임이 없는 경우 적절한 오류 메시지 반환

④ 강퇴 처리 관련 에러 핸들링 (send_messages의 KICK 부분)
강퇴 대상 닉네임이 없을 때와 강퇴 대상의 소켓이 이미 닫힌 경우 예외 발생
- 닉네임 존재 여부 확인 후 닉네임이 없을 시 발신자에게 알림
- 소켓 닫힘으로 인한 에러 발생 시 작업 중단 및 로그 출력

⑤ 예약 메시지 처리 에러 핸들링 (handle_scheduled_messages)
큐 접근 중 논리적 에러 발생 시 예외 처리
- schedule_queue를 순회하며 발생하는 예외를 잡아 로그 출력
- 메시지 제거 시 큐의 상태를 안전하게 확인

⑥ 소켓 수신 에러 핸들링 (receive_messages)
클라이언트가 연결을 끊었을 때, 데이터 수신 실패했을 때 예외 처리
- 연결 종료 시 스레드 종료 및 자원 해제
- 데이터 수신 실패 시 break로 루프 종료

⊙ Client
① 메시지 수신 중 에러 처리 (receive_messages)
서버가 클라이언트 연결을 끊거나 네트워크 문제가 발생할 때 발생하는 예외 처리
데이터 수신 실패 (빈 데이터나 네트워크 중단) 발생 시 예외 처리
- Disconnected from server 메시지 출력 후 소켓을 닫고 수신 루프 종료


6. Additional Comments (팀플 날짜 기록)
2024/11/30
과제 시작
주제 구상 : 단체 채팅방 선정

12/02
thread 기반의 서버1개와 클라이언트4개이상 포함하는 프로그램 생성
단체 채팅방 형태 완성
카카오톡 오픈채팅방 형식으로 별명 설정 후 채팅방 참여
클라이언트1은 방장 권한 획득, 다른 클라이언트 강퇴가능
- 자기 자신 강퇴 문제 (해결)
- 별명이 같을 때 강퇴 문제 (해결)
별명 중복 허용X
broadcast로 채팅방에 있는 모든 클라이언트에게 새로운 클라이언트 참여 알림, 채팅방 나감 알림, 강퇴 알림

12/03
- 구현한 기능
단체 채팅방(오픈 채팅방)
1. 클라이언트 별명 설정 √
1.1 클라이언트 별명 변경 (메시지 형식: /rename) √
2. 클라이언트1은 방장으로서 다른 클라이언트를 강퇴 (메시지 형식: /kick) √
3. 예약 메시지 (메시지 형식: /schedule HH:MM <메시지> ) √
4. 개인 메시지 (귓속말) (메시지 형식: /whisper <닉네임> <메시지>) √
5. 사용자 목록 조회 (메시지 형식: /user) √ 
6. 메시지 앞 현재 시간 표시 √ (import datetime, 시:분 까지 출력) √

닉네임을 변경하고 강퇴당했을 때 오류 수정
강퇴당했을 때 예외처리