import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from TeamMember import TeamMember
from time import strftime
import json

with open('protodatabase.json', 'r') as f:
    protodb = json.load(f)

print(protodb)
user_sessions = {}


class Form(StatesGroup):
    register = State()
    login = State()
    submit = State()
    help = State()
    neutral = State()
    broadcast = State()


logging.basicConfig(level=logging.INFO)

bot = Bot(token="")
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)


def get_keyboard():
    buttons = [[
        types.InlineKeyboardButton(text="M202", callback_data="num_M202"),
        types.InlineKeyboardButton(text="M302", callback_data="num_M302"),
        types.InlineKeyboardButton(text="M303", callback_data="num_M303")],
        [types.InlineKeyboardButton(text="S103", callback_data="num_S103"),
        types.InlineKeyboardButton(text="S202", callback_data="num_S202"),
        types.InlineKeyboardButton(text="R110", callback_data="num_R110")],
        [types.InlineKeyboardButton(text="R207", callback_data="num_R207"),
        types.InlineKeyboardButton(text="R201", callback_data="num_R201"),
        types.InlineKeyboardButton(text="N206", callback_data="num_N206"),
        types.InlineKeyboardButton(text="N204", callback_data="num_N204")]]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    user_sessions[user_id] = {}
    await message.answer("Чтобы зарегистрировать команду, введите /register, чтобы продолжить участие, введите /login")


@dp.message(Command("register"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    session = user_sessions.get(user_id)
    user_sessions[user_id] = session
    await state.set_state(Form.register)
    await message.reply('Введите название команды и юзернеймы участников в столбец \n\n Пример:\n Несогласные\n @biba\n @boba')


@dp.message(Command("login"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    session = user_sessions.get(user_id)
    user_sessions[user_id] = session
    await state.set_state(Form.login)
    await message.reply('Введите имя вашей команды')


@dp.message(Form.register)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = str(message.from_user.id)
    try:
        u_name = message.text.split('\n')[0]
        team_comp = message.text.split()[1:]
    except:
        await message.reply('Видимо, что-то не так с форматированием: отправьте, пожалуйста, данные еще раз!')
    if user_id in protodb.keys():
        await message.reply(f'Простите, вы уже зарегистрированы на участие(( \n'
                            f'Если по каким-то причинам хотите перерегистрироваться, свяжитесь с организатором: @saemari \n'
                            f'Если вы попали сюда в результате технической ошибки, свяжитесь с тех. специалистом: @zlovoblachko')
    else:
        protodb[user_id] = {'username': u_name, 'team_comp': team_comp, 'score': 0, 'solved': [], 'available_help': [],
                            'task': 0}
        with open('protodatabase.json', 'w') as f:
            f.write(json.dumps(protodb, indent=2))
        player = TeamMember(message.text)
        await message.reply(f'Ура, команда {u_name} зарегистрирована!\n'
                            f'Ваш текущий счет - {player.point_getter()} очков!')
        await message.reply('Чтобы начать решать задачи, пришлите в чат что угодно!')
        with open('logging.txt', 'a') as log:
            log.write(f'Команда {player.name} зарегистрировалась в {strftime("%d, %b, %H:%M:%S")}\n')
        await state.set_state(Form.neutral)


@dp.message(Form.login)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = str(message.from_user.id)
    if user_id in protodb:
        player = TeamMember(protodb[user_id]['username'],
                            protodb[user_id]['score'],
                            protodb[user_id]['solved'],
                            protodb[user_id]['available_help'])
        await message.reply(f'Добро пожаловать обратно!'
                            f'Вы уже поймали {player.point_getter()} гласных - остальные ждут!')
        await state.set_state(Form.neutral)
    else:
        await message.reply(f'Вы не зарегистрированы - зарегистрируйтесь, пожалуйста!')
        await message.reply('Введите название команды и юзернеймы участников в столбец \n\n Пример:\n Несогласные\n @biba\n @boba')
        await state.set_state(Form.register)


@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
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
    user_id = str(message.from_user.id)
    player = TeamMember(protodb[user_id]['username'],
                        protodb[user_id]['score'],
                        protodb[user_id]['solved'],
                        protodb[user_id]['available_help'])
    task = protodb[user_id]['task']
    answer = message.text.lower()
    await message.answer(player.answer_check(task, answer))
    protodb[user_id]['score'] = player.point_getter()
    protodb[user_id]['solved'] = player.solved
    with open('protodatabase.json', 'w') as f:
        f.write(json.dumps(protodb, indent=2))
    await state.set_state(Form.neutral)
    await message.answer('Чтобы вернуться в меню, нажмите /back')


@dp.message(Command("hint"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = str(message.from_user.id)
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
        await message.answer(f'Для получения подсказки вам придётся потерять 2 гласных.'
                             f'На данный момент вы собрали {player.point_getter()} гласных\n'
                             f'Если вы всё еще хотите брать подсказку, отправьте "Да" \n'
                             f'Если вы передумали, пришлите /solve, чтобы отправить решение, или /back, чтобы'
                             f'перейти к другой локации!')


@dp.message(Command("score"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = str(message.from_user.id)
    player = TeamMember(protodb[user_id]['username'],
                        protodb[user_id]['score'],
                        protodb[user_id]['solved'],
                        protodb[user_id]['available_help'])
    await message.answer(f'Вы собрали {player.point_getter()} гласных\n')


@dp.message(Form.help)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    user_id = str(message.from_user.id)
    player = TeamMember(protodb[user_id]['username'],
                        protodb[user_id]['score'],
                        protodb[user_id]['solved'],
                        protodb[user_id]['available_help'])
    task = protodb[user_id]['task']
    await message.answer(player.get_some_help(task))
    protodb[user_id]['available_help'] = player.available_help
    protodb[user_id]['score'] = player.point_getter()
    with open('protodatabase.json', 'w') as f:
        f.write(json.dumps(protodb, indent=2))
    await message.answer('Надеемся, помогло! Для решения нажмите /solve')


@dp.message(Form.neutral)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Выберите локацию",
        reply_markup=get_keyboard()
    )


@dp.message(Command("broadcast"))
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    if message.from_user.id == 1658604792:
        await state.set_state(Form.broadcast)
    else:
        await message.answer('ой, не та кнопка! отправьте что угодно, чтобы снова перейти к задачкам')


@dp.message(Form.broadcast)
async def cmd_reply(message: types.Message, state: FSMContext) -> None:
    for id in protodb.keys():
        try:
            await bot.send_message(id, message.text)
        except:
            with open('logging.txt', 'a') as log:
                log.write(f'Пользователь {id} не получил сообщение-броадкаст\n')


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
