from tkinter import *
from tkinter import ttk
import json
name = 0
day = 0
row1 = 0
column1 = 0

mainwindow = Tk()
canvas = Canvas()
mainwindow.title("Project")
mainwindow.geometry("600x400")
image1 = PhotoImage(file="Empty.png")

ttk.Button(mainwindow, text="Quit", command=mainwindow.destroy).pack(anchor="ne",side="right")
ttk.Button(mainwindow, text="Help", ).pack(anchor="nw",side="left")
ttk.Button(mainwindow, text="Settings", ).pack(anchor="nw",side="left")

ttk.Button(mainwindow, text="Quit", command=mainwindow.destroy,image=image1).pack(anchor="ne",side="right")

canvas.pack(anchor="center")
mainwindow.mainloop()

