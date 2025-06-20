import readline
import asyncio
from app.parser import Parser
from app.readline import Readline

async def main():
    Readline.setup()
    while True:
        async with asyncio.TaskGroup() as tg:
            for command in Parser.parse(input("$ ")):
                await command.execute()
                command.close_io()
                tg.create_task(command.wait())

if __name__ == "__main__":
    asyncio.run(main())
