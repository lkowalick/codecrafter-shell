import readline
import asyncio
from app.parser import Parser
from app.completer import Completer

async def main():
    setup_readline()
    while True:
        async with asyncio.TaskGroup() as tg:
            for full_command in Parser.parse(input("$ ")):
                process = await full_command.execute()
                if hasattr(process, "wait"):
                    tg.create_task(process.wait())

def setup_readline():
    readline.set_completer(Completer.completion)
    if readline.backend == "editline":
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind('tab: complete')
        readline.set_completion_display_matches_hook(Completer.completion_display)

if __name__ == "__main__":
    asyncio.run(main())
