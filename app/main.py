import sys

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
                    print(f'{arg}: command not found')
            case _:
                print(f'{" ".join(command)}: command not found')

if __name__ == "__main__":
    main()
