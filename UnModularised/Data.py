
global files
files = {}
def load_files_startup():
        global files
        # Load calendar data

        with open("Days.json", "r") as f:
            files["days"] = json.load(f)

        with open("Events.json", "r") as f:
            files["events"] = json.load(f)

        with open("Repeats.json", "r") as f:
            files["repeats"] = json.load(f)

        # Load Module data

        with open("Comprehension.json", "r") as f:
            files["comprehension"] = json.load(f)

def load_file(filename):
    global files
    return files[filename]

def save_file(filename):
    global files
    with open(filename.capitalize() + ".json", "w") as f:
        json.dump(files[filename], f, indent=4)
     

        