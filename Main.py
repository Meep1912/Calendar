
from tkinter import *

from tkinter import ttk

import calendar

from datetime import datetime, date


# ============================================================
# VARIABLES
# ============================================================


# ------------------------------------------------------------
# Time
# ------------------------------------------------------------

current_second = datetime.now().second
current_minute = datetime.now().minute
current_hour = datetime.now().hour
current_day = datetime.now().day
current_month = datetime.now().month
current_year = datetime.now().year


# ------------------------------------------------------------
# General
# ------------------------------------------------------------

name = 0
day = 0
row1 = 0
column1 = 0
scale = 1
xy_offset = [50,100]
mode = "month"
day_buttons = []


# ------------------------------------------------------------
# Window
# ------------------------------------------------------------

mainwindow = Tk()
mainwindow.title("Project")
mainwindow.geometry("600x400")


# ------------------------------------------------------------
# Display settings
# ------------------------------------------------------------

if mode =="month":

    scale = 2
    true_scale = 1 / scale
    global current_display_month, current_display_year
    current_display_month = current_month
    current_display_year = current_year

elif mode =="year":
    scale = 4
    true_scale = 1 / scale


# ------------------------------------------------------------
# Images
# ------------------------------------------------------------

image1 = PhotoImage(file="Empty.png")
image2 = PhotoImage(file="Full.png")
image3 = PhotoImage(file="Today.png")

day_yet_to_come_icon = image1.subsample(scale,scale)
day_came_icon = image2.subsample(scale,scale)
today_icon = image3.subsample(scale,scale)


# ============================================================
# FUNCTIONS
# ============================================================


# ------------------------------------------------------------
# Change displayed month
# ------------------------------------------------------------

def change_month(sign,xy_offset,spacing,true_scale):
    global current_display_month, current_display_year
    if sign == "-":
        if current_display_month != 1:
            current_display_month -= 1

        else:
            current_display_year -=1
            current_display_month = 12

    elif sign == "+":
        if current_display_month != 12:
            current_display_month += 1

        else:
            current_display_year += 1
            current_display_month = 1

    elif sign == "O":
        current_display_month = current_month

    draw_month(xy_offset,spacing,true_scale,current_day,current_month,current_year)



# ------------------------------------------------------------
# Get mouse coordinates
# ------------------------------------------------------------

def update_coords():

     x = mainwindow.winfo_pointerx() - mainwindow.winfo_rootx()
     y = mainwindow.winfo_pointery() - mainwindow.winfo_rooty()

     return x , y


# ------------------------------------------------------------
# When a day button is pressed
# ------------------------------------------------------------

def pressed1(day): 
    draw_day_veiw(day)


# ------------------------------------------------------------
# Day view window
# ------------------------------------------------------------

global current_day_frame
current_day_frame = None


def draw_day_veiw(day):
    global current_day_frame,current_display_year
    month_name = calendar.month_name[current_display_month]
    if current_day_frame is not None:
        current_day_frame.destroy()
    current_day_frame = Toplevel()
    current_day_frame.title("Project")
    current_day_frame.geometry("600x400")
    ttk.Label(
        current_day_frame,
        text=str(day) + " " + month_name + " "+ str(current_display_year),
        font=("Times New Roman",15,"bold")).place(x=30,y=0)


# ------------------------------------------------------------
# Close day view
# ------------------------------------------------------------

def close_day_view():
    global current_day_frame
    current_day_frame.destroy()
    current_day_frame = None


# ------------------------------------------------------------
# Draw the month
# ------------------------------------------------------------

def draw_month(xy_offset,spacing,true_scale,current_day,current_month,current_year):
    global current_display_month
    month_name = calendar.month_name[current_display_month]
    month_label.config(text=month_name+" "+str(current_display_year))
    kill_button()
    for i in range(calendar.monthrange(current_year,current_display_month)[1]):
        x = (i % 10) * 50*true_scale*spacing + xy_offset[0]
        y = (i // 10) * 50*true_scale*spacing + xy_offset[1]
        button_date = date(current_display_year,current_display_month,i + 1)
        today = date(current_year,current_month,current_day)


        # Determine whether this day is in the past,
        # is today, or is still in the future.

        if button_date < today:
            btn = Button(
                mainwindow,
                image=day_came_icon,
                command=lambda day=i+1: pressed1(day),
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                bd=0,
                padx=0,
                pady=0)

        if button_date > today:
            btn = Button(
                mainwindow,
                image=day_yet_to_come_icon,
                command=lambda day=i+1: pressed1(day),
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                bd=0,
                padx=0,
                pady=0)

        if button_date == today:
            btn = Button(
                mainwindow,
                image=today_icon,
                command=lambda day=i+1: pressed1(day),
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                bd=0,
                padx=0,
                pady=0)
        btn.place(x=x, y=y)
        day_buttons.append(btn)


# ------------------------------------------------------------
# Delete all existing day buttons
# ------------------------------------------------------------

def kill_button():

    for btn in day_buttons:
        if btn is not None:
            btn.destroy()
    day_buttons.clear()


# ============================================================
# GUI
# ============================================================


# ------------------------------------------------------------
# Top buttons
# ------------------------------------------------------------

ttk.Button(
    mainwindow,
    text="Quit",
    command=mainwindow.destroy).place(x=0,y=0)


ttk.Button(
    mainwindow,
    text="Help").place(x=80,y=0)


ttk.Button(
    mainwindow,
    text="Settings").place(x=160,y=0)


# ------------------------------------------------------------
# Month navigation buttons
# ------------------------------------------------------------

Button(
       mainwindow,
       command=lambda : change_month("-",xy_offset,spacing,true_scale), 
       text="<",
       borderwidth=0,
       highlightthickness=0,
       relief="flat",
       bd=0,
       padx=0,
       pady=0).place(x=220,y=70)


Button(
       mainwindow,
       command=lambda : change_month("O",xy_offset,spacing,true_scale), 
       text="O",
       borderwidth=0,
       highlightthickness=0,
       relief="flat",
       bd=0,
       padx=0,
       pady=0).place(x=280,y=70)


Button(
       mainwindow,
       command=lambda : change_month("+",xy_offset,spacing,true_scale), 
       text=">",
       borderwidth=0,
       highlightthickness=0,
       relief="flat",
       bd=0,
       padx=0,
       pady=0

).place(x=340,y=70)


# ------------------------------------------------------------
# Labels
# ------------------------------------------------------------

if mode =="month":
        
    label1 = Label(mainwindow,text="")
    label1.place(x=0,y=0)
    
    month_label = Label(mainwindow,text="")
    month_label.place(x=240,y=50)

    spacing = 2

    draw_month(
        xy_offset,
        spacing,
        true_scale,
        current_day,
        current_month,
        current_year
    )



elif mode =="year":
    pass


# ------------------------------------------------------------
# Day window close protocol
# ------------------------------------------------------------

if current_day_frame is not None:
    current_day_frame.protocol("WM_DELETE_WINDOW", close_day_view)


# ============================================================
# MAIN LOOP
# ============================================================

mainwindow.mainloop()


