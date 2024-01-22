import asyncio
import logging
from random import randint
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from TeamMember import TeamMember
from keys import help_worth
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sqlite3
import pandas as pd


class Form(StatesGroup):
    register = State()
    login = State()
    submit = State()
    help = State()
    neutral = State()


logging.basicConfig(level=logging.INFO)

bot = Bot(token="6346530233:AAEXtH8RnDhxmHwIsLI3cog_5vMClPo1BGU")
dp = Dispatcher()


def get_keyboard():
    buttons = [[
        types.InlineKeyboardButton(text="Лока А", callback_data="num_1"),
        types.InlineKeyboardButton(text="Лока Б", callback_data="num_2"),
        types.InlineKeyboardButton(text="Лока В", callback_data="num_3")]]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Чтобы зарегистрировать команду, введите /register, чтобы продолжить участие, введите /login")


# Регистрация

@dp.message(Command("register"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.register)
    await message.reply('Введите имя вашей команды')


@dp.message(Form.register)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    global player
    player = TeamMember(message.text)
    await message.reply(f'Ура, команда {message.text} зарегистрирована!\n'
                        f'Ваш текущий счет - {player.point_getter()} очков!')
    await state.set_state(Form.neutral)


@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    print('thing')
    global task
    task = callback.data.split("_")[1]
    await callback.message.answer(f'Вы в локации {task}! Что вы хотите сделать? \n'
                                  f'Чтобы отправить решение, нажмите /solve \n'
                                  f'Чтобы получить подсказку, нажмите /hint')
    await callback.answer()


@dp.message(Command("back"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    print('back')
    await state.set_state(Form.neutral)


@dp.message(Command("solve"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.submit)
    await message.answer(f'Присылайте ваше решение!')


@dp.message(Form.submit)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    answer = message.text
    await message.answer(player.answer_check(task, answer))
    await message.answer('Чтобы вернуться в меню, нажмите /back')


@dp.message(Command("hint"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.help)
    if task in player.available_help:
        await message.answer('Вот ваша подсказка:')
    elif task not in player.available_help:
        await message.answer(f'Хотите подсказочку? \n'
                             f'Для этого пункта подсказка стоит {help_worth[task]} очков. \n'
                             f'У вас на счете - {player.point_getter()}\n'
                             f'Обратите внимание, что после получения подсказки вы получите на 1 балл'
                             f'меньше за решение задачи!\n'
                             f'Если вы всё еще хотите брать подсказку, отправьте "Да"')


@dp.message(Form.help)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await message.answer(player.get_some_help(task))
    await message.answer('Надеюсь, помогло! Для решения нажмите /solve')


@dp.message(Form.neutral)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Выберите локацию",
        reply_markup=get_keyboard()
    )
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
