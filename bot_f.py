from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from parser_f import parse_url
import json , re, logging, time, asyncio


logging.basicConfig(level=logging.INFO)
API_TOKEN = ''
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class SaveURL(StatesGroup):
    url_one = State()
    delete_urls= State()

database={}

def update_database():
    with open("database.json", "w", encoding="utf-8") as file:
        user_data = database.values()
        json_data = [json.dumps(data, ensure_ascii=False) + '\n' for data in user_data]
        file.write('\n'.join(json_data))

def read_database():
    try:
        with open("database.json", "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    user_id = entry["id"]
                    database[user_id] = entry
    except FileNotFoundError:
        # Если файл не найден, создаем пустую базу данных
        with open("database.json", "w", encoding="utf-8") as file:
            file.write("")
        database.clear()

read_database()



@dp.message(CommandStart())
async def send_welcome(message: Message):
    user_id=str(message.from_user.id)
    if user_id not in database:
        database[user_id] = {"id": user_id, "data": []}
        update_database()

    kb = [
        [
            types.KeyboardButton(text="Вывести cписок ваших ссылок"),
            types.KeyboardButton(text="Отправить ссылку")
        ],
    ]
    stb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(f"Привет, выбери действие ", reply_markup=stb)


@dp.message(lambda message: message.text == 'Отправить ссылку')
async def get_url(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user_id not in database:
        database[user_id] = {"id": user_id, "data": []}
        update_database()

    await message.answer(f"Отправьте ссылку на товар с Wildberries")
    await state.set_state(SaveURL.url_one)

@dp.message(SaveURL.url_one)
async def check_url(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    url_re1 = re.match('https://www.wildberries.ru/catalog/[\d]', message.text)
    url_re2 = re.match('https://wildberries.ru/catalog/[\d]', message.text)
    if url_re1 is None and url_re2 is None:
        await message.answer(f'Вы не отправили ссылку на товар Wildberries')
    else:
        wait_mes = await message.answer("Ожидайте")
        await state.update_data(url=message.text)
        data = await state.get_data()
        url = data['url']
        res = await parse_url(url)
        await bot.delete_message(chat_id=wait_mes.chat.id, message_id=wait_mes.message_id)

        if res:
            await message.answer(f"Название: {res['Название']}\nСсылка: {message.text}\nЦена без скидки: {res['Цена без скидки']}\nЦена со скидкой: {res['Цена']}\nСкидка: {res['Скидка']}\nАртикул: {res['Артикул']}")
        else:
            await message.answer("Не удалось получить данные")
        kb = [
            [
                types.KeyboardButton(text="Вывести cписок ваших ссылок"),
                types.KeyboardButton(text="Отправить ссылку", )
            ],
        ]
        stb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        result = {
            'url': message.text ,
            'Название': res['Название'],
            'Цена': res['Цена'],
            'Цена без скидки': res['Цена без скидки'],
            'Артикул': res['Артикул'],
            'Скидка': res['Скидка']
        }
        if result['url'] not in database[user_id]['data'] and result['Артикул'] not in [item['Артикул'] for item in database[user_id]['data']]:
            database[user_id]['data'].append(result)
            update_database()
            await message.answer(f"Ссылка добавлена в ваш список", reply_markup=stb)
        else:
            await message.answer("Ссылка уже добавлена в ваш список")



def display_urls(user_id):
    output = ""
    if user_id in database and 'data' in database[user_id] and len(database[user_id]['data']) > 0:
        for i, entry in enumerate(database[user_id]['data']):
            url = entry['url']
            name= entry['Название']
            output += f"{i + 1}.{name} {url}\n"
    else:
        output = "У вас нет ссылок в списке."
    return output

@dp.message(lambda message: message.text == 'Вывести cписок ваших ссылок')
async def process_commands(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    kb = [
        [
            types.KeyboardButton(text="Удалить ссылку"),
            types.KeyboardButton(text="Отправить ссылку")
        ],
    ]
    butt = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    urls = display_urls(user_id)
    await message.answer(f"Ваши ссылки:\n{urls}", reply_markup=butt)

@dp.message(lambda message: message.text == 'Удалить ссылку')
async def process_commands(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    urls = display_urls(user_id)
    kb = [
        [
            types.KeyboardButton(text="Отправить ссылку")
        ],
    ]
    butt = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    if user_id in database and 'data' in database[user_id] and len(database[user_id]['data']) > 0:
        await message.answer(f"Введите номер ссылки, которую желаете удалить.")
        await state.set_state(SaveURL.delete_urls)
    else:
        await message.answer(f"У вас нет ссылок в списке.\nДавайте это исправим. Нажмите кнопку", reply_markup=butt)

    @dp.message(SaveURL.delete_urls)
    async def delete_urls(message: Message, state: FSMContext):
        user_id = str(message.from_user.id)
        try:
            index = int(message.text) - 1
            if 0 <= index < len(database[user_id]['data']):
                del database[user_id]['data'][index]
                update_database()
                urls = display_urls(user_id)
                await message.answer(f"Ссылка удалена из вашего списка.\n Ваши ссылки: \n {urls} ")
            else:
                await message.answer("Неверный номер ссылки")
        except ValueError:
            await message.answer("Введите корректный номер ссылки")


async def periodic_parse_results():
    while True:
        for user_id in database.keys():
            if len(database[user_id]['data']) > 0:
                for i in database[user_id]['data']:
                    if 'url' not in i:
                        continue
                    url_parse = i['url']
                    sale = i['Скидка']
                    res = await parse_url(url_parse)
                    if res is None:
                        continue
                    sale_res = res['Скидка']
                    if sale_res > sale and i['Цена без скидки'] == res['Цена без скидки'] and i['Цена']!= res['Цена']:
                        await bot.send_message(user_id, f"Скидка на товар увеличилась.\n{url_parse}")
                        i['Цена'] =res['Цена']
                        i['Скидка'] = sale_res
                        update_database()
                    elif sale_res > sale and i['Цена без скидки'] != res['Цена без скидки']:
                        final_price_1 = float(i['Цена'].text.replace(" ", "").replace("₽", ""))
                        final_price_2 = float(res['Цена'].text.replace(" ", "").replace("₽", ""))
                        i['Цена без скидки'] = res['Цена без скидки']
                        i['Скидка'] = sale_res
                        update_database()
                        if final_price_1< final_price_2:
                            await bot.send_message(user_id, f"Скидка на товар увеличилась.\n{url_parse}")
                    elif sale_res == sale and i['Цена без скидки'] != res['Цена без скидки'] and i['Цена']!= res['Цена']:
                        i['Цена без скидки'] = res['Цена без скидки']
                        i['Цена'] = res['Цена']
                        old_price_1= float(i['Цена без скидки'].text.replace(" ", "").replace("₽", ""))
                        old_price_2 = float(res['Цена без скидки'].text.replace(" ", "").replace("₽", ""))
                        final_price_1 = float(i['Цена'].text.replace(" ", "").replace("₽", ""))
                        final_price_2 = float(res['Цена'].text.replace(" ", "").replace("₽", ""))
                        if old_price_1 < old_price_2 and final_price_1 < final_price_2:
                            await bot.send_message(user_id, f"Цена уменьшилась .\n{url_parse}")
                        update_database()
                    else:
                        continue

        await asyncio.sleep(60)



async def start():
    task = asyncio.create_task(periodic_parse_results())
    await dp.start_polling(bot)
    await task

