import os
import readline
from app.command import Command

class Completer:
    completer = None

    def __init__(self, text):
        self.completions = set()
        self.complete_builtins(text)
        self.complete_executables(text)

    def complete(self, state):
        if state >= len(self.completions):
            return None
        return list(self.completions)[state]+" "

    def complete_builtins(self, text):
        for builtin in Command.BUILTINS:
            if builtin.startswith(text):
                self.completions.add(builtin)

    def complete_executables(self, text):
        for dir in os.environ["PATH"].split(":"):
            if not os.path.exists(dir):
                continue
            for executable in os.listdir(dir):
                if executable.startswith(text):
                    self.completions.add(executable)

    def completion(text, state):
        if state == 0:
            Completer.completer = Completer(text)
        return Completer.completer.complete(state)
    
    def completion_display(substitution, matches, longest_match_length):
        print("")
        print(" ".join(matches))
        print("$ " +readline.get_line_buffer(), end="")