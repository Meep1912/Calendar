import json
global files
filepaths = {
     "Days":"Data/Days.json",
     "Events":"Data/Events.json",
     "Repeats":"Data/Repeats.json"
}
files = {}
def load_files_startup():
        global files
        # Load calendar data

        for file in filepaths.keys():
            with open(filepaths[file], "r",encoding="utf-8") as f:
                files[file] = json.load(f)

def load_file(filename):
    global files
    return files[filename]

def save_file(filename, data):
    with open(filename + ".json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
     