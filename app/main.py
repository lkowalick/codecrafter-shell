import sys
import os
import subprocess

BUILTINS = ["exit", "echo", "type", "pwd", "cd"]

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
        elif string[i] == "'":
            i += 1
            start = i
            while i < len(string) and string[i] != "'":
                i += 1
            if separated:
                tokens.append(string[start:i])
            else:
                tokens[-1] += string[start:i]
            separated = False
        else:
            start = i
            i += 1
            while i < len(string) and string[i] != " " and string[i] != "'":
                i += 1
            if separated:
                tokens.append(string[start:i])
            else:
                tokens[-1] += string[start:i]
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
