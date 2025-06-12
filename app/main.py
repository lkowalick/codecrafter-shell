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
                        for executable in os.listdir(dir):
                            if os.path.basename(executable) == arg:
                                print(f'{arg} is {executable}')
                                found = True
                    if not found:
                        print(f'{arg}: not found')
            case _:
                print(f'{" ".join(command)}: command not found')

if __name__ == "__main__":
    main()
