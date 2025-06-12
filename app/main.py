import sys


def main():
    while True:
        command_str = input("$ ")
        match command_str.split():
            case ["exit", status]:
                sys.exit(0)
            case ["echo", *rest]:
                sys.stdout(" ".join(rest))
            case _:
                print(f'{" ".join(command_str)}: command not found')

if __name__ == "__main__":
    main()
