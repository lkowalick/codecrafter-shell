import sys
import os
import subprocess
import readline

BUILTINS = ["exit", "echo", "type", "pwd", "cd"]

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKSLASH = "\\"
SPACE = " "
NEWLINE = "\n"

def main():
    setup_readline()

    try:
        while True:
            full_command = tokenize(input("$ "))
            output = sys.stdout
            error = sys.stderr
            match full_command:
                case [*beginning, ("1>" | "1>>" | ">" | ">>") as redir_out, out_file, ("2>" | "2>>") as redir_err, error_file]:
                    output = open(out_file,'a') if redir_out.endswith(">>") else open(out_file,'w')
                    error = open(error_file,'a') if redir_err.endswith(">>") else open(error_file,'w')
                    full_command = beginning
                case [*beginning, ("1>" | "1>>" | ">" | ">>") as redir_out, out_file]:
                    output = open(out_file,'a') if redir_out.endswith(">>") else open(out_file,'w')
                    full_command = beginning
                case [*beginning, ("2>" | "2>>") as redir_err, error_file]:
                    error = open(error_file,'a') if redir_err.endswith(">>") else open(error_file,'w')
                    full_command = beginning
            match full_command:
                case ["exit", _]:
                    sys.exit(0)
                case ["echo", *rest]:
                    output.write(" ".join(rest)+"\n")
                case ["type", arg] if arg in BUILTINS:
                    output.write(f'{arg} is a shell builtin\n')
                case ["type", arg]:
                    executable = find_executable(arg)
                    if executable:
                        output.write(f'{arg} is {executable}\n')
                    else:
                        error.write(f'{arg}: not found\n')
                case ["pwd"]:
                    output.write(os.getcwd()+"\n")
                case ["cd", "~"]:
                    os.chdir(os.environ["HOME"])
                case ["cd", destination] if os.path.exists(destination):
                    os.chdir(destination)
                case ["cd", nonexistent_destination]:
                        error.write(f'cd: {nonexistent_destination}: No such file or directory\n')
                case [command, *args] if find_executable(command):
                    subprocess.run([command]+args, stdout=output, stderr=error)
                case _:
                    error.write(f'{" ".join(full_command)}: command not found\n')
    finally:
        output.close()
        error.close()

def tokenize(string):
    i = 0
    tokens = []
    separated = True
    while i < len(string):
        if string[i] == " ":
            i += 1
            separated = True
        elif string[i] == SINGLE_QUOTE:
            i += 1
            start = i
            while i < len(string) and string[i] != SINGLE_QUOTE:
                i += 1
            if separated:
                tokens.append(string[start:i])
            else:
                tokens[-1] += string[start:i]
            i += 1 # skip over the closing quote
            separated = False
        elif string[i] == DOUBLE_QUOTE:
            i += 1
            token = ""
            while i < len(string) and string[i] != DOUBLE_QUOTE:
                if string[i] == BACKSLASH and string[i+1] in ["$", BACKSLASH, DOUBLE_QUOTE]:
                    i += 1
                token += string[i]
                i += 1
            if separated:
                tokens.append(token)
            else:
                tokens[-1] += token
            i += 1 # skip over the closing quote
            separated = False
        else:
            token = ""
            while i < len(string) and string[i] not in [SPACE, SINGLE_QUOTE, DOUBLE_QUOTE]:
                if string[i] == BACKSLASH:
                    i += 1
                token += string[i]
                i += 1
            if separated:
                tokens.append(token)
            else:
                tokens[-1] += token
            separated = False
    return tokens

class Completer:
    completer = None

    def __init__(self):
        self.index = 0

    def complete(self, text):
        while self.index < len(BUILTINS):
            builtin_name = BUILTINS[self.index]
            self.index += 1
            if builtin_name.startswith(text):
                return builtin_name + " "

def completion(text, state):
    if state == 0:
        Completer.completer = Completer()
    return Completer.completer.complete(text)

def setup_readline():
    readline.set_completer(completion)
    if readline.backend == "editline":
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind('tab: complete')

def find_executable(name) -> None | str:
    for dir in os.environ["PATH"].split(":"):
        if not os.path.exists(dir):
            continue
        for executable in os.listdir(dir):
            if executable == name:
                return f'{dir}/{executable}'

if __name__ == "__main__":
    main()
