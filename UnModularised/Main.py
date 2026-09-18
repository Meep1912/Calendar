
from tkinter import *

from tkinter import ttk, colorchooser

import calendar

from datetime import datetime, date

from Data import *

from Comprehension import *

load_files_startup()

# VARIABLES


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
calendar_zoom = 20                                                                                                                  

# ------------------------------------------------------------
# Window
# ------------------------------------------------------------

mainwindow = Tk()
mainwindow.title("Project")
mainwindow.geometry("600x400")


# ------------------------------------------------------------
# Display settings
# ------------------------------------------------------------

if mode == "month":
    scale = 2
    true_scale = 1 / scale
    current_display_date = [current_month, current_year]

elif mode == "year":
    scale = 4
    true_scale = 1 / scale

# Images


image1 = PhotoImage(file="Empty.png")
image2 = PhotoImage(file="Full.png")
image3 = PhotoImage(file="Today.png")

day_yet_to_come_icon = image1.subsample(scale,scale)
day_came_icon = image2.subsample(scale,scale)
today_icon = image3.subsample(scale,scale)


# FUNCTIONS

# function which sets the month veiw


def change_month(sign, xy_offset, spacing, true_scale):

    global current_display_date

    if sign == "+":

        if current_display_date[0] != 1:
            current_display_date[0] -= 1
        else:
            current_display_date[1] -= 1
            current_display_date[0] = 12

    elif sign == "-":

        if current_display_date[0] != 12:
            current_display_date[0] += 1
        else:
            current_display_date[1] += 1
            current_display_date[0] = 1

    elif sign == "O":

        current_display_date[0] = datetime.now().month
        current_display_date[1] = datetime.now().year

    draw_month(xy_offset, spacing, true_scale)

# Get mouse coordinates

def update_coords():

     x = mainwindow.winfo_pointerx() - mainwindow.winfo_rootx()
     y = mainwindow.winfo_pointery() - mainwindow.winfo_rooty()

     return x , y


# Day view window


current_day_frame = None

def draw_day_veiw(day):

    global current_day_frame, calendar_zoom

    month_name = calendar.month_name[current_display_date[0]]

    # detect if there is a day frame already being displayed
    if current_day_frame is not None:
        current_day_frame.destroy()

    # window settings

    current_day_frame = Toplevel()
    current_day_frame.title("Project")
    current_day_frame.geometry("600x400")

    # scroll bar logic

    canvas = Canvas(current_day_frame)
    scrollbar = ttk.Scrollbar(current_day_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, width=600,height=100*calendar_zoom)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    current_day_frame.bind("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
    current_day_frame.bind("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
    

    # Label showing the day month and year of the clicked dot
    ttk.Label(
        scrollable_frame,
        text=str(day) + " " + month_name + " "+ str(current_display_date[1]),
        font=("Times New Roman",15,"bold")).place(x=30,y=0)

    # zoom buttons
    inc = Button(
        scrollable_frame,
        text="+",
        command= lambda: calendar_zoom_function("+",day)).place(x=200,y=0)            
    dec = Button(
        scrollable_frame,
        text="-",
        command= lambda: calendar_zoom_function("-",day)).place(x=220,y=0)


    # add event button
    ttk.Button(
        scrollable_frame,
        text="add event",
        command=lambda: add_event_veiw(day)
    ).place(x=30,y=30)

    # -------render the current events-----------
    
    # load files

    days_json = load_file("Days")
    events_json = load_file("Events")
    repeats_json = load_file("Repeats")
    
    # Get day of the week
    day_name = date(current_display_date[1],current_display_date[0],day).strftime("%A")

    # get events on that day (day of the week)
    day_name = "Every "+day_name
    repeating_events = repeats_json[day_name]
    # add the daily events
    repeating_events.extend(repeats_json["Every Day"])

    # format the clicked day's date into a key for Days.json
    temp = f"{day:02d}|{current_display_date[0]:02d}|{current_display_date[1]}"
    # fetch a list of events
    events = days_json[temp]
    # append list of events for repeating_events making sure no duplicates r pressent
    for event in repeating_events:
        if event not in events:
            events.append(event)

    # The events coraspond to keys in Events.json this fetches the data for each event in that day
    list_of_events_and_data = []
    for event in events:
        list_of_events_and_data.append(events_json[event])

    # Creates a list of values corasponding to time
    grid_ = []
    y1=0
    for hour in range(24):
        for minute in range(0, 60, 30):
            grid_.append(f"{hour:02d}:{minute:02d}")
    grid_.append("24:00")

    # make a label for each time with increasing distance
    for time in grid_:
        ttk.Label(
                    scrollable_frame,
                    borderwidth=0,
                    relief="flat",
                    text=time).place(x=0,y=(y1*calendar_zoom+80))
        
        y1 += 1
    
    i = 0

    # Create a frame for each event
    for event in list_of_events_and_data:

        data = event.split("|")
        title = events[i]
        start_time = data[0]
        duration = data[1] 
        duration = duration_to_mins(duration)
        colour = data[2]
        description = data[3]

        # work out start_time in mins
        start_time_mins = start_time.split(":")
        hours = int(start_time_mins[0])
        mins = int(start_time_mins[1])
        start_time_mins = hours*60 + mins

        height1 = int(duration) / 30 * calendar_zoom 
        y1 =start_time_mins / 30* calendar_zoom  + 80

        cool_event = Frame(
            scrollable_frame,
            width=400,
            height=height1,
            bg=colour,
        )
        cool_event.place(x=50,y=y1)
        cool_event.lift()
        cool_event.bind("<Button-1>", lambda event: event_clicked(title,day))

        cool_label = Label(
            cool_event,
            text=title,
            relief="flat",
            border=0,
            bg=colour
        )
        cool_label.place(x=10,y=20)
        cool_label.lift()
        cool_label.bind("<Button-1>", lambda event: event_clicked(title,day))
        if height1 > 100:
            Label(
                cool_event,
                text=description,
                relief="flat",
                border=0,
                bg=colour
            ).place(x=10,y=40)
        i += 1

current_event_frame = None

def calendar_zoom_function(zoom,day):
    global calendar_zoom

    if zoom == "+" and calendar_zoom +10 != 200:
        calendar_zoom += 10
    if zoom == "-" and calendar_zoom -10 != 0:
        calendar_zoom -= 10
    draw_day_veiw(day)
    
def event_clicked(Title,day):
    global current_event_frame, current_display_date
    # detect if there is a day frame already being displayed
    if current_event_frame is not None:
        current_event_frame.destroy()

    # window settings

    current_event_frame = Toplevel()
    current_event_frame.title("Project")
    current_event_frame.geometry("800x600")

    Label(
        current_event_frame,
        text=Title
    ).place(x=10,y=10)
    if Title == "Comprehension":
        draw_comprehension(day, current_display_date[0], current_display_date[1], current_event_frame)
        

add_event_frame = None

def duration_to_mins(x):

    if "Whole day" in x:
        return 1440
    if "hour" in x:
        parts = x.split()
        hours = int(parts[0])
        if "min" in x:
            mins = int(parts[2])
        else:
            mins = 0
        return hours*60+mins
    if "min" in x:
        mins = x.split()[0]
        return mins
    
def add_event_veiw(day):
    global add_event_frame, colour_picked
    if add_event_frame is not None:
        add_event_frame.destroy()
    add_event_frame = Toplevel()
    current_day_frame.title("Project")
    add_event_frame.geometry("600x400")
    # title
    ttk.Label(
        add_event_frame,
        text="Title",
        font=("Times New Roman",15,"bold")).place(x=0,y=0)
    Title_entry = ttk.Entry(
        add_event_frame,
    )
    Title_entry.place(x=0,y=25)

    # Start time

    start_times = []
    for hour in range(24):
        for minute in range(0, 60, 15):
            start_times.append(f"{hour:02d}:{minute:02d}")
    ttk.Label(
        add_event_frame,
        text="Start Time",
        font=("Times New Roman",15,"bold")).place(x=0,y=50)
    Start_Entry = ttk.Combobox(
        add_event_frame,
        values=start_times
        )
    Start_Entry.place(x=0,y=75)

    # duration

    durations = ["5 min", "10 min", "15 min", "20 min",
                 "30 min", "40 min", "50 min", "1 hour",
                 "1 hour 30 min", "2 hours", "2 hours 30 min",
                 "3 hours", "4 hours", "5 hours", "6 hours",
                 "7 hours", "8 hours", "9 hours", "10 hours",
                 "11 hours", "Whole day"]
    ttk.Label(
        add_event_frame,
        text="Duration",
        font=("Times New Roman",15,"bold")).place(x=0,y=100)
    duration_entry = ttk.Combobox(
        add_event_frame,
        values=durations
        )
    duration_entry.place(x=0,y=125)

    # Colour picker

    ttk.Label(
        add_event_frame,
        text="Colour",
        font=("Times New Roman",15,"bold")).place(x=0,y=150)
    
    colour_button = Button(
    add_event_frame,
    text="Choose Colour",
    command=choose_colour,
    )
    colour_button.place(x=0,y=175)

    
    
    # Description
    ttk.Label(
        add_event_frame,
        text="Description",
        font=("Times New Roman",15,"bold")).place(x=0,y=220)
    Description_entry = Text(
        add_event_frame,
        height = 5,
        width = 30,
    )
    Description_entry.place(x=0,y=245)
    
    # Repeats
    repeats = ["No Repeat","Every Day","Every Monday","Every Tuesday",
               "Every Wendnesday","Every Thursday","Every Friday",
               "Every Saturday","Every Sunday",]
    ttk.Label(
        add_event_frame,
        text="Repeats",
        font=("Times New Roman",15,"bold")).place(x=200,y=0)
    repeats_entry = ttk.Combobox(
            add_event_frame,
            values=repeats
            )
    repeats_entry.place(x=200,y=25)
    repeats_entry.insert(0,"No Repeat")
    # Done button
    Done_Button = Button(
        add_event_frame,
        text="Done!",
        command=lambda: Updates(Title_entry.get(),Start_Entry.get(),duration_entry.get(),colour_picked,Description_entry.get("1.0", "end"),day,repeats_entry.get()),
        )
    Done_Button.place(x=0,y=350)


def Updates(Title,Start,duration,colour,description,day,repeat_period):
    Update_json(Title,Start,duration,colour,description)
    Update_Days(Title, day)
    Update_Repeats(Title,repeat_period)
    add_event_frame.destroy()

def Update_Repeats(Title,repeat_period):
    # load the data in repeats
    repeats_json = load_file("Repeats")
    # get the current repeating events on that schedule
    current_repeating_events = repeats_json[repeat_period]
    # add title / event to existing events
    current_repeating_events.append(Title)
    # write back to file
    save_file("Repeats",repeats_json)



def Update_json(Title,Start,duration,colour,description):

    events_json = load_file("Events")

    event_dictionary = {
        Title: Start +"|"+ duration+"|"+ colour+"|"+description}
    
    events_json.update(event_dictionary)

    save_file("Events",events_json)


def Update_Days(Title, day):

    global current_display_date
    days_json = load_file("Days")
    temp = f"{day:02d}|{current_display_date[0]:02d}|{current_display_date[1]}"
    days_json[temp].append(Title)
    save_file("Days",days_json)




def choose_colour():
    global colour_picked
    colour_picked = colorchooser.askcolor()[1]

def close_day_view():
    global current_day_frame
    current_day_frame.destroy()
    current_day_frame = None



# Draw month

def draw_month(xy_offset, spacing, true_scale):

    current_display_month = current_display_date[0]
    current_display_year = current_display_date[1]

    month_name = calendar.month_name[current_display_month]

    month_label.config(text=month_name + " " + str(current_display_year))

    kill_button()

    for i in range(calendar.monthrange(current_display_year, current_display_month)[1]):

        x = (i % 10) * 50 * true_scale * spacing + xy_offset[0]

        y = (i // 10) * 50 * true_scale * spacing + xy_offset[1]

        button_date = date(current_display_year,current_display_month,i + 1)
        today = date.today()

        # this day is in the past,
        # is today, or is still in the future.

        if button_date < today:

            btn = Button(
                mainwindow,
                image=day_came_icon,
                command=lambda day=i+1: draw_day_veiw(day),
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                bd=0,
                padx=0,
                pady=0
            )

        if button_date > today:

            btn = Button(
                mainwindow,
                image=day_yet_to_come_icon,
                command=lambda day=i+1: draw_day_veiw(day),
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                bd=0,
                padx=0,
                pady=0
            )

        if button_date == today:

            btn = Button(
                mainwindow,
                image=today_icon,
                command=lambda day=i+1: draw_day_veiw(day),
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
                bd=0,
                padx=0,
                pady=0
            )

        btn.place(x=x, y=y)
        day_buttons.append(btn)



# Delete all day buttons


def kill_button():

    for btn in day_buttons:
        if btn is not None:
            btn.destroy()
    day_buttons.clear()


# GUI

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


Button(
       mainwindow,
       command=lambda : change_month("+",xy_offset,spacing,true_scale), 
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
       command=lambda : change_month("-",xy_offset,spacing,true_scale), 
       text=">",
       borderwidth=0,
       highlightthickness=0,
       relief="flat",
       bd=0,
       padx=0,
       pady=0).place(x=340,y=70)


if mode =="month":
        
    label1 = Label(mainwindow,text="")
    label1.place(x=0,y=0)
    
    month_label = Label(mainwindow,text="")
    month_label.place(x=240,y=50)

    spacing = 2

    draw_month(xy_offset, spacing, true_scale)  



elif mode =="year":
    pass


if current_day_frame is not None:
    current_day_frame.protocol("WM_DELETE_WINDOW", close_day_view)



mainwindow.mainloop()


