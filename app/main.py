import sys
import os
import readline
from dataclasses import dataclass
import io
from typing import Literal, Optional
from functools import reduce
import asyncio

BUILTINS = ["exit", "echo", "type", "pwd", "cd", "GET_BACKEND"]

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKSLASH = "\\"
SPACE = " "
NEWLINE = "\n"


@dataclass
class Command:
    command: str
    piped_input: Optional[io.TextIOWrapper] = None
    output: io.TextIOWrapper = sys.stdout
    error: io.TextIOWrapper = sys.stderr

async def main():
    setup_readline()
    while True:
        full_commands, pipes = parse_output(tokenize_with_pipes(input("$ ")))
        processes = []
        for i, full_command in enumerate(full_commands):
            process = await execute_command(full_command)
            if i < len(full_commands) - 1:
                os.close(pipes[i][1])
            if i > 0:
                os.close(pipes[i-1][0])
            processes.append(process)
        async with asyncio.TaskGroup() as tg:
            for process in processes:
                tg.create_task(process.wait())


async def execute_command(full_command: Command) -> Optional[asyncio.subprocess.Process]:
    match full_command.command:
        case ["exit", _]:
            sys.exit(0)
        case ["echo", *rest]:
            full_command.output.write(" ".join(rest)+"\n")
        case ["type", arg] if arg in BUILTINS:
            full_command.output.write(f'{arg} is a shell builtin\n')
        case ["type", arg]:
            executable = find_executable(arg)
            if executable:
                full_command.output.write(f'{arg} is {executable}\n')
            else:
                full_command.error.write(f'{arg}: not found\n')
        case ["pwd"]:
            full_command.output.write(os.getcwd()+"\n")
        case ["GET_BACKEND"]:
            print(readline.backend)
        case ["cd", "~"]:
            os.chdir(os.environ["HOME"])
        case ["cd", destination] if os.path.exists(destination):
            os.chdir(destination)
        case ["cd", nonexistent_destination]:
            full_command.error.write(f'cd: {nonexistent_destination}: No such file or directory\n')
        case [command, *args] if find_executable(command):
            process = await asyncio.create_subprocess_exec(*([command]+args), stdin=full_command.piped_input, stdout=full_command.output, stderr=full_command.error)
            return process
        case _:
            full_command.error.write(f'{" ".join(full_command)}: command not found\n')

def tokenize_with_pipes(string):
    result = []
    for subcommand in string.split("|"):
        result.append(tokenize(subcommand))
    return result

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

    def __init__(self, text):
        self.completions = set()
        self.complete_builtins(text)
        self.complete_executables(text)

    def complete(self, state):
        if state >= len(self.completions):
            return None
        return list(self.completions)[state]+" "

    def complete_builtins(self, text):
        for builtin in BUILTINS:
            if builtin.startswith(text):
                self.completions.add(builtin)

    def complete_executables(self, text):
        for dir in os.environ["PATH"].split(":"):
            if not os.path.exists(dir):
                continue
            for executable in os.listdir(dir):
                if executable.startswith(text):
                    self.completions.add(executable)

def completion(text, state):
    if state == 0:
        Completer.completer = Completer(text)
    return Completer.completer.complete(state)

def completion_display(substitution, matches, longest_match_length):
    print("")
    print(" ".join(matches))
    print("$ " +readline.get_line_buffer(), end="")

def setup_readline():
    readline.set_completer(completion)
    if readline.backend == "editline":
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind('tab: complete')
        readline.set_completion_display_matches_hook(completion_display)

def find_executable(name) -> None | str:
    for dir in os.environ["PATH"].split(":"):
        if not os.path.exists(dir):
            continue
        for executable in os.listdir(dir):
            if executable == name:
                return f'{dir}/{executable}'

def wire_pipes(commands):
    full_commands = [None for _ in commands]
    pipes = [os.pipe() for _ in commands[:-1]]
    for i, command in enumerate(commands):
        pipe_input = None if i == 0 else pipes[i-1][0]
        output = pipes[i][1] if i < len(commands) - 1 else sys.stdout
        full_commands[i] = Command(command, pipe_input, output, sys.stderr)
    return full_commands, pipes

def parse_output(commands):
    if len(commands) > 1:
        return wire_pipes(commands)
    command = commands[0]
    output, error = None, None
    while ">" in "".join(command):
        match command:
            case [*beginning, ("1>" | "1>>" | ">" | ">>") as redir_out, out_file]:
                output = open(out_file,'a') if redir_out.endswith(">>") else open(out_file,'w')
                command = beginning
            case [*beginning, ("2>" | "2>>") as redir_err, error_file]:
                error = open(error_file,'a') if redir_err.endswith(">>") else open(error_file,'w')
                command = beginning
    if output is None:
        output = sys.stdout
    if error is None:
        error = sys.stderr
    return [Command(command, None, output, error)], []

if __name__ == "__main__":
    asyncio.run(main())
