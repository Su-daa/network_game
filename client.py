# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.messagebox
import tkinter.simpledialog
import socket
import threading
from threading import Thread
from time import sleep
from tkinter import *
from tkinter import PhotoImage


#새로운 프레임 띄우기
def openFrame(frame):
    frame.tkraise()

def name_select():
    result = tkinter.simpledialog.askstring("제목", "닉네임을 입력하세요")
    global your_name
    your_name = str(result)
    my_name.set(your_name)
    if your_name.encode('utf-8').isalnum() == False:
        tk.messagebox.showerror(
            title="ERROR!", message="영어로 닉네임을 입력하세요."
        )
        name_select()
    else:
        lbl_your_name["text"] = "당신의 닉네임: " + your_name
        connect_to_server(your_name)


#이미지선택
a = None
def character_select1(e):
    global a
    a = image1

def character_select2(e):
    global a
    a = image2

def character_select3(e):
    global a
    a = image3

def character_select4(e):
    global a
    a = image4

def select_ok(e):
    select_char_can.configure(image = a)

def char_select():
    img_a = str(a)
    print("img_a:", img_a)
    char_image = f'$image_char: {your_name}: {img_a}'
    print(char_image)
    client.send(char_image.encode('utf-8'))


def chat_send(event=None):
    message = f'message: {your_name}: {chat_input.get()}'
    client.send(message.encode('utf-8'))
    chat_input.delete(0, 'end')

def game_logic(you, opponent):
    winner = ""
    rock = "rock"
    paper = "paper"
    scissors = "scissors"
    player0 = "you"
    player1 = "opponent"

    if you == opponent:
        winner = "draw"
    elif you == rock:
        if opponent == paper:
            winner = player1
        else:
            winner = player0
    elif you == scissors:
        if opponent == rock:
            winner = player1
        else:
            winner = player0
    elif you == paper:
        if opponent == scissors:
            winner = player1
        else:
            winner = player0
    return winner


def enable_disable_buttons(todo):
    if todo == "disable":
        btn_rock.config(state=tk.DISABLED)
        btn_paper.config(state=tk.DISABLED)
        btn_scissors.config(state=tk.DISABLED)
        gamest_bt.config(state=tk.DISABLED)
    else:
        btn_rock.config(state=tk.NORMAL)
        btn_paper.config(state=tk.NORMAL)
        btn_scissors.config(state=tk.NORMAL)
        gamest_bt.config(state=tk.NORMAL)

def count_down(my_timer, nothing):
    global game_round
    if game_round <= TOTAL_NO_OF_ROUNDS:
        game_round = game_round + 1

    lbl_game_round["text"] = "Game " + str(game_round) + " round 가 시작되었습니다."
    game_lb = tk.Label(top_left_frame, image = game)
    lbl_game_round["text"] = "Game " + str(game_round) + " round 가 시작되었습니다."

    while my_timer > 0:
        my_timer = my_timer - 1
        print("게임 타이머: " + str(my_timer))
        lbl_timer["text"] = my_timer
        sleep(1)

    enable_disable_buttons("enable")
    lbl_round["text"] = "Round - " + str(game_round)
    lbl_final_result["text"] = " "

def choice(arg):
    global your_choice, client, game_round
    your_choice = arg
    lbl_your_choice["text"] = "당신의 선택: " + your_choice

    if client:
        dataToSend = "Game_Round" + str(game_round) + your_choice
        client.send(dataToSend.encode('utf-8'))
        enable_disable_buttons("disable")


def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR, your_name
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode('utf-8'))  # 연결 후 서버에게 메세지 보냄

        # 서버로부터 메세지를 계속 수신하기 위해 스레드 시작
        openFrame(frame2)  ##추가함
        threading._start_new_thread(receive_message_from_server, (client, "m"))
        # threading._start_new_thread(chat_receive, (client,))
        # threading._start_new_thread(chat_send, (client,))


    except Exception as e:
        tk.messagebox.showerror(
            title="ERROR!!!",
            message="host와 연결 할 수 없습니다. "
            + HOST_ADDR
            + " on port: "
            + str(HOST_PORT)
            + " 연결 할 수 없습니다. 다시 시도해주세요. "
        )

def game_start():
    client.send("$entered_game".encode('utf-8'))
    openFrame(frame4)

def receive_message_from_server(sck, m): #매칭
    global your_name, opponent_name, game_round
    global your_choice, opponent_choice, your_score, opponent_score,final_result,color
    final_result = ""
    color = ""

    while True:
        from_server = str(sck.recv(4096).decode())

        if not from_server:
            break

        if from_server.startswith("welcome"):

            if from_server == "welcome1":
                lbl_welcome["text"] = (
                    " 환영합니다! " + your_name + " 님 상대방을 기다려주세요."
                )
            elif from_server == "welcome2":

                lbl_welcome["text"] = (
                    " 환영합니다! " + your_name + " 님 상대방을 기다려주세요."
                )
            lbl_line_server.pack()


        elif from_server.startswith("opponent_name$"):

            opponent_name = from_server.replace("opponent_name$", "")
            select_anchar_user = tk.Label(frame3, text=opponent_name,bg="white",bd=0)
            select_anchar_user.place(x=300, y=13)
            lbl_opponent_name["text"] = "상대방 닉네임: " + opponent_name
            opp_name = str(opponent_name)
            top_frame.pack()
            middle_frame.pack()
            lbl_welcome.config(state=tk.DISABLED)
            lbl_line_server.config(state=tk.DISABLED)
            openFrame(frame3)

        #########################수정
        elif from_server.startswith("message"):
            try:
                msg = from_server[9:len(from_server)] + """\n"""
                chat_space.insert(tkinter.END, msg)  ##이건 채팅창에 출력되어야 함 END, '\n',
                print("chat_receive worked. message received and inserted")
            except:
                print("error. chat_receive not working. no message received")

        elif from_server.startswith("$opp_img_choice:"):
            opp_img_choice = from_server[-8:len(from_server)]
            print("opp_img_choice:", opp_img_choice)
            # select_char_opp.configure(image=opp_img_choice[2:])
            opp_img = tk.PhotoImage(file="image/" + opp_img_choice[2:] + ".gif")  # 경로를 따로 지정하지 않으면 파일이 있는 위치를 가리킴.
            # label = tk.Label(image=opp_img)
            select_char_opp = tk.Label(frame3, width=150, height=150, image=opp_img)  ##상대방 캐릭터 선택 결과 출력 위치
            select_char_opp.place(x=220, y=50)

        elif from_server.startswith("$start_game"):
            print("client received the message start_game. start count_down")
            threading._start_new_thread(count_down, (game_timer, ""))


        #elif from_server.startswith("start"):
           # gamestart()

        elif from_server.startswith("$opponent_choice"):
            # 서버에서 상대방 선택-> 가위 바위 보 선택
            opponent_choice = from_server.replace("$opponent_choice", "")

            # 누가 이겼는지 결과
            who_wins = game_logic(your_choice, opponent_choice)
            round_result = " "
            if who_wins == "you":
                your_score = your_score + 1
                round_result = "WIN"
                # final_result = "(당신이 선공입니다!!!)"
                # color = "green"
            elif who_wins == "opponent":
                opponent_score = opponent_score + 1
                round_result = "LOSE"
                # final_result = "(당신이 방어입니다!!!)"
                # color = "red

            else:
                round_result = "DRAW"
                # final_result = "(무승부!!!)"
                # color = "black"
                # lbl_opponent_choice["text"] = "상대방의 선택: " + opponent_choice
                # lbl_result["text"] = "결과: " + round_result
                # lbl_game_round["text"] = "다시 선택해주세요."
                # enable_disable_buttons('')
                # continue

            # GUI 업데이트
            lbl_opponent_choice["text"] = "상대방의 선택: " + opponent_choice
            lbl_result["text"] = "이번 라운드 결과: " + round_result

            # 마지막 라운드 결과
            if game_round == TOTAL_NO_OF_ROUNDS:
                # compute final result
                final_result = ""
                color = ""

                if your_score > opponent_score:
                    color = "darkgreen"
                    result_img=win_img
                elif your_score < opponent_score:
                    color = "darkgreen"
                    result_img=lose_img
                else:
                    color = "darkgreen"
                    result_img=draw_img
                    # sleep(2)
                    # game_logic(your_choice, opponent_choice)

                lbl_final_result["text"] = (
                    "잠시후 결과창으로 이동합니다!!!"
                )
                lbl_final_result.config(foreground=color)
                enable_disable_buttons("disable")

                sleep(3)
                openFrame(frame5)

                #결과 페이지 보이게 하기
                result = tk.Label(frame5,image=result_img)
                result.place(x=-2, y=-2)

                game_round = 0
                your_score = 0
                opponent_score = 0

            threading._start_new_thread(count_down, (game_timer, ""))
    sck.close()
"""
def gameready():
    ready_message="start"
    client.send(ready_message.encode('utf-8'))
    enable_disable_buttons("disable")
def gamestart():
    sleep(1)
    openFrame(frame4)
    top_frame.pack()
    middle_frame.pack()
    threading._start_new_thread(count_down, (game_timer, ""))
"""

'**************************게임창 띄우기******************************'
window=tkinter.Tk()
window.title("가위바위보 게임")
window.geometry("700x700")

global my_name, opp_name
my_name = StringVar()
opp_name = StringVar()

#프레임 정의
frame1=tkinter.Frame(window,bg='white') #기본 프레임
frame2=tkinter.Frame(window,bg='white') #닉네임 정하고 매칭 시작후 방 들어가는 화면
frame3=tkinter.Frame(window,bg='white') #대기방
frame4=tkinter.Frame(window,bg='white') #가위바위보 창
frame5=tkinter.Frame(window,bg='white') #참참참 게임
frame1.grid(row=0, column=0, sticky="nsew")
frame2.grid(row=0, column=0, sticky="nsew")
frame3.grid(row=0, column=0, sticky="nsew")
frame4.grid(row=0, column=0, sticky="nsew")
frame5.grid(row=0, column=0, sticky="nsew")


#이미지
image1=PhotoImage(file="image/image1.gif")
image2=PhotoImage(file="image/image2.gif")
image3=PhotoImage(file="image/image3.gif")
image4=PhotoImage(file="image/image4.gif")
playbt=PhotoImage(file="image/start.gif")
photo_rock = PhotoImage(file="image/rock.gif")
photo_paper = PhotoImage(file="image/paper.gif")
photo_scissors = PhotoImage(file="image/scissors.gif")
win_img=PhotoImage(file="image/win.gif")
lose_img=PhotoImage(file="image/lose.gif")
draw_img=PhotoImage(file="image/draw.gif")
startbg=PhotoImage(file="image/startbg.gif")
treebg=PhotoImage(file="image/tree.gif")
waitbg=PhotoImage(file="image/waiting.gif")
select_ch=PhotoImage(file="image/select_ch.gif")

me=PhotoImage(file="image/me.gif")
you=PhotoImage(file="image/you.gif")
game=PhotoImage(file = "image/game.gif")
round_start = PhotoImage(file = "image/round_start.gif")
animals_img = PhotoImage(file = "image/animals.gif")
gamelog_img=PhotoImage(file="image/gamelog.gif")
line_img=PhotoImage(file="image/line.gif")
smallline_img=PhotoImage(file="image/smallline.gif")


#frame1(게임 첫 화면)
start_bg = tk.Label(frame1,image=startbg,bd=0)
start_bg.place(x=0, y=0)
game_st=tk.Button(frame1,image=playbt,bd=0,command = name_select)
game_st.pack(padx=250,pady=400)
tree_bg=tk.Label(frame1,image=treebg,bd=0)
tree_bg.place(x=0,y=550)

#frame2(매칭방)
input_nickname_bt=tk.Label(frame2,image=waitbg)
input_nickname_bt.place(x = 0, y= 0)

#frame3(대기방)
#선택 이미지 표시
select_char_can = tk.Label(frame3, width =150, height = 150,bg="white",bd=0)
select_char_can.place(x=50, y=50)
select_ch_lb=tk.Label(frame3,image=me,bd=0)
select_ch_lb.place(x=20,y=10)
select_char_user=tk.Label(frame3, textvariable= my_name,bg="white",bd=0)
select_char_user.place(x=60,y=13)
select_ch_you_lb=tk.Label(frame3,image=you,bd=0)
select_ch_you_lb.place(x=250,y=13)

#캐릭터 선택 버튼
char_select_br = tk.Button(frame3,image=select_ch,bd=1,command = char_select)
char_select_br.place(x =200,y=650)
#캐릭터 버튼 배치
char_image1 = tk.Button(frame3,image=image1, width = 200, height = 200)
char_image2 = tk.Button(frame3,image=image2, width = 200, height = 200)
char_image3 = tk.Button(frame3,image=image3, width = 200, height = 200)
char_image4 = tk.Button(frame3,image=image4, width = 200, height = 200)
char_image1.place(x=25,y=240)
char_image2.place(x=235,y=440)
char_image3.place(x=25,y=440)
char_image4.place(x=235,y=240)
char_image1.bind('<Button>', character_select1)
char_image2.bind('<Button>', character_select2)
char_image3.bind('<Button>', character_select3)
char_image4.bind('<Button>', character_select4)
char_select_br.bind('<Button>', select_ok)


#채팅 보여질 공간 (Label에서 Text로 변경)
chat_space = tk.Text(frame3, width = 30, height =35)
chat_space.place(x= 460, y=30)

#채팅입력 하는곳
chat_input = tk.Entry(frame3)
# chat_input.bind("<Return>",chat_send)
chat_input.place(x = 460, y = 500,width=155,height=22)
chat_input.bind("<Return>",chat_send )

#전송 버튼
chat_br = tk.Button(frame3, text=" 전송 ", command = chat_send)
chat_br.place(x =630,y=495)

#가위바위보 게임시작 버튼
gamest_bt= tk.Button(frame3,image=playbt,command=game_start,bd=0)
gamest_bt.place(x=480,y=550)

your_name = ""
opponent_name = ""
game_round = 0
game_timer = 4
your_choice = ""
opponent_choice = ""
TOTAL_NO_OF_ROUNDS = 5
your_score = 0
opponent_score = 0

# 네트워크 클라이언트
client = None
HOST_ADDR = "192.168.231.1"
# HOST_ADDR = "localhost"
HOST_PORT = 8080


animals_lb = tk.Label(frame4, image = animals_img, bd = 0)
animals_lb.place(x=0,y=537)


tree_bg=tk.Label(frame1,image=treebg,bd=0)
tree_bg.place(x=0,y=550)
top_message_frame = tk.Frame(frame4,bg='white')

lbl_line = tk.Label(
    top_message_frame,
    image=line_img,
    bg='white'
).pack()
lbl_welcome = tk.Label(top_message_frame, text="",bg='white')
lbl_welcome.pack()
#welcome_lb = tk.Label(frame4, image = welcome_img,bg='white')
#welcome_lb.place(x = 220, y= 15)
lbl_line_server = tk.Label(
    top_message_frame,
    image=line_img,bg='white'
)
lbl_line_server.pack_forget()
top_message_frame.pack(side=tk.TOP)


top_frame = tk.Frame(frame4, bg = "white")
top_left_frame = tk.Frame(
    top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=2,bg= "white"
)
lbl_your_name = tk.Label(
    top_left_frame, text="당신의 닉네임 " + your_name, font="Helvetica 11 bold", bg="white"
)

lbl_opponent_name = tk.Label(top_left_frame, text="상대방 닉네임 " + opponent_name, bg='white')
lbl_your_name.grid(row=0, column=0, padx=5, pady=8)
lbl_opponent_name.grid(row=1, column=0, padx=5, pady=8)
top_left_frame.pack(side=tk.LEFT, padx=(10, 10))


top_right_frame = tk.Frame(
    top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=2, bg = 'white'
)
lbl_game_round = tk.Label(
    top_right_frame,
    text="Game round (x)",
    foreground="black",
    font="Helvetica 14 bold", bg = 'white'
)
lbl_timer = tk.Label(
    top_right_frame, text=" ", font="Helvetica 24 bold", foreground="black", bg = 'white'
)
lbl_game_round.grid(row=0, column=0, padx=5, pady=5)
lbl_timer.grid(row=1, column=0, padx=5, pady=5)
top_right_frame.pack(side=tk.RIGHT, padx=(10, 10))

top_frame.pack_forget()

middle_frame = tk.Frame(frame4,bg='white')

lbl_line = tk.Label(
    middle_frame,text="-------------------------------------------------------",bg='white',foreground="green"
).pack()
lbl_line = tk.Label(
    middle_frame, text="**** GAME LOG ****", font="Helvetica 13 bold", foreground="black", bg= 'white'
).pack()


lbl_line = tk.Label(
    middle_frame,text="-------------------------------------------------------",bg='white',foreground="green"
).pack()

round_frame = tk.Frame(middle_frame,bg='white')
lbl_round = tk.Label(round_frame, text="Round",bg='white')
lbl_round.pack()
lbl_your_choice = tk.Label(
    round_frame, text="당신의 선택: " + "None", font="Helvetica 13 bold",bg='white'
)
lbl_your_choice.pack()
lbl_opponent_choice = tk.Label(round_frame, text="상대방 선택: " + "None",bg='white')
lbl_opponent_choice.pack()
lbl_result = tk.Label(
    round_frame, text=" ", foreground="green", font="Helvetica 13 bold",bg='white'
)
lbl_result.pack()
round_frame.pack(side=tk.TOP)

final_frame = tk.Frame(middle_frame,bg='white')
lbl_line = tk.Label(
    final_frame,text="-------------------------------------------------------",bg='white',foreground="green"
).pack()
lbl_final_result = tk.Label(
    final_frame, text=" ", font="Helvetica 13 bold", foreground="darkgreen",bg='white'
)
lbl_final_result.pack()
lbl_line = tk.Label(
    final_frame,text="-------------------------------------------------------",bg='white',foreground="green"
).pack()
final_frame.pack(side=tk.TOP)

middle_frame.pack_forget()

button_frame = tk.Frame(frame4, bg= 'white')
button_frame.pack(side=tk.BOTTOM)

btn_rock = tk.Button(
    frame4,
    text="주먹",
    command=lambda: choice("rock"),
    state=tk.DISABLED,
    image=photo_rock,
)
btn_paper = tk.Button(
    frame4,
    text="보",
    command=lambda: choice("paper"),
    state=tk.DISABLED,
    image=photo_paper,
)
btn_scissors = tk.Button(
    frame4,
    text="가위",
    command=lambda: choice("scissors"),
    state=tk.DISABLED,
    image=photo_scissors,
)

btn_rock.place(x=200, y=450)
btn_paper.place(x=300, y=450)
btn_scissors.place(x=400, y=450)


openFrame(frame1)
window.mainloop()
