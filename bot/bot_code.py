import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from TeamMember import TeamMember
from keys import help_worth
from time import strftime
import json

with open('protodatabase.json', 'r') as f:
    print(f.read() == "")
    if f.read() == "":
        protodb = {}
    else:
        protodb = json.load(f)

print(protodb)
user_sessions = {}


class Form(StatesGroup):
    register = State()
    login = State()
    submit = State()
    help = State()
    neutral = State()


logging.basicConfig(level=logging.INFO)

bot = Bot(token="6346530233:AAEXtH8RnDhxmHwIsLI3cog_5vMClPo1BGU")
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)


def get_keyboard():
    buttons = [[
        types.InlineKeyboardButton(text="Лока А", callback_data="num_1"),
        types.InlineKeyboardButton(text="Лока Б", callback_data="num_2"),
        types.InlineKeyboardButton(text="Лока В", callback_data="num_3")]]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_sessions[user_id] = {}
    await message.answer("Чтобы зарегистрировать команду, введите /register, чтобы продолжить участие, введите /login")


@dp.message(Command("register"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    session = user_sessions.get(user_id)
    user_sessions[user_id] = session
    await state.set_state(Form.register)
    await message.reply('Введите имя вашей команды и телеграмовские юзернеймы участников (считая ваш) в одну строку \n'
                        'Юзернеймы - это то, что начинается с @')


@dp.message(Command("login"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    session = user_sessions.get(user_id)
    user_sessions[user_id] = session
    await state.set_state(Form.login)
    await message.reply('Введите имя вашей команды')


@dp.message(Form.register)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    u_name = message.text.split()[0]
    team_comp = message.text.split()[1:]
    if user_id in protodb.keys():
        await message.reply(f'Простите, вы уже зарегистрированы на участие(( \n'
                            f'Если по каким-то причинам хотите перерегистрироваться, свяжитесь с организатором: @saemari \n'
                            f'Если вы попали сюда в результате технической ошибки, свяжитесь с тех. специалистом: @zlovoblachko')
    else:
        protodb[user_id] = {'username': u_name, 'team_comp': team_comp, 'score': 0, 'solved': [], 'available_help': [], 'task': 0}
        with open('protodatabase.json', 'w') as f:
            f.write(json.dumps(protodb, indent = 2))
        player = TeamMember(message.text)
        await message.reply(f'Ура, команда {u_name} зарегистрирована!\n'
                            f'Ваш текущий счет - {player.point_getter()} очков!')
        await message.reply('Чтобы начать решать задачи, пришлите в чат что угодно!')
        with open('logging.txt', 'a') as log:
            log.write(f'Команда {player.name} зарегистрировалась в {strftime("%d, %b, %H:%M:%S")}\n')
        await state.set_state(Form.neutral)


@dp.message(Form.login)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    if message.text in protodb:
        user_id = message.from_user.id
        player = TeamMember(protodb[user_id]['username'],
                            protodb[user_id]['score'],
                            protodb[user_id]['solved'],
                            protodb[user_id]['available_help'])
        await message.reply(f'Добро пожаловать обратно!'
                            f'Ваш счет - {player.point_getter()}')


@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    protodb[user_id]['task'] = callback.data.split("_")[1]
    task = callback.data.split("_")[1]
    await callback.message.answer(f'Вы в локации {task}! Что вы хотите сделать? \n'
                                  f'Чтобы отправить решение, нажмите /solve \n'
                                  f'Чтобы получить подсказку, нажмите /hint \n'
                                  f'Чтобы посмотреть свой текущий счет, введите /score \n'
                                  f'Чтобы вернуться назад, нажмите /back')
    await callback.answer()


@dp.message(Command("back"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await message.answer(
            "Выберите локацию",
            reply_markup=get_keyboard())
    await state.set_state(Form.neutral)


@dp.message(Command("solve"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.submit)
    await message.answer(f'Присылайте ваше решение!')


@dp.message(Form.submit)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    player = TeamMember(protodb[user_id]['username'],
                        protodb[user_id]['score'],
                        protodb[user_id]['solved'],
                        protodb[user_id]['available_help'])
    task = protodb[user_id]['task']
    answer = message.text.lower()
    await message.answer(player.answer_check(task, answer))
    protodb[user_id]['score'] = player.point_getter()
    protodb[user_id]['solved'].append(task)
    with open('protodatabase.json', 'w') as f:
        f.write(json.dumps(protodb, indent = 2))
    await state.set_state(Form.neutral)
    await message.answer('Чтобы вернуться в меню, нажмите /back')


@dp.message(Command("hint"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    player = TeamMember(protodb[user_id]['username'],
                        protodb[user_id]['score'],
                        protodb[user_id]['solved'],
                        protodb[user_id]['available_help'])
    task = protodb[user_id]['task']
    await state.set_state(Form.help)
    if task in player.available_help:
        await message.answer('Вот ваша подсказка:')
        await message.answer(player.get_some_help(task))
    elif task not in player.available_help:
        await message.answer(f'Хотите подсказочку? \n'
                             f'Для этого пункта подсказка стоит {help_worth[task]} очков. \n'
                             f'У вас на счете - {player.point_getter()}\n'
                             f'Обратите внимание, что после получения подсказки вы получите на 1 балл'
                             f'меньше за решение задачи!\n'
                             f'Если вы всё еще хотите брать подсказку, отправьте "Да" \n'
                             f'Если вы передумали, пришлите /solve, чтобы отправить решение, или /back, чтобы'
                             f'перейти к другой локации!')


@dp.message(Command("score"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    player = TeamMember(protodb[user_id]['username'],
                        protodb[user_id]['score'],
                        protodb[user_id]['solved'],
                        protodb[user_id]['available_help'])
    await message.answer(f'У вас на счете - {player.point_getter()} очков\n')


@dp.message(Form.help)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    player = TeamMember(protodb[user_id]['username'],
                        protodb[user_id]['score'],
                        protodb[user_id]['solved'],
                        protodb[user_id]['available_help'])
    task = protodb[user_id]['task']
    await message.answer(player.get_some_help(task))
    protodb[user_id]['available_help'] = player.available_help
    protodb[user_id]['score'] = player.point_getter()
    with open('protodatabase.json', 'w') as f:
        f.write(json.dumps(protodb, indent = 2))
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
