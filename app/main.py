import sys
import os
import subprocess

BUILTINS = ["exit", "echo", "type", "pwd", "cd"]

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKSLASH = "\\"
SPACE = " "
NEWLINE = "\n"

def main():
    while True:
        full_command = tokenize(input("$ "))
        match full_command:
            case ["exit", status]:
                sys.exit(0)
            case ["echo", *rest]:
                print(" ".join(rest))
            case ["type", arg]:
                if arg in BUILTINS:
                    print(f'{arg} is a shell builtin')
                else:
                    executable = find_executable(arg)
                    if executable:
                        print(f'{arg} is {executable}')
                    else:
                        print(f'{arg}: not found')
            case ["pwd"]:
                print(os.getcwd())
            case ["cd", destination]:
                if destination == "~":
                    os.chdir(os.environ["HOME"])
                elif os.path.exists(destination):
                    os.chdir(destination)
                else:
                    print(f'cd: {destination}: No such file or directory')
            case [command, *args]:
                if find_executable(command):
                    subprocess.run([command]+args)
                else:
                    print(f'{command}: command not found')
            case _:
                print(f'{" ".join(full_command)}: command not found')

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
                if string[i] == BACKSLASH:
                    if string[i+1] == "n":
                        string[i+1] == "\n"
                    else:
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

def find_executable(name) -> None | str:
    for dir in os.environ["PATH"].split(":"):
        if not os.path.exists(dir):
            continue
        for executable in os.listdir(dir):
            if executable == name:
                return f'{dir}/{executable}'

if __name__ == "__main__":
    main()
