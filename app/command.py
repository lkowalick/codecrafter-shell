from dataclasses import dataclass
import io
import os
import sys
from typing import Optional
import asyncio


@dataclass
class Command:
    BUILTINS = ["exit", "echo", "type", "pwd", "cd", "history", "GET_BACKEND"]

    command: str
    piped_input: Optional[io.TextIOWrapper] = None
    output: io.TextIOWrapper = sys.stdout
    error: io.TextIOWrapper = sys.stderr
    process: asyncio.subprocess.Process | None = None

    async def execute(self):
        output = self.output if hasattr(self.output, "write") else os.fdopen(self.output, "w")
        match self.command:
            case ["exit", _]:
                sys.exit(0)
            case ["echo", *rest]:
                output.write(" ".join(rest)+"\n")
            case ["type", arg] if arg in Command.BUILTINS:
                output.write(f'{arg} is a shell builtin\n')
            case ["type", arg]:
                executable = Command.find_executable(arg)
                if executable:
                    output.write(f'{arg} is {executable}\n')
                else:
                    self.error.write(f'{arg}: not found\n')
            case ["pwd"]:
                output.write(os.getcwd()+"\n")
            case ["GET_BACKEND"]:
                print(readline.backend)
            case ["cd", "~"]:
                os.chdir(os.environ["HOME"])
            case ["cd", destination] if os.path.exists(destination):
                os.chdir(destination)
            case ["cd", nonexistent_destination]:
                self.error.write(f'cd: {nonexistent_destination}: No such file or directory\n')
            case [command, *args] if Command.find_executable(command):
                self.process = await asyncio.create_subprocess_exec(*([command]+args), stdin=self.piped_input, stdout=self.output, stderr=self.error)
            case _:
                self.error.write(f'{" ".join(self.command)}: command not found\n')
    
    def find_executable(name) -> None | str:
        for dir in os.environ["PATH"].split(":"):
            if not os.path.exists(dir):
                continue
            for executable in os.listdir(dir):
                if executable == name:
                    return f'{dir}/{executable}'
                
    def close_io(self):
        Command.try_close_file(self.output)
        Command.try_close_file(self.piped_input)

    async def wait(self):
        if self.process:
            await self.process.wait()
    
    async def exec_and_wait(self):
        await self.execute()
        self.close_io()
        await self.wait()

    def try_close_file(fd_or_file):
        try:
            os.close(fd_or_file)
        except:
            pass