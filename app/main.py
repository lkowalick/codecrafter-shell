import sys


def main():
    while True:
        command = input("$ ").split()
        match command:
            case ["exit", status]:
                sys.exit(0)
            case _:
                print(f'{" ".join(command)}: command not found')

if __name__ == "__main__":
    main()
