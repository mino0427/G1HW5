1조 조원 구성 및 역할

20203043 권수현 - 알고리즘 설계, 구현, 아이디어 제공 및 기능 구현

20203058 남태인 - 알고리즘 설계, 구현, 아이디어 제공 및 기능 구현

20203072 안민호 – 알고리즘 설계, 구현, 아이디어 제공 및 기능 구현

1. 프로그램 구성요소 : server.py, client.py

◆ server.py 구성요소
① 

② 

③ 

④ 

⑤ 

◆ client.py 구성요소
① 
②
③ 
④


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

3. 프로그램 실행환경 및 실행방법 설명
(실행방법 - 2번 참고)
외부 서버 - 구글 클라우드 (파이썬 3.11.2버전, 0.25-2 vCPU (1 shared core)
		메모리 1GB, Boot disk size 20GB, interface type: SCSI
로컬 실행 환경 - 프로세서 12th Gen Intel(R) Core(TM) i5-12500H 2.50 GHz
		      RAM 16GB, 64bit 운영체제, x64기반 프로세서


4. 구현한 최적의 알고리즘 제시 및 설명


⦁ 알고리즘 시나리오


5. Error or Additional Message Handling
▶ Additional Message Handling
⊙ Server
①
② 

③ 

⊙ Client
①
② 
③ 



▶ Error Handling (Exception 처리 포함)

⊙ Server
① 

② 

③

⊙ Client
① 
② 

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


- 기능
단체 채팅방(오픈 채팅방)
1. 클라이언트 별명 설정 √
1.1 클라이언트 별명 변경 (메시지 형식: /rename) √
2. 클라이언트1은 방장으로서 다른 클라이언트를 강퇴 (메시지 형식: /kick) √
3. 파일 전송 기능 ( 메시지를 전송하는지 파일을 전송하는지 확인)
4. 예약 메시지
5. 개인 메시지 (귓속말) (메시지 형식: /whisper <닉네임> <메시지>) √
6. 사용자 목록 조회 (메시지 형식: /user) √ 
7. 메시지 앞 현재 시간 표시 √ (import datetime, 시:분 까지 출력) √

닉네임을 변경하고 강퇴당했을 때 오류 수정