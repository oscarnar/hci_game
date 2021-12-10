import copy
from os import system
from tkinter import *
import sys
import game
import turtle
import os
import random
import autopy
import time

sWidth, sHeight = game.wScr, game.hScr #autopy.screen.size()

def setup():
    global ventana
    global t
    global s
    global game_canvas
    global HP

    game_canvas = Canvas(ventana, width = sWidth, height = sHeight)
    # game_canvas.create_text(sWidth/2, sHeight/2, text="HP: " + str(HP))
    # canvas.place(relx=0.5, rely=0.5,anchor=CENTER)
    game_canvas.pack(fill=BOTH, expand=YES)
    # canvas.place(x=200, y=200,anchor=CENTER)

    # canvas.grid(padx=2, pady=2, row=0, column=0, rowspan=10, columnspan=10)
    s = turtle.TurtleScreen(game_canvas)
    # t=turtle.Turtle()
    t = turtle.RawTurtle(s)
    # s.setup(1.0,1.0,None,None)
    t.hideturtle()
    t.up()
    t.speed(0)
    t.pensize(5)
    t.pencolor("red")
    # turtle.tracer(0, 0)
    s.tracer(0, 0)
    return s, t


def drawCSq(t, cx, cy, a):
    t.goto(cx-(a/2), cy-(a/2))
    t.down()
    t.goto(cx+(a/2), cy-(a/2))
    t.goto(cx+(a/2), cy+(a/2))
    t.goto(cx-(a/2), cy+(a/2))
    t.goto(cx-(a/2), cy-(a/2))
    t.up()

def drawHP():
    global HP
    t.clear()
    t.goto(0, HP)
    t.write("HP: " + str(HP), font=("Arial", 16, "normal"))

def timer():
    global tstep
    global sx
    global sy
    global lastSpawn
    global Delay
    global HP
    global Score
    global Combo
    global game_canvas

    # end = HP, -sHeight/2 +50
    # start = HP , 50
    # game_canvas.create_line(50,-sHeight/2 + 50, sWidth/2 -50 , width=10, fill="green")
    # game_canvas.create_line(* start, * end , width=10, fill="green")

    # game_canvas.config()
    # game_canvas.itemconfig(label, fill="green")

    # t.pencolor("green")
    t.write("HP: " + str(HP), font=("Arial", 22, "normal"))
    # t.pencolor("red")

    if tstep >= lastSpawn+Delay:
        sx.append(random.randrange(-320+A, 320-A))
        sy.append(random.randrange(-240+A, 240-A))
        st.append(tstep)
        sttl.append(TTL)
        lastSpawn = tstep
        Delay -= max(1, Delay//DelayDecFact)
        Delay = max(MinDelay, Delay)
        # game_canvas.delete(line)

    j = 0
    while j < len(sx):
        if(st[j]+sttl[j] < tstep):
            del st[j]
            del sttl[j]
            del sx[j]
            del sy[j]
            HP -= HpDec
            HP = max(0, HP)
            Combo = 0
            print("HP:", HP, "Score:", Score, "Combo:", Combo, "Last Hit:", 0)
        else:
            j += 1

    t.clear()
    
    for i in range(len(sx)):
        drawCSq(t, sx[i], sy[i], A)
        # drawHP()
        A2 = A*((sttl[i]+st[i]-tstep-(sttl[i]*JudgmentLine))/sttl[i])
        if(A2 > 0):
            drawCSq(t, sx[i], sy[i], A+A2)
    game.detect_gesture(game.mode)

    path_bg = game.images_path + str(game.tmp_path) + '.png'

    s.bgpic(path_bg)
    s.update()
    rm_command = "rm " + game.images_path + str(game.tmp_path) + '.png'
    os.system(rm_command)
    game.tmp_path = (game.tmp_path + 1)
    tstep += 1
    if HP > 0:
        s.ontimer(timer, 10)
    else:
        # s.bye()
        gameover_screen()
        

def game_over():
    global isPlaying
    global ventana
    global canvas_root
    global img

    game_canvas.destroy()
    gameover_img = PhotoImage(file="assets/game_over.png")
    canvas_root = Canvas(ventana, height=500, width=500, bg="salmon")
    canvas_root.create_image(tmp_pos_x,tmp_pos_y, image=gameover_img)
    canvas_root.pack(fill=BOTH, expand=YES)
    # img = canvas_root.create_image(tmp_pos_x, tmp_pos_y, image=gameover_img)
    # isPlaying = False
    # ventana.after(1,hand_move)

def print_score():
    global HP
    global label_score
    label_score.config(text=HP)

def click(x, y):
    global TTL
    global HP
    global Score
    global Combo

    if len(sx) > 0 and sx[0]-(A/2) < x and sx[0]+(A/2) > x and sy[0]-(A/2) < y and sy[0]+(A/2) > y:
        TTL -= TTLDec
        TTL = max(MinTTL, TTL)
        HP += HpInc
        HP = min(100, HP)
        Combo += 1
        HitDiff = abs((st[0]+(sttl[0]*(1-JudgmentLine)))-tstep)
        HitDiffPre = 1-(HitDiff/(sttl[0]*(1-JudgmentLine)))
        LastHit = 50+int(250*HitDiffPre)
        Score += Combo*LastHit
        print("HP:", HP, "Score:", Score, "Combo:", Combo, "Last Hit:", LastHit)
        del sx[0]
        del sy[0]
        del st[0]
        del sttl[0]

    t.clear()

    for i in range(len(sx)):
        drawCSq(t, sx[i], sy[i], A)
        A2 = A*((sttl[i]+st[i]-tstep-(sttl[i]*JudgmentLine))/sttl[i])
        if(A2 > 0):
            drawCSq(t, sx[i], sy[i], A+A2)
    print_score()
    s.update()


def hand_move():
    global tmp_pos_x
    global tmp_pos_y
    global img
    global canvas_root
    global close_img
    global hand_img
    global isPlaying
    game.detect_gesture(game.mode)
    if(game.hand_state == 'Close'):
        canvas_root.itemconfig(img,image=close_img)
    if(game.hand_state == 'Open'):
        canvas_root.itemconfig(img,image=hand_img)
    tmp_x,tmp_y = autopy.mouse.location()
    canvas_root.move(img, tmp_x - tmp_pos_x, tmp_y - tmp_pos_y)
    tmp_pos_x ,tmp_pos_y = autopy.mouse.location()
    # hand_canvas.move(img, 0, 1)
    # hands_label.place(x=game.pos_x, y=game.pos_y)
    # img = canvas_root.create_image(game.pos_x, game.pos_y, image=hand_img)
    if(isPlaying == False):
        ventana.after(1,hand_move)

def hand_move_over():
    global tmp_pos_x
    global tmp_pos_y
    global img_over
    global canvas_gameover
    global close_img
    global hand_img
    global isPlaying
    game.detect_gesture(game.mode)
    if(game.hand_state == 'Close'):
        canvas_gameover.itemconfig(img_over,image=close_img)
    if(game.hand_state == 'Open'):
        canvas_gameover.itemconfig(img_over,image=hand_img)
    tmp_x,tmp_y = autopy.mouse.location()
    #BUG:
    canvas_gameover.move(img_over, tmp_x - tmp_pos_x, tmp_y - tmp_pos_y)
    tmp_pos_x ,tmp_pos_y = autopy.mouse.location()
    if(isPlaying == False):
        ventana.after(1,hand_move_over)

ventana = Tk()
ventana.attributes('-fullscreen', True)
# ventana.geometry('800x800')
ventana.config(bg='skyblue')
ventana.title('Just Draw')
ventana.resizable(width=False, height=False)
# ventana.iconbitmap('./imagenes/imagen.ico')
ventana.config(cursor="none")


# ventana.mainloop()
## Second instructions Screen: Game objetives
instructions_img = PhotoImage(file='assets/instructions.png')
def instructions_screen():
    global ventana
    global canvas_instructions
    global instructions_img
    global canvas_root
    canvas_root.destroy()
    canvas_instructions.create_image(game.wScr/2 ,game.hScr/2, image=instructions_img)
    canvas_instructions.pack(fill=BOTH, expand=YES)
    # time.sleep(5)
    ventana.after(5000, jugar)

# canvas_root = Canvas(ventana, height=game.hScr, width=game.wScr, bg="salmon")

def salir():
    sys.exit()

logo_img = PhotoImage(file='assets/just_draw_logo.png')
def menu():
    global canvas_root
    global canvas_init
    global logo_img
    canvas_init.destroy()

    canvas_root.create_image(game.wScr/2 ,game.hScr/2 - 250, image=logo_img)
    canvas_root.pack(fill=BOTH, expand=YES)

    fontButton = 'Helvetica 15 bold'
    boton_jugar = Button(canvas_root, text='JUGAR', command=instructions_screen, font=(fontButton))
    boton_jugar.config( height = 5, width = 30, fg = "black", activebackground="#6ab14b", activeforeground="white")
    boton_jugar.place(x=game.wScr/2 - 150, y=game.hScr/2 + 50)

    boton_salir = Button(canvas_root, text='SALIR', command=salir, font=(fontButton))
    boton_salir.config( height = 5, width = 30, fg = "black", activebackground="#6ab14b", activeforeground="white")

    # boton_salir.grid(row = 1, column = 3, pady = 10, padx = 100)
    boton_salir.place(x=game.wScr/2 - 150, y=game.hScr/2 + 180)
    # ventana.after(1,hand_move(canvas_root))

first_img = PhotoImage(file='assets/first.png')
## First Screen: instructions for controls
def first_screen():
    global ventana
    global canvas_init
    global first_img
    # first_img = PhotoImage(file='assets/first.png')
    canvas_init.create_image(game.wScr/2 ,game.hScr/2, image=first_img)
    canvas_init.pack(fill=BOTH, expand=YES)
    # time.sleep(5)
    ventana.after(5000, menu)

gameover_img = PhotoImage(file='assets/game_over.png')
gameover_img = gameover_img.subsample(2,2)
## First Screen: instructions for controls
def gameover_screen():
    global ventana
    global canvas_gameover
    global game_canvas
    global gameover_img
    global isPlaying
    isPlaying = False
    game_canvas.destroy()
    canvas_gameover.create_image(game.wScr/2 ,game.hScr/2, image=gameover_img)
    canvas_gameover.pack(fill=BOTH, expand=YES)
    fontButton = 'Helvetica 15 bold'
    boton_jugar = Button(canvas_gameover, text='JUGAR OTRA VEZ', command=instructions_screen, font=(fontButton))
    boton_jugar.config( height = 5, width = 30, fg = "black", activebackground="#6ab14b", activeforeground="white")
    boton_jugar.place(x=game.wScr/2 - 150, y=game.hScr/2 + 100)

    boton_salir = Button(canvas_gameover, text='SALIR', command=salir, font=(fontButton))
    boton_salir.config( height = 5, width = 30, fg = "black", activebackground="#6ab14b", activeforeground="white")
    boton_salir.place(x=game.wScr/2 - 150, y=game.hScr/2 + 230)
    ventana.after(1,hand_move_over)

# img=PhotoImage(file='imagen.ico')
#Label(ventana, image=img).place(x=10, y=0)
#ventana.tk.call('wn','imagen', ventana._w,img)

def jugar():
    global s
    global t
    global isPlaying
    global canvas_instructions
    global game_canvas
    global ventana
    canvas_instructions.destroy()
    canvas_hp = Canvas(ventana, height=10, width=50, bg="red")
    # canvas_hp.create_line(15, 25, 200, 25,width=10)
    # canvas_hp.create_text(sWidth/2, sHeight/2, text="HP: " )
    # canvas_hp.pack()#fill=BOTH, expand=YES)
    isPlaying = True
    s, t = setup()
    s.ontimer(timer, 10)
    # ventana.after(1,timer)
    # game_canvas.labe(game.wScr/2 ,game.hScr/2, image=gameover_img)
    label_score = Label(game_canvas, text=HP, fg='green', bg='white', font=('Helvetica', 40))
    label_score.pack()
    game_canvas.create_window(0, -380, window=label_score)
    # ventana.after(1,print_score)
    s.onclick(click)
    
    s.mainloop()

canvas_gameover = Canvas(ventana, height=500, width=500, bg="salmon")
# canvas_gameover.create_image(game.wScr/2 ,game.hScr/2, image=gameover_img)
canvas_init = Canvas(ventana, height=500, width=500, bg="salmon")
canvas_instructions = Canvas(ventana, height=500, width=500, bg="salmon")
canvas_root = Canvas(ventana, height=500, width=500, bg="salmon")
canva_hp = None
game_canvas = Canvas(ventana, height=500, width=500, bg="salmon")

# s,t=setup()
s = None
t = None
tstep = 0
# Box size
A = 100
# time for respawn the square
Delay = 25
MinDelay = 20
# time for life of square
TTL = 45
MinTTL = 20

DelayDecFact = 15
TTLDec = 3

JudgmentLine = 0.33
lastSpawn = 0
HP = 100
Score = 0
# rest HP if dont hit
HpDec = 50 ## CHANGEEEE THISS
HpInc = 1
Combo = 0
sx = []
sy = []
st = []
sttl = []
isPlaying = False

first_screen()

# Hands position
# hand_canvas = Canvas(ventana, width=game.wScr, height=game.hScr)
# hand_canvas.pack(pady=20)
hand_img = PhotoImage(file='assets/open_hand.png')
close_img = PhotoImage(file='assets/close_hand.png')
hand_img = hand_img.subsample(5, 5)
close_img = close_img.subsample(5, 5)
# img = hand_canvas.create_image(260,125, anchor=NW,image=hand_img)
tmp_pos_x ,tmp_pos_y = autopy.mouse.location()
img = canvas_root.create_image(tmp_pos_x, tmp_pos_y, image=hand_img)
img_over = canvas_gameover.create_image(tmp_pos_x, tmp_pos_y, image=hand_img)
# hands_label = Label(ventana, image=hand_img, fg='green',
#                  font=('Verdana', 80), bg='skyblue')
# hands_label.place(x=100, y=50)

first_screen()
# ventana.after(1,first_screen)
ventana.after(1,hand_move)

ventana.mainloop()
