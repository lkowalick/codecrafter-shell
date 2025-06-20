import asyncio
from app.parser import Parser
from app.readline import Readline

async def main():
    Readline.setup()
    while True:
        async with asyncio.TaskGroup() as tg:
            for command in Parser.parse(input("$ ")):
                tg.create_task(command.exec_and_wait())

if __name__ == "__main__":
    asyncio.run(asyncio.gather(main()))
