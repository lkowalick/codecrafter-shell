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
    try:
        while True:
            full_command = tokenize(input("$ "))
            output = sys.stdout
            match full_command:
                case [*beginning, ">", filename] | [*beginning, "1>", filename]:
                    output = open(filename,'w')
                    full_command = beginning
            match full_command:
                case ["exit", status]:
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
                        output.write(f'{arg}: not found\n')
                case ["pwd"]:
                    output.write(os.getcwd())
                case ["cd", "~"]:
                    os.chdir(os.environ["HOME"])
                case ["cd", destination] if os.path.exists(destination):
                    os.chdir(destination)
                case ["cd", nonexistent_destination]:
                        output.write(f'cd: {nonexistent_destination}: No such file or directory\n')
                case [command, *args] if find_executable(command):
                    subprocess.run([command]+args, stdout=output)
                case _:
                    output.write(f'{" ".join(full_command)}: command not found\n')
    finally:
        output.close()

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

def find_executable(name) -> None | str:
    for dir in os.environ["PATH"].split(":"):
        if not os.path.exists(dir):
            continue
        for executable in os.listdir(dir):
            if executable == name:
                return f'{dir}/{executable}'

if __name__ == "__main__":
    main()
