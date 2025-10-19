
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from datetime import datetime, timedelta

# Ініціалізація
API_TOKEN = 'YOUR_BOT_TOKEN'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Стани для FSM
class UserStates(StatesGroup):
    start = State()
    tutorial_sent = State()
    after_tutorial = State()
    name_input = State()
    experience_select = State()
    pain_points_select = State()
    goal_select = State()
    ready_to_pay = State()


# База даних (для прикладу — словник, в проді використовуй PostgreSQL)
user_data = {}


# БЛОК 1: Привітання
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data[user_id] = {
        "timestamp_start": datetime.now(),
        "stage": "start"
    }
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Давай інфу 🔥", callback_data="get_info")],
        [types.InlineKeyboardButton(text="Та шо там у тебе?", callback_data="whats_inside")]
    ])
    
    # Відправка мему (замість зображення використовуємо URL)
    await message.answer_photo(
        photo="https://your-server.com/memes/welcome.jpg",  # Замінити на реальний URL
        caption=(
            "Шо, бро, знову на інфоциганів натрапив? 😏\n"
            "Розслабся, тут без гівна.\n\n"
            "Я так само колись починав — без знань, без системи, просто вірив у меми про \"туземун\" 🚀\n\n"
            "Коротше, свій чувак у крипті.\n"
            "Тут усе чесно, без водички — чисто практика, альфа і трохи фану 😎\n\n"
            "Готовий зловити щось, що реально працює, а не чергову \"мотиваційну байку\"?"
        ),
        reply_markup=keyboard
    )
    
    await state.set_state(UserStates.start)


# Обробка кнопок БЛОК 1
@dp.callback_query(F.data.in_(["get_info", "whats_inside"]))
async def process_block1(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    user_data[user_id]["button_clicked"] = callback.data
    
    # Чекаємо 2 хвилини перед наступним повідомленням
    await asyncio.sleep(120)  # 120 секунд = 2 хвилини
    
    # БЛОК 2: Туторіал
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Давай туторіал 🎬", callback_data="get_tutorial")]
    ])
    
    await callback.message.answer(
        "Та не парся, не буде лекцій і нудятини 😴\n\n"
        "Для тебе підготував короткий туторіал із реально корисною інфою — без води, без фігні, все як ти любиш 💪\n\n"
        "Хочеш розібратись, як зібрати свій крипто-портфель і не злити депозит після першої червоної свічки?\n\n"
        "Тут усе по-людському:\n"
        "✅ 10 хвилин чистої альфи\n"
        "✅ Нічого зайвого\n"
        "✅ Після — вже будеш на голову вищим за 80% новачків\n\n"
        "Летимо? 👇",
        reply_markup=keyboard
    )
    
    await state.set_state(UserStates.tutorial_sent)


# БЛОК 2: Відправка туторіалу
@dp.callback_query(F.data == "get_tutorial")
async def send_tutorial(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    user_data[user_id]["tutorial_sent"] = datetime.now()
    
    await callback.message.answer(
        "Ось твій туторіал, бро! 👇\n\n"
        "https://youtube.com/your-tutorial-link\n\n"  # Замінити на реальний лінк
        "Дивись спокійно, після напишу 😉"
    )
    
    # Чекаємо 10-15 хвилин
    await asyncio.sleep(900)  # 15 хвилин
    
    # БЛОК 3: Після туторіалу
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Покажи, шо там", callback_data="show_inside")]
    ])
    
    await callback.message.answer(
        "Зацінив, бро? 👀\n"
        "Це лише початок 😉\n\n"
        "Усередині Yamato — контент у сотні разів глибший.\n\n"
        "Там не \"як заробити\", а як не злити, коли всі інші панікують 💀\n\n"
        "Ми даємо:\n"
        "🔥 Щоденну альфу з ринку\n"
        "📊 Реальні кейси (не вигадки)\n"
        "💬 Ком'юніті без токсиків і спамерів\n"
        "🧠 Notion-базу знань, яку оновлюють щотижня\n\n"
        "Хочеш глянути, шо всередині?",
        reply_markup=keyboard
    )
    
    await state.set_state(UserStates.after_tutorial)


# БЛОК 3-4: Показати контент
@dp.callback_query(F.data == "show_inside")
async def show_content(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Чекаємо 8-12 годин (для тесту можна зменшити)
    await asyncio.sleep(36000)  # 10 годин
    
    # БЛОК 4: Підсилення
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Та давай вже залечу", callback_data="lets_go")],
        [types.InlineKeyboardButton(text="Хочу більше 🔥", callback_data="want_more")]
    ])
    
    await callback.message.answer_photo(
        photo="https://your-server.com/memes/sneakpeek.jpg",  # Замінити
        caption=(
            "Ну дивись, шо в нас є 👇\n\n"
            "🧩 Чек-лист — як за 5 хв відсіяти скам-проекти\n"
            "💡 Кейс: чувак зробив х3 за тиждень без істерик\n"
            "📈 Щоденні апдейти по топових токенах\n"
            "🎯 Стратегії для різних рівнів (від новачка до про)\n\n"
            "І це лише 10% від того, що ми даємо в Yamato.\n\n"
            "Тут усе просто:\n"
            "— ніяких курсів на $5000,\n"
            "— ніяких \"гуру\" з орендованими ламборгіні,\n"
            "— тільки реальні люди, що заробляють у крипті й діляться альфою.\n\n"
            "Шо, бро, тобі таке по душі? 😉"
        ),
        reply_markup=keyboard
    )


# БЛОК 5: Емоційний тригер
@dp.callback_query(F.data.in_(["lets_go", "want_more"]))
async def emotional_trigger(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Чекаємо 24 години (для тесту — менше)
    await asyncio.sleep(86400)  # 24 години
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Мені це треба 🔥", callback_data="need_this")]
    ])
    
    await callback.message.answer(
        "Слухай, бро, скажи чесно — скільки разів уже \"починав із понеділка\"? 😅\n\n"
        "Крипта — це не рулетка.\n"
        "Просто більшість не мають нормального оточення, яке підтримає, коли все летить у мінус.\n\n"
        "У Yamato ми не паніємо при -20%.\n"
        "Ми чітко знаємо, що робимо 💪\n\n"
        "Це не просто чат, а ком'юніті, де:\n"
        "✅ Кажуть \"тримай лінію\", а не \"продавай усе\"\n"
        "✅ Діляться стратегіями, а не скрінами з Binance\n"
        "✅ Допомагають, а не троллять\n\n"
        "Хочеш відчути себе частиною цього двіжу?\n\n"
        "Бо самому в крипті — це як грати в Dark Souls без гайдів 💀",
        reply_markup=keyboard
    )


# БЛОК 6: Анкетування — Ім'я
@dp.callback_query(F.data == "need_this")
async def start_survey_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await callback.message.answer(
        "Ну давай, братан, зробимо маленький \"KYC\", але по-нашому 😎\n"
        "Без паспортів, просто хочу зрозуміти, хто ти 👇\n\n"
        "1️⃣ Як тебе звати, бро?\n"
        "(або як тебе кликати в чаті?)"
    )
    
    await state.set_state(UserStates.name_input)


# Отримання імені
@dp.message(UserStates.name_input)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.text
    user_data[user_id]["name"] = user_name
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Я ще новачок 🍼", callback_data="exp_newbie")],
        [types.InlineKeyboardButton(text="Місяців 3–6", callback_data="exp_3-6")],
        [types.InlineKeyboardButton(text="Десь рік, уже шарю", callback_data="exp_1year")],
        [types.InlineKeyboardButton(text="Та я пережив LUNA, FTX і ще не здався 😂", callback_data="exp_veteran")]
    ])
    
    await message.answer(
        f"Кайф, {user_name}! 🤝\n\n"
        "2️⃣ Скільки вже в крипті?",
        reply_markup=keyboard
    )
    
    await state.set_state(UserStates.experience_select)


# Досвід у крипті
@dp.callback_query(F.data.startswith("exp_"))
async def process_experience(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    user_data[user_id]["experience"] = callback.data.replace("exp_", "")
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Інфоцигани", callback_data="pain_infoscam")],
        [types.InlineKeyboardButton(text="Зливи", callback_data="pain_losses")],
        [types.InlineKeyboardButton(text="Безсистемність", callback_data="pain_chaos")],
        [types.InlineKeyboardButton(text="Купа \"експертів\" із Telegram", callback_data="pain_experts")],
        [types.InlineKeyboardButton(text="Не знаю, з чого почати", callback_data="pain_start")]
    ])
    
    await callback.message.answer(
        "Respect 🫡\n\n"
        "3️⃣ Шо тебе більше всього бісить у крипті?\n"
        "(можна кілька варіантів, жми шо в душу запало)",
        reply_markup=keyboard
    )
    
    await state.set_state(UserStates.pain_points_select)


# Pain points (можна вибрати кілька)
@dp.callback_query(F.data.startswith("pain_"))
async def process_pain_points(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Додано!")
    user_id = callback.from_user.id
    
    if "pain_points" not in user_data[user_id]:
        user_data[user_id]["pain_points"] = []
    
    pain = callback.data.replace("pain_", "")
    user_data[user_id]["pain_points"].append(pain)
    
    # Додаємо кнопку "Далі" після вибору
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Інфоцигани", callback_data="pain_infoscam")],
        [types.InlineKeyboardButton(text="Зливи", callback_data="pain_losses")],
        [types.InlineKeyboardButton(text="Безсистемність", callback_data="pain_chaos")],
        [types.InlineKeyboardButton(text="Купа \"експертів\" із Telegram", callback_data="pain_experts")],
        [types.InlineKeyboardButton(text="Не знаю, з чого почати", callback_data="pain_start")],
        [types.InlineKeyboardButton(text="➡️ Далі", callback_data="pain_done")]
    ])
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)


# Завершення вибору pain points
@dp.callback_query(F.data == "pain_done")
async def pain_done(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Пасивку без нервів 😌", callback_data="goal_passive")],
        [types.InlineKeyboardButton(text="Заробляти стабільно 📈", callback_data="goal_stable")],
        [types.InlineKeyboardButton(text="Потрапити в нормальну ком'юніті 💬", callback_data="goal_community")],
        [types.InlineKeyboardButton(text="Альфу та інсайти 😎", callback_data="goal_alpha")]
    ])
    
    await callback.message.answer(
        "Ага, розумію тебе, бро 💯\n\n"
        "4️⃣ І головне — чого ти хочеш?",
        reply_markup=keyboard
    )
    
    await state.set_state(UserStates.goal_select)


# Мета користувача
@dp.callback_query(F.data.startswith("goal_"))
async def process_goal(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    user_data[user_id]["goal"] = callback.data.replace("goal_", "")
    user_name = user_data[user_id].get("name", "бро")
    
    await callback.message.answer(
        f"Дякую, {user_name}! 🔥\n\n"
        "Тепер я розумію, що тобі треба.\n"
        "Yamato — саме те місце, де ти знайдеш це.\n\n"
        "Дай мені трохи часу підготувати для тебе персональну інфу 👀\n"
        "Скоро напишу 😉"
    )
    
    # Чекаємо 36-48 годин (для тесту — менше)
    await asyncio.sleep(129600)  # 36 годин
    
    # БЛОК 7: Соціальний доказ
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Я встигаю?", callback_data="am_i_in_time")],
        [types.InlineKeyboardButton(text="Та скільки можна, дайте доступ", callback_data="give_access")]
    ])
    
    await callback.message.answer(
        "Ну шо, бро, коротко по фактах 👇\n\n"
        "Yamato зараз відкрив першу хвилю доступу — і місць лишилось не так уже й багато.\n\n"
        "Чому?\n"
        "Бо ми не беремо всіх підряд. Тільки тих, хто реально хоче діяти.\n\n"
        "Хлопці, що залетіли першими, уже:\n"
        "✅ Підняли профіт без паніки\n"
        "✅ Спокійно торгують за системою\n"
        "✅ Не ловлять FOMO на кожній новині\n\n"
        "Ось реальні відгуки:\n"
        "💬 \"Нарешті знайшов нормальних людей без понтів\"\n"
        "💬 \"За тиждень зрозумів більше, ніж за пів року на YouTube\"\n"
        "💬 \"Тут реально діляться альфою, а не впарюють курси\"\n\n"
        "Якщо відчуваєш, що пора нарешті вирватись із кола зливів — саме час.\n\n"
        "Але місць на цю хвилю залишилось **менше 20**.",
        reply_markup=keyboard
    )


# БЛОК 8: Конверсія
@dp.callback_query(F.data.in_(["am_i_in_time", "give_access"]))
async def conversion(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Я з вами 💪", url="https://payment.yamato.com")],  # Замінити на реальний лінк
        [types.InlineKeyboardButton(text="Хочу уточнити деталі", url="https://t.me/yamato_support")]  # Замінити
    ])
    
    await callback.message.answer(
        "Окей, без мінералки.\n\n"
        "Yamato — це закрите крипто-ком'юніті, де:\n"
        "💎 новачки не губляться,\n"
        "📊 трейдери діляться альфою,\n"
        "💬 ніхто не впарює \"поради\" за донати.\n\n"
        "Що всередині:\n"
        "🔐 Notion-база з гайдами, чек-листами і кейсами\n"
        "💬 Discord-сервер з каналами під різні рівні\n"
        "📈 Telegram-канал з щоденними апдейтами\n"
        "🎯 7-денний старт-челендж \"From Zero to Hero\"\n"
        "🧠 Менторська підтримка (не боти, а живі люди)\n\n"
        "💵 Підписка: **$199 / 2 місяці**\n"
        "(це менше $4 на день — одна кава в Starbucks ☕)\n\n"
        "Оплата: крипта (USDT/USDC) або картка.\n\n"
        "Після оплати отримаєш:\n"
        "✅ Доступ до Notion-бази (одразу)\n"
        "✅ Інвайт у Discord (протягом 5 хв)\n"
        "✅ Додавання в Telegram-канал\n"
        "✅ Старт челенджу\n\n"
        "Ну шо, летимо? 🚀",
        reply_markup=keyboard
    )
    
    await state.set_state(UserStates.ready_to_pay)


# БЛОК 9: Онбординг (викликається через webhook після оплати)
async def onboarding(user_id: int):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Почати челендж 💪", callback_data="start_challenge")],
        [types.InlineKeyboardButton(text="Глянути Notion 📚", url="https://notion.yamato.com")],
        [types.InlineKeyboardButton(text="Увійти в Discord 💬", url="https://discord.gg/yamato")]
    ])
    
    await bot.send_message(
        user_id,
        "ВІТАЮ, БРО! 🔥🔥🔥\n\n"
        "Ти офіційно став частиною Yamato — місця, де замість \"паніка\" кажуть \"заряджай стакан\" 😎\n\n"
        "Тепер ти в клубі, де:\n"
        "✅ Ніхто не паніє при дампах\n"
        "✅ Усі діляться альфою, а не хейтять\n"
        "✅ Є чітка система, а не хаос\n\n"
        "Почнемо з легкого — наш старт-челендж **\"7 днів до апгрейду\"**:\n\n"
        "📅 День 1: Як налаштувати свій перший портфель\n"
        "📅 День 2: Топ-3 помилки новачків (і як їх уникнути)\n"
        "📅 День 3: Де шукати альфу (і як не попастись на скам)\n"
        "📅 День 4: Базова технічна аналіз (без води)\n"
        "📅 День 5: Психологія трейдингу (чому ти зливаєш)\n"
        "📅 День 6: Як використовувати Notion-базу на повну\n"
        "📅 День 7: Твій перший профітний трейд (під супроводом)\n\n"
        "Кожен день — коротка задача (10-15 хв), поради від менторів і нові апдейти 💪\n\n"
        "Готовий прокачати скіли й не ловити FOMO?",
        reply_markup=keyboard
    )


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
