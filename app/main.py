import sys
import os
import subprocess

BUILTINS = ["exit", "echo", "type", "pwd"]

def main():
    while True:
        full_command = input("$ ").split()
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
            case [command, *args]:
                if find_executable(command):
                    subprocess.run([command]+args)
                else:
                    print(f'{command}: command not found')
            case _:
                print(f'{" ".join(full_command)}: command not found')

def find_executable(name) -> None | str:
    for dir in os.environ["PATH"].split(":"):
        if not os.path.exists(dir):
            continue
        for executable in os.listdir(dir):
            if executable == name:
                return f'{dir}/{executable}'

if __name__ == "__main__":
    main()
