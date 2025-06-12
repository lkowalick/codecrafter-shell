import sys
import os

COMMANDS = ["exit", "echo", "type"]

def main():
    while True:
        command = input("$ ").split()
        match command:
            case ["exit", status]:
                sys.exit(0)
            case ["echo", *rest]:
                print(" ".join(rest))
            case ["type", arg]:
                if arg in COMMANDS:
                    print(f'{arg} is a shell builtin')
                else:
                    found = False
                    for dir in os.environ["PATH"].split(":"):
                        if not os.path.exists(dir):
                            continue
                        for executable in os.listdir(dir):
                            if executable == arg:
                                print(f'{arg} is {dir}/{executable}')
                                found = True
                    if not found:
                        print(f'{arg}: not found')
            case _:
                print(f'{" ".join(command)}: command not found')

if __name__ == "__main__":
    main()
