import turtle
import random

def setup():
    s=turtle.Screen()
    t=turtle.Turtle()
    s.setup(960,540)
    t.hideturtle()
    t.up()
    t.speed(0)
    turtle.tracer(0,0)
    return s,t

def drawCSq(t,cx,cy,a):
    t.goto(cx-(a/2),cy-(a/2))
    t.down()
    t.goto(cx+(a/2),cy-(a/2))
    t.goto(cx+(a/2),cy+(a/2))
    t.goto(cx-(a/2),cy+(a/2))
    t.goto(cx-(a/2),cy-(a/2))
    t.up()

def timer():
    global tstep
    global sx
    global sy
    global lastSpawn
    global Delay
    global HP
    global Score
    global Combo

    if tstep>=lastSpawn+Delay:
        sx.append(random.randrange(-320+A,320-A))
        sy.append(random.randrange(-240+A,240-A))
        st.append(tstep)
        sttl.append(TTL)
        lastSpawn=tstep
        Delay-=max(1,Delay//DelayDecFact)
        Delay=max(MinDelay,Delay)

    j=0
    while j<len(sx):
        if(st[j]+sttl[j]<tstep):
            del st[j]
            del sttl[j]
            del sx[j]
            del sy[j]
            HP-=HpDec
            HP=max(0,HP)
            Combo=0
            print("HP:",HP,"Score:",Score,"Combo:",Combo,"Last Hit:",0)
        else:
            j+=1

    t.clear()

    for i in range(len(sx)):
        drawCSq(t,sx[i],sy[i],A)
        A2=A*((sttl[i]+st[i]-tstep-(sttl[i]*JudgmentLine))/sttl[i])
        if(A2>0):
            drawCSq(t,sx[i],sy[i],A+A2)

    s.update()
    tstep+=1
    if HP>0:
        s.ontimer(timer,10)
    else:
        s.bye()

def click(x,y):
    global TTL
    global HP
    global Score
    global Combo

    if len(sx)>0 and sx[0]-(A/2)<x and sx[0]+(A/2)>x and sy[0]-(A/2)<y and sy[0]+(A/2)>y:
        TTL-=TTLDec
        TTL=max(MinTTL,TTL)
        HP+=HpInc
        HP=min(100,HP)
        Combo+=1
        HitDiff=abs((st[0]+(sttl[0]*(1-JudgmentLine)))-tstep)
        HitDiffPre=1-(HitDiff/(sttl[0]*(1-JudgmentLine)))
        LastHit=50+int(250*HitDiffPre)
        Score+=Combo*LastHit
        print("HP:",HP,"Score:",Score,"Combo:",Combo,"Last Hit:",LastHit)
        del sx[0]
        del sy[0]
        del st[0]
        del sttl[0]

    t.clear()

    for i in range(len(sx)):
        drawCSq(t,sx[i],sy[i],A)
        A2=A*((sttl[i]+st[i]-tstep-(sttl[i]*JudgmentLine))/sttl[i])
        if(A2>0):
            drawCSq(t,sx[i],sy[i],A+A2)

    s.update()

s,t=setup()
tstep=0
A=50
Delay=200
TTL=100
DelayDecFact=15
TTLDec=5
MinDelay=30
MinTTL=45
JudgmentLine=0.33
lastSpawn=0
HP=100
Score=0
HpDec=5
HpInc=1
Combo=0
sx=[]
sy=[]
st=[]
sttl=[]

s.ontimer(timer,10)
s.onclick(click)
s.mainloop()
