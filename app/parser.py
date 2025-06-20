import os
import sys
from app.command import Command

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKSLASH = "\\"
SPACE = " "
NEWLINE = "\n"

class Parser:
    def parse(input_line):
        return Parser.parse_output(Parser.tokenize_with_pipes(input_line))

    def parse_output(commands):
        if len(commands) > 1:
            return Parser.wire_pipes(commands)
        command = commands[0]
        output, error = sys.stdout, sys.stderr
        while ">" in "".join(command):
            match command:
                case [*beginning, ("1>" | "1>>" | ">" | ">>") as redir_out, out_file]:
                    output = open(out_file,'a') if redir_out.endswith(">>") else open(out_file,'w')
                    command = beginning
                case [*beginning, ("2>" | "2>>") as redir_err, error_file]:
                    error = open(error_file,'a') if redir_err.endswith(">>") else open(error_file,'w')
                    command = beginning
        return [Command(command, None, output, error)]


    def wire_pipes(commands):
        full_commands = [None for _ in commands]
        pipes = [os.pipe() for _ in commands[:-1]]
        for i, command in enumerate(commands):
            pipe_input = None if i == 0 else pipes[i-1][0]
            output = pipes[i][1] if i < len(commands) - 1 else sys.stdout
            full_commands[i] = Command(command, pipe_input, output, sys.stderr)
        return full_commands

    def tokenize_with_pipes(string):
        result = []
        for subcommand in string.split("|"):
            result.append(Parser.tokenize(subcommand))
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
