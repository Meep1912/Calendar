from tkinter import *
from tkinter import ttk
from Data import load_file, save_file

def draw_comprehension(day, current_display_month, current_display_year, current_event_frame):

    Comprehension_json = load_file("Comprehension")

        # scroll bar logic

    canvas3 = Canvas(current_event_frame)
    scrollbar3 = ttk.Scrollbar(current_event_frame, orient="vertical", command=canvas3.yview)
    scrollable_frame3 = Frame(canvas3, height=4000,width=600)
    scrollable_frame3.bind(
        "<Configure>",
        lambda e: canvas3.configure(scrollregion=canvas3.bbox("all"))
    )
    canvas3.create_window((0, 0), window=scrollable_frame3, anchor="nw")
    canvas3.configure(yscrollcommand=scrollbar3.set)
    canvas3.pack(side="left", fill="both", expand=True)
    scrollbar3.pack(side="right", fill="y")
    current_event_frame.bind("<Button-4>", lambda event: canvas3.yview_scroll(-1, "units"))
    current_event_frame.bind("<Button-5>", lambda event: canvas3.yview_scroll(1, "units"))

    key = f"{day:02d}|{current_display_month:02d}|{current_display_year}"

    todays_stuff = Comprehension_json[key]
    text = todays_stuff["text"]
    questions = todays_stuff["questions"]
    correct_answer = todays_stuff["correct_answer"]
    given_answers = todays_stuff["given_answer"]
    spacing = 100
    answer_boxes = []
    while len(given_answers) < len(questions):
        given_answers.append("")
    Main = Text(
        scrollable_frame3,
        height=13,
        width=50,
        font=(8))
    Main.place(x=10,y=40)
    Main.insert("1.0",text)
    for i in range(0,len(questions)):

            question = Text(scrollable_frame3,height=2,width=45,font=(8))
            question.place(x=10,y=350 + i * spacing)
            question.insert("1.0", questions[i])
            question.config(state="disabled")

            answer = Entry(scrollable_frame3,width=45)
            answer.place(x=10,y=410 + i * spacing)
            answer.insert("0",given_answers[i])
            answer_boxes.append(answer)

    submit_button = Button(
        scrollable_frame3,
        text="Done!",
        command=lambda: submit_comprehension(answer_boxes,Main,todays_stuff,Comprehension_json,key)) 
    submit_button.place(y=5,x=220)

    add_questions = Button(
        scrollable_frame3,
        text="Add",
        command=lambda:add_question_veiw(key))
    add_questions.place(x=120,y=5)

    # save 
global add_questions_frame
add_questions_frame= None


def add_question_veiw(key):
    global add_questions_frame
    # detect if there is a day frame already being displayed
    if add_questions_frame is not None:
        add_questions_frame.destroy()

    # window settings

    add_questions_frame = Toplevel()
    add_questions_frame.title("Project")
    add_questions_frame.geometry("600x700")

    # scroll bar logic

    canvas2 = Canvas(add_questions_frame)
    scrollbar2 = ttk.Scrollbar(add_questions_frame, orient="vertical", command=canvas2.yview)
    scrollable_frame2 = Frame(canvas2, height=4000,width=600)
    scrollable_frame2.bind(
        "<Configure>",
        lambda e: canvas2.configure(scrollregion=canvas2.bbox("all"))
    )
    canvas2.create_window((0, 0), window=scrollable_frame2, anchor="nw")
    canvas2.configure(yscrollcommand=scrollbar2.set)
    canvas2.pack(side="left", fill="both", expand=True)
    scrollbar2.pack(side="right", fill="y")
    add_questions_frame.bind("<Button-4>", lambda event: canvas2.yview_scroll(-1, "units"))
    add_questions_frame.bind("<Button-5>", lambda event: canvas2.yview_scroll(1, "units"))

    # entry box for string of text
    question = Text(
        scrollable_frame2,
        height=150,
        width=90,
        font=("Noto Sans CJK JP", 12))
    question.place(
                x=10,
                y=40,
                )
    # button to enter data into decoder
    submit_add_questions = Button(
        scrollable_frame2,
        text="Done!",
        command=lambda:decode_question_data(question.get("1.0", "end-1c")))
    submit_add_questions.place(x=10,y=0)




 
def decode_question_data(data):
    data_list = data.splitlines()
    Comprehension_json = load_file("Comprehension")
    date_indexes = [
        i for i, line in enumerate(data_list)
        if line == "Date"
    ]
    for i, date_index in enumerate(date_indexes):
        # End of this day's data
        if i + 1 < len(date_indexes):
            end = date_indexes[i + 1]
        else:
            end = len(data_list)
        day_data = data_list[date_index:end]
        Text_start = day_data.index("Text")
        Questions_start = day_data.index("Questions")
        Answers_start = day_data.index("Answers")
        date = day_data[1]
        text = "\n".join(day_data[Text_start + 1:Questions_start])
        questions = day_data[Questions_start + 1:Answers_start]
        answers = day_data[Answers_start + 1:]

        Comprehension_json[date] = {
            "text": text,
            "questions": questions,
            "correct_answer": answers,
            "given_answer":[]}

        save_file("Comprehension",Comprehension_json)


def submit_comprehension(answer_boxes,Main,todays_stuff,Comprehension_json,key):
    given_answers = []
    # get entry anwsers in a list
    for box in answer_boxes:
        given_answers.append(box.get())
    # get main text
    Main_Text = Main.get("1.0", "end-1c")
    # submit button
    # edit todays stuff with updated main text and given anwsers
    todays_stuff["text"] = Main_Text
    todays_stuff["given_answer"] = given_answers
    # update whole dict
    Comprehension_json[key] = todays_stuff
    # give dict to save function
    save_file("Comprehension",Comprehension_json)
    