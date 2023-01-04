# -*- coding: utf-8 -*-
import tkinter as tk
import socket
import threading
from time import sleep


window = tk.Tk()
window.title("Sever")

# 두 개의 버튼 위젯으로 구성된 상단 프레임 (예: btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# 호스트 및 포트 정보를 표시하기 위한 두 개의 레이블로 구성된 중간 프레임
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Address: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# 클라이언트 영역
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = "192.168.231.1"
HOST_PORT = 8080
client_name = " "
clients = []
clients_names = []
player_data = []
player = 0

# 서버 기능 시작
def start_server():
    global server, HOST_ADDR, HOST_PORT
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(2) ##2명만 접속 가능한 거 확인 완료


    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Address: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# 서버 기능 중지
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)


def accept_clients(the_server, y):
    while True:
        if len(clients) < 2:
            client, addr = the_server.accept()
            clients.append(client)
            print('clients: ', clients)
            print('client: ', client)

            # GUI 스레드 막히지 않도록 스레드 사용
            threading._start_new_thread(send_receive_client_message, (client, addr))


# 현재 클라이언트로부터 메시지를 받는 함수 AND
# 해당 메시지를 다른 클라이언트에게 보냄
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, player_data, player0, player1, player_img_data, player

    client_msg = " "
    # 클라이언트에게 환영 메세지 보내기
    client_name = client_connection.recv(4096)
    if len(clients) < 2:
        client_connection.send("welcome1".encode('utf-8'))
    else:
        client_connection.send("welcome2".encode('utf-8'))

    clients_names.append(client_name)
    update_client_names_display(clients_names)  # 업데이트 된 클라이언트 이름 나타남

    if len(clients) > 1:
        print("matched 2")
        sleep(1)

        # 상대방 이름 보내기
        clients[0].send("opponent_name$".encode('utf-8') + clients_names[1])
        clients[1].send("opponent_name$".encode('utf-8') + clients_names[0])


    while True:
        data = client_connection.recv(4096).decode()
        print("data: ", data)
        if not data: break
        #$image_char: one: pyimage2
        if data.startswith("$image_char"):
            img_choice = data[-8:len(data)]
            print("img_choice:", img_choice)
            print("clients_names[0]:", str(clients_names[0]))
            print("clients_names[1]:", str(clients_names[1]))

            cli_name = f'b\'{data[13:-10]}\''
            print("cli_name:", cli_name)
            #clients_name 리스트 안에 각 클라이언트의 이름이 저장되어 있음

            if str(clients_names[0]) == cli_name:
              clients[1].send(f'$opp_img_choice: {img_choice}'.encode('utf-8'))
            elif str(clients_names[1]) == cli_name:
              clients[0].send(f'$opp_img_choice: {img_choice}'.encode('utf-8'))
            else:
              print("error. have no corresponding nickname")

        elif data.startswith("message"):
            print('message received: ', data)
            # client_connection.sendall(data.encode('utf-8'))
            for client in clients:
                client.send(data.encode('utf-8'))
                print('server sended a message to ', client)

        elif data.startswith("$entered_game"):
            player += 1
            print("player added", player)
            if player == 2:
                print("player 2 done. let the game begin.")
                for client in clients:
                    client.send("$start_game".encode('utf-8'))
                print("send successfully done")
        else:
            print("server.py에서 else로 들어옴")
            # 수신된 데이터에서 플레이어 선택
            player_choice = data[11:len(data)]

            msg = {
                "choice": player_choice,
                "socket": client_connection
            }

            if len(player_data) < 2:
                player_data.append(msg)

            if len(player_data) == 2:
                print("$opponent_choice 보낸다~~ 타이머 시작한다 ")
                # 플레이어 선택을 다른 플레이어에게 보냄
                player_data[0].get("socket").send("$opponent_choice".encode('utf-8') + player_data[1].get("choice").encode('utf-8'))
                player_data[1].get("socket").send("$opponent_choice".encode('utf-8') + player_data[0].get("choice").encode('utf-8'))

                player_data = []


    # 클라이언트 인덱스를 찾고 이름, 연결 목록에서 제거
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    client_connection.close()

    update_client_names_display(clients_names)  # 클라이언트 이름 표시 업데이트

# 클라이언트 목록에서 현재 클라이언트의 인덱스 반환
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# 새 클라이언트가 연결할 때 클라이언트 이름 표시 또는 업데이트
# 연결된 클라이언트의 연결이 끊겼을 때
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+b"\n")
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()
