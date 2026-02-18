from pathlib import Path


class GCodeModel:
    def __init__(self):
    #store gcode lines as bytes in a list not str
    #important becasue when writing to serial port it needs to be bytes
        self.lines: list[bytes] = []
        self.cleaned: list[bytes] = []
        self.loaded_name: str = ""
        self.total: int = 0
        self.sent: int = 0
        self.paused: bool = False

    def load_from_file(self, path: str) -> int:
        file_path = Path(path)
        #reset variables
        self.lines = []
        self.cleaned = []
        self.total = 0
        self.sent = 0
        self.paused = False

        #reads from gcode file, and stores it in variable text as a big string
        text = file_path.read_text(encoding="utf-8")
        #split text into lines and store as list of bytes, it splits at \n, the /n charcaters are saved when reading from the gcode file
        for raw in text.splitlines():
            line =raw.strip()
            #this gets rid of empty lines and comments
            if not line or line.startswith(";"):
                continue
            #this gets rid of comments after a command
            semi = line.find(";")
            if semi != -1:
                line = line[:semi].strip()
                #this checks if it was a comment only line
                if not line:
                    continue
            self.cleaned.append((line +"\r\n").encode("ascii"))

        self.lines = self.cleaned
        self.loaded_name = file_path.name
        self.total = len(self.cleaned)
        self.sent = 0
        self.paused = False
        return self.total
        

    def reset_job_counters(self):
        self.sent = 0
        self.paused = False

"""
if __name__ == "__main__":
    model = GCodeModel()
    count = model.load_from_file("DG_UI\cube-svgrepo-com.gcode")
    print(f"Loaded {count} lines from test.gcode")
    for line in model.lines:
        print(line)"""