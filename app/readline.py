import os
import readline
from app.command import Command

class Readline:
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
            Readline.completer = Readline(text)
        return Readline.completer.complete(state)
    
    def completion_display(substitution, matches, longest_match_length):
        print("")
        print(" ".join(matches))
        print("$ " +readline.get_line_buffer(), end="")

    def setup():
        readline.set_completer(Readline.completion)
        if readline.backend == "editline":
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind('tab: complete')
            readline.set_completion_display_matches_hook(Readline.completion_display)
        