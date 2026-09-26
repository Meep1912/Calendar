import json
global files
files = {}
def load_files_startup():
        global files
        # Load calendar data

        with open("Days.json", "r",encoding="utf-8") as f:
            files["Days"] = json.load(f)

        with open("Events.json", "r",encoding="utf-8") as f:
            files["Events"] = json.load(f)

        with open("Repeats.json", "r",encoding="utf-8") as f:
            files["Repeats"] = json.load(f)
        # Load Module data


def load_file(filename):
    global files
    return files[filename]

def save_file(filename, data):
    with open(filename + ".json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
     