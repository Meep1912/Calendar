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
xy_offset = [50,100]
mode = "month"

# window 
mainwindow = Tk()
mainwindow.title("Project")
mainwindow.geometry("600x400")



if mode =="month":
    scale = 2
    true_scale = 1 / scale
    current_display_month = current_month

elif mode =="year":
    scale = 4
    true_scale = 1 / scale

image1 = PhotoImage(file="Empty.png")
image2 = image1.subsample(scale,scale)


ttk.Button(mainwindow, text="Quit", command=mainwindow.destroy).place(x=0,y=0)
ttk.Button(mainwindow, text="Help", ).place(x=80,y=0)
ttk.Button(mainwindow, text="Settings", ).place(x=160,y=0)

Button(
       mainwindow,
       command=lambda : change_month("-"), 
       text="<",
       borderwidth=0,
       highlightthickness=0,
       relief="flat",
       bd=0,
       padx=0,
       pady=0).place(x=220,y=70)

Button(
       mainwindow,
       command=lambda : change_month("O"), 
       text="O",
       borderwidth=0,
       highlightthickness=0,
       relief="flat",
       bd=0,
       padx=0,
       pady=0).place(x=280,y=70)

Button(
       mainwindow,
       command=lambda : change_month("+"), 
       text=">",
       borderwidth=0,
       highlightthickness=0,
       relief="flat",
       bd=0,
       padx=0,
       pady=0).place(x=340,y=70)

def change_month(sign):
    if sign == "-":
        current_display_month -= 1
        draw_month(xy_offset,spacing,current_display_month,true_scale)
    elif sign == "+":
        current_display_month += 1
        draw_month(xy_offset,spacing,current_display_month,true_scale)
    elif sign == "O":
        current_display_month = current_month
        draw_month(xy_offset,spacing,current_display_month,true_scale)


def update_coords():
     x = mainwindow.winfo_pointerx() - mainwindow.winfo_rootx()
     y = mainwindow.winfo_pointery() - mainwindow.winfo_rooty()
     return x , y

def pressed1(day): 
    label1.config(text=day)

def draw_month(xy_offset,spacing,month,true_scale,):

    for i in range(calendar.monthrange(current_year,month)[1]):
        x = (i % 10) * 50*true_scale*spacing + xy_offset[0]
        y = (i // 10) * 50*true_scale*spacing + xy_offset[1]

        Button(
            mainwindow,
            image=image2,
            command=lambda day=i+1: pressed1(day),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            bd=0,
            padx=0,
            pady=0
        ).place(x=x, y=y)




label1 = Label(mainwindow, text="")
label1.place(x=0,y=0)

if mode =="month":
    spacing = 2
    draw_month(xy_offset,spacing,current_display_month,true_scale)


elif mode =="year":
    pass


# loading and scaling image


mainwindow.mainloop()

