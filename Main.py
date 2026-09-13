from tkinter import *
from tkinter import ttk
import calendar
import json
from datetime import datetime



####  Variables

# Time
current_second = datetime.now().second
current_minute = datetime.now().minute
current_hour = datetime.now().hour

current_day = datetime.now().day
current_month = datetime.now().month
current_year = datetime.now().year

# General  
name = 0
day = 0
row1 = 0
column1 = 0
scale = 1
xy_offset = [0,50]
mode = "month"

# window 
mainwindow = Tk()
mainwindow.title("Project")
mainwindow.geometry("600x400")

# loading and scaling image

if mode =="month":
    global true_scale
    scale = 2
    true_scale = (1/scale)

image1 = PhotoImage(file="Empty.png")
image2 = image1.subsample(scale,scale)



#ttk.Button(mainwindow, text="Quit", command=mainwindow.destroy).grid(column=0,row=0)
#ttk.Button(mainwindow, text="Help", ).grid(column=1,row=0)
#ttk.Button(mainwindow, text="Settings", ).grid(column=2,row=0)

def update_coords():
     x = mainwindow.winfo_pointerx() - mainwindow.winfo_rootx()
     y = mainwindow.winfo_pointery() - mainwindow.winfo_rooty()
     return x , y

def pressed1(mode,xy_offset):

    # when any day button is pressed, runs update_coords which returns x+y of mouse,
    # these values are ajusted based off the scale of the boxes and the offset they have

    if mode == "month":
        base = 50 * true_scale
        x,y = update_coords()
        x -= xy_offset[0]
        y -= xy_offset[1]
        print("xy: ",x,y)
        x = myround(x)
        y = myround(y)
        print("x_round,y: ",x,y)
        x = x + 10*y
        clicked_day = x
        label1.config(text=f"{clicked_day}")

def myround(a):
    base = 50*true_scale
    nearest_a =  base * round(a/base)
    return nearest_a / base



def draw_days(xy_offset):
    y_ = 0
    x_ = 0
    temp = 0
    for i in range(31):
        x = (i % 10) * 50 + xy_offset[0]
        y = (i // 10) * 50 + xy_offset[1]

        Button(
            mainwindow,
            image=image2,
            command=lambda: pressed1(mode, xy_offset),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            bd=0,
            padx=0,
            pady=0).place(x=x, y=y)

label1 = Label(mainwindow, text="")
label1.place(x=0,y=0)

draw_days(xy_offset)

mainwindow.mainloop()

