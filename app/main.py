import readline
import asyncio
from app.parser import Parser
from app.completer import Completer

async def main():
    setup_readline()
    while True:
        async with asyncio.TaskGroup() as tg:
            for command in Parser.parse(input("$ ")):
                await command.execute()
                command.close_io()
                tg.create_task(command.wait())

def setup_readline():
    readline.set_completer(Completer.completion)
    if readline.backend == "editline":
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind('tab: complete')
        readline.set_completion_display_matches_hook(Completer.completion_display)

if __name__ == "__main__":
    asyncio.run(main())
