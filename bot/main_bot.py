import aiogram
import logging
import asyncio
import sys
import redis
from aiogram.filters import command
from redis_update import Updater
import os
import dotenv

# global vars
dotenv.load_dotenv("../.env")
upd = Updater()
TOKEN: str = os.getenv("BOT_API")
CMD: list = ['exchange', 'rates']
bot: aiogram.Bot = aiogram.Bot(token=TOKEN)
dp: aiogram.Dispatcher = aiogram.Dispatcher(bot=bot)

# auto update redis coroutine
async def auto_update() -> None:
    while True:
        upd.update()
        await asyncio.sleep(24 * 3600)

# start command
@dp.message(aiogram.filters.CommandStart())
async def start(message: aiogram.types.Message) -> None:
    await message.answer("This bot simply converts some currency to other one.\n" +
                         "/exchange cur_from cur_to amount - Converts cur_from to cur_to\n" +
                         "/rates - Show all currency courses in RUB")

# exchange command
@dp.message(aiogram.filters.Command(CMD[0]))
async def exchange(message: aiogram.types.Message, command: command.CommandObject):
    redis_cli = redis.Redis(host="redis", port=6379)
    cargs = command.args.split(" ")
    print(cargs)
    cur_from = cargs[0].lower()
    cur_to = cargs[1].lower()
    rate = (float(redis_cli.get("{}".format(cur_from)).decode("utf-8").replace(",", ".")) /
            float(redis_cli.get("{}".format(cur_to)).decode("utf-8").replace(",", ".")))
    amount = float(cargs[-1])
    val = amount * rate
    redis_cli.close()
    await message.answer(f"{amount} {cur_from.upper()} is {val} {cur_to.upper()}")

# rates command
@dp.message(aiogram.filters.Command(CMD[1]))
async def rates(message: aiogram.types.Message):
    redis_cli = redis.Redis(host="redis", port=6379)
    answer = ''
    for key in redis_cli.keys("*"):
        answer += f"1 {key.decode("utf-8")} -> {redis_cli.get(key).decode("utf-8")} RUB \n"
    redis_cli.close()
    await message.answer(answer)

# creating polling coroutine
async def poll() -> None:
    await dp.start_polling(bot)


async def main() -> None:
    await asyncio.gather(poll(), auto_update())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
