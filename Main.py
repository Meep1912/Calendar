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

class circle():
    def __init__(self,name,day,row1,column1):
        self.name = name
        self.day = day
        self.row = row1
        self.column = column1
        ttk.Button(mainwindow, text="1",command=self.run()).grid(row=row1,column=column1)
    def run():
        pass
ttk.Button(mainwindow, text="Quit", command=mainwindow.destroy).pack(anchor="ne",side="right")
ttk.Button(mainwindow, text="Help", ).pack(anchor="nw",side="left")
ttk.Button(mainwindow, text="Settings", ).pack(anchor="nw",side="left")
canvas.pack(anchor="center")
mainwindow.mainloop()
