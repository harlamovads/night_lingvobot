import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from TeamMember import TeamMember
import sqlite3
import pandas as pd


class Form(StatesGroup):
    register = State()
    login = State()
    submit = State()
    help = State()


logging.basicConfig(level=logging.INFO)

bot = Bot(token="")
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Чтобы зарегистировать команду, введите /register, чтобы продолжить участие, введите /login")


# Регистрация

@dp.message(Command("register"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.register)
    await message.reply('Введите имя вашей команды')


@dp.message(Form.register)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    global player
    player = TeamMember(message.text)
    print(player.name)
    await message.reply(f'Ура, команда {message.text} зарегистрирована!')
    await message.answer(f'Ваш текущий счет - {player.point_getter()} очков!')
    await message.answer('Высылаю текст задачи: *sample text*, нажмите /solve, чтобы сдать решение!\n '
                         'Чтобы получить подсказку, нажмите /hint')
    await state.set_state(Form.submit)


# Решения
@dp.message(Command("solve"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.submit)
    await message.answer('Присылайте решение, перед ответом напишите, '
                         'пожалуйста, номер задачи, отделив его от решения пробелом')


@dp.message(Form.submit)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    task = message.text.split()[0]
    answer = message.text
    await message.answer(player.answer_check(task, answer))
    await message.answer(f'Ваш текущий счет - {player.point_getter()} очков!')


@dp.message(Command("hint"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.help)
    await message.answer('Хотите подсказочку? Пришлите номер задачи, но это будет стоить вам баллов...')


@dp.message(Form.help)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    task = message.text
    await message.answer(player.get_some_help(task))
    await message.answer('Надеюсь, помогло! Для решения нажмите /solve')
    await state.set_state(Form.submit)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
