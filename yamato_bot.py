"""
YAMATO CHATBOT - aiogram implementation
Повний сценарій крипто-бота з емоційною воронкою
"""

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Ініціалізація
API_TOKEN = '8347139211:AAGoUvk4tBMaJvsTrcmbygrmGQ47gkwkLfs'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# 💾 Шлях до JSON файлів
DATA_DIR = Path(__file__).parent / "bot_data"
DATA_DIR.mkdir(exist_ok=True)
USER_DATA_FILE = DATA_DIR / "user_data.json"
ACTIVE_PROCESSES_FILE = DATA_DIR / "active_processes.json"


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

# 🛡️ Захист від спаму: відстежуємо активні процеси
active_processes = {}  # {user_id: "process_name"}


# 🛡️ Хелпер: Ініціалізація user_data
def init_user(user_id: int):
    """Ініціалізує користувача, якщо його ще немає в базі"""
    if user_id not in user_data:
        user_data[user_id] = {
            "timestamp_start": datetime.now().isoformat(),
            "stage": "unknown"
        }
    return user_data[user_id]


# 💾 Функції для збереження/завантаження JSON
def save_data():
    """Зберігає user_data в JSON файл"""
    try:
        # Конвертуємо datetime в string для JSON
        data_to_save = {}
        for user_id, data in user_data.items():
            data_to_save[str(user_id)] = {}
            for key, value in data.items():
                if isinstance(value, datetime):
                    data_to_save[str(user_id)][key] = value.isoformat()
                else:
                    data_to_save[str(user_id)][key] = value
        
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Помилка збереження даних: {e}")


def load_data():
    """Завантажує user_data з JSON файлу"""
    global user_data
    try:
        if USER_DATA_FILE.exists():
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                data_loaded = json.load(f)
                # Конвертуємо назад string keys в int
                user_data = {int(k): v for k, v in data_loaded.items()}
                print(f"✅ Завантажено дані для {len(user_data)} користувачів")
        else:
            print("📝 Файл даних не знайдено, починаємо з чистого листа")
    except Exception as e:
        print(f"❌ Помилка завантаження даних: {e}")
        user_data = {}


# 💾 Автозбереження кожні 60 секунд
async def auto_save_loop():
    """Автоматичне збереження даних кожну хвилину"""
    while True:
        await asyncio.sleep(60)  # Збереження кожні 60 секунд
        save_data()
        print(f"💾 Автозбереження: {datetime.now().strftime('%H:%M:%S')}")


# БЛОК 1: Привітання
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data[user_id] = {
        "timestamp_start": datetime.now().isoformat(),
        "stage": "start"
    }
    save_data()  # 💾 Зберігаємо після старту
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Давай інфу 🔥", callback_data="get_info")],
        [types.InlineKeyboardButton(text="Та шо там у тебе?", callback_data="whats_inside")]
    ])
    
    # 🔥 БЛОК 1: Привітання
    await message.answer(
        text=(
            "🎯 <b>Шо, бро, знову на інфоциганів натрапив?</b> 😏\n"
            "Розслабся, тут без гівна.\n\n"
            "Я так само колись починав — без знань, без системи, просто вірив у меми про \"<i>туземун</i>\" 🚀\n\n"
            "Коротше, <b>свій чувак у крипті</b>.\n"
            "Тут усе чесно, без водички — чисто <b>практика, альфа і трохи фану</b> 😎\n\n"
            "Готовий зловити щось, що <b>реально працює</b>, а не чергову \"мотиваційну байку\"?\n\n"
            "💡 [Тут мем \"WELCOME TO CRYPTO\"]"
        ),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await state.set_state(UserStates.start)


# Обробка кнопок БЛОК 1
@dp.callback_query(F.data.in_(["get_info", "whats_inside"]))
async def process_block1(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    
    # 🛡️ ЗАХИСТ: Перевіряємо, чи вже обробляємо цю дію
    if user_id in active_processes:
        await callback.answer("⏳ Почекай, обробляю попередню дію...", show_alert=True)
        return
    
    # 🛡️ ЗАХИСТ: Перевіряємо, чи вже відправили БЛОК 2
    current_state = await state.get_state()
    if current_state == UserStates.tutorial_sent or user_data.get(user_id, {}).get("block2_sent"):
        await callback.answer("✅ Я вже надіслав тобі інфу, бро!", show_alert=False)
        return
    
    await callback.answer()
    active_processes[user_id] = "block1_to_block2"
    
    try:
        user_data[user_id]["button_clicked"] = callback.data
        
        # 🔥 МОМЕНТАЛЬНО відправляємо БЛОК 2
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Давай туторіал 🎬", callback_data="get_tutorial")]
        ])
        
        await callback.message.answer(
            "Та не парся, не буде лекцій і нудятини 😴\n\n"
            "Для тебе підготував короткий туторіал із <b>реально корисною інфою</b> — без води, без фігні, все як ти любиш 💪\n\n"
            "Хочеш розібратись, як зібрати свій крипто-портфель і <b>не злити</b> депозит після першої червоної свічки?\n\n"
            "Тут усе по-людському:\n"
            "✅ <b>10 хвилин чистої альфи</b>\n"
            "✅ Нічого зайвого\n"
            "✅ Після — вже будеш <b>на голову вищим за 80% новачків</b>\n\n"
            "Летимо? 👇",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        user_data[user_id]["block2_sent"] = True
        await state.set_state(UserStates.tutorial_sent)
        save_data()  # 💾 Зберігаємо прогрес
        
    finally:
        # 🛡️ Звільняємо процес
        if user_id in active_processes:
            del active_processes[user_id]


# БЛОК 2: Відправка туторіалу
@dp.callback_query(F.data == "get_tutorial")
async def send_tutorial(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    
    # 🛡️ ЗАХИСТ: Перевіряємо, чи вже обробляємо
    if user_id in active_processes:
        await callback.answer("⏳ Почекай, обробляю...", show_alert=True)
        return
    
    # 🛡️ ЗАХИСТ: Перевіряємо, чи вже відправили туторіал
    if user_data.get(user_id, {}).get("tutorial_sent"):
        await callback.answer("✅ Туторіал вже надіслано, бро!", show_alert=False)
        return
    
    await callback.answer()
    active_processes[user_id] = "tutorial_to_block3"
    
    try:
        user_data[user_id]["tutorial_sent"] = datetime.now()
        
        # 🔥 МОМЕНТАЛЬНО відправляємо туторіал
        await callback.message.answer(
            "<b>Ось твій туторіал, бро!</b> 👇\n\n"
            "🎬 https://youtube.com/your-tutorial-link\n\n"  # Замінити на реальний лінк
            "Дивись спокійно, після напишу 😉",
            parse_mode="HTML"
        )
        
        # 🔥 ВИДАЛЕНО ЗАТРИМКУ — наступний блок відправляється ОДРАЗУ
        # В продакшені можна повернути: await asyncio.sleep(900) — 15 хвилин
        
        # БЛОК 3: Після туторіалу
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Покажи, шо там", callback_data="show_inside")]
        ])
        
        await callback.message.answer(
            "<b>Зацінив, бро?</b> 👀\n"
            "Це лише <i>початок</i> 😉\n\n"
            "Усередині <b>Yamato</b> — контент у <b>сотні разів глибший</b>.\n\n"
            "Там не \"як заробити\", а <b>як не злити</b>, коли всі інші панікують 💀\n\n"
            "Ми даємо:\n"
            "🔥 <b>Щоденну альфу</b> з ринку\n"
            "📊 <b>Реальні кейси</b> (не вигадки)\n"
            "💬 <b>Ком'юніті</b> без токсиків і спамерів\n"
            "🧠 <b>Notion-базу знань</b>, яку оновлюють щотижня\n\n"
            "Хочеш глянути, шо всередині?",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        user_data[user_id]["block3_sent"] = True
        await state.set_state(UserStates.after_tutorial)
        save_data()  # 💾 Зберігаємо прогрес
        
    finally:
        # 🛡️ Звільняємо процес
        if user_id in active_processes:
            del active_processes[user_id]


# БЛОК 3-4: Показати контент
@dp.callback_query(F.data == "show_inside")
async def show_content(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    
    # 🛡️ ЗАХИСТ
    if user_id in active_processes:
        await callback.answer("⏳ Вже обробляю, зачекай...", show_alert=True)
        return
    
    if user_data.get(user_id, {}).get("block4_sent"):
        await callback.answer("✅ Я вже показав тобі контент!", show_alert=False)
        return
    
    await callback.answer()
    active_processes[user_id] = "block3_to_block4"
    
    try:
        # 🔥 ВИДАЛЕНО ЗАТРИМКУ — БЛОК 4 відправляється ОДРАЗУ
        # В продакшені можна повернути: await asyncio.sleep(36000) — 10 годин
        
        # 🔥 БЛОК 4: Підсилення (відправка)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Та давай вже залечу", callback_data="lets_go")],
            [types.InlineKeyboardButton(text="Хочу більше 🔥", callback_data="want_more")]
        ])
        
        # 🔥 Відправка без фото (для тестування)
        await callback.message.answer(
            text=(
                "💎 <b>Ну дивись, шо в нас є</b> 👇\n\n"
                "🧩 Чек-лист — <b>як за 5 хв відсіяти скам-проекти</b>\n"
                "💡 Кейс: чувак зробив <b>х3 за тиждень</b> без істерик\n"
                "📈 <b>Щоденні апдейти</b> по топових токенах\n"
                "🎯 Стратегії для різних рівнів (від новачка до про)\n\n"
                "І це лише <b>10%</b> від того, що ми даємо в Yamato.\n\n"
                "Тут усе просто:\n"
                "— <b>ніяких</b> курсів на $5000,\n"
                "— <b>ніяких</b> \"гуру\" з орендованими ламборгіні,\n"
                "— тільки <b>реальні люди</b>, що заробляють у крипті й діляться альфою.\n\n"
                "Шо, бро, тобі таке по душі? 😉\n\n"
                "🖼️ [Тут мем \"SNEAKPEEK\"]"
            ),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        user_data[user_id]["block4_sent"] = True
        save_data()  # 💾 Зберігаємо прогрес
        
    finally:
        if user_id in active_processes:
            del active_processes[user_id]


# БЛОК 5: Емоційний тригер
@dp.callback_query(F.data.in_(["lets_go", "want_more"]))
async def emotional_trigger(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    
    # 🛡️ ЗАХИСТ
    if user_id in active_processes:
        await callback.answer("⏳ Обробка...", show_alert=True)
        return
    
    if user_data.get(user_id, {}).get("block5_sent"):
        await callback.answer("✅ Вже надіслано!", show_alert=False)
        return
    
    await callback.answer()
    active_processes[user_id] = "block4_to_block5"
    
    try:
        # 🔥 ВИДАЛЕНО ЗАТРИМКУ — БЛОК 5 відправляється ОДРАЗУ
        # В продакшені можна повернути: await asyncio.sleep(86400) — 24 години
        
        # 🔥 БЛОК 5: Емоційний тригер (відправка)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Мені це треба 🔥", callback_data="need_this")]
        ])
        
        await callback.message.answer(
            "Слухай, бро, скажи чесно — скільки разів уже <i>\"починав із понеділка\"</i>? 😅\n\n"
            "<b>Крипта — це не рулетка.</b>\n"
            "Просто більшість не мають нормального оточення, яке підтримає, коли все летить у мінус.\n\n"
            "У <b>Yamato</b> ми <b>не паніємо</b> при -20%.\n"
            "Ми чітко знаємо, що робимо 💪\n\n"
            "Це не просто чат, а <b>ком'юніті</b>, де:\n"
            "✅ Кажуть <b>\"тримай лінію\"</b>, а не \"продавай усе\"\n"
            "✅ Діляться <b>стратегіями</b>, а не скрінами з Binance\n"
            "✅ <b>Допомагають</b>, а не троллять\n\n"
            "Хочеш відчути себе частиною цього двіжу?\n\n"
            "Бо самому в крипті — це як грати в <i>Dark Souls без гайдів</i> 💀",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        user_data[user_id]["block5_sent"] = True
        save_data()  # 💾 Зберігаємо прогрес
        
    finally:
        if user_id in active_processes:
            del active_processes[user_id]


# БЛОК 6: Анкетування — Ім'я
@dp.callback_query(F.data == "need_this")
async def start_survey_name(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    
    # 🛡️ ЗАХИСТ
    if user_data.get(user_id, {}).get("survey_started"):
        await callback.answer("✅ Анкета вже надіслана!", show_alert=False)
        return
    
    await callback.answer()
    user_data[user_id]["survey_started"] = True
    save_data()  # 💾 Зберігаємо прогрес
    
    # 🔥 МОМЕНТАЛЬНО відправляємо анкету
    await callback.message.answer(
        "Ну давай, братан, зробимо маленький <b>\"KYC\"</b>, але по-нашому 😎\n"
        "Без паспортів, просто хочу зрозуміти, хто ти 👇\n\n"
        "<b>1️⃣ Як тебе звати, бро?</b>\n"
        "(або як тебе кликати в чаті?)",
        parse_mode="HTML"
    )
    
    await state.set_state(UserStates.name_input)


# Отримання імені
@dp.message(UserStates.name_input)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    
    user_name = message.text
    user_data[user_id]["name"] = user_name
    save_data()  # 💾 Зберігаємо прогрес
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Я ще новачок 🍼", callback_data="exp_newbie")],
        [types.InlineKeyboardButton(text="Місяців 3–6", callback_data="exp_3-6")],
        [types.InlineKeyboardButton(text="Десь рік, уже шарю", callback_data="exp_1year")],
        [types.InlineKeyboardButton(text="Та я пережив LUNA, FTX і ще не здався 😂", callback_data="exp_veteran")]
    ])
    
    await message.answer(
        f"<b>Кайф, {user_name}!</b> 🤝\n\n"
        "<b>2️⃣ Скільки вже в крипті?</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await state.set_state(UserStates.experience_select)


# Досвід у крипті
@dp.callback_query(F.data.startswith("exp_"))
async def process_experience(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    
    # 🛡️ ЗАХИСТ: Якщо вже вибрано досвід
    if user_data.get(user_id, {}).get("experience"):
        await callback.answer("✅ Вже вибрано!", show_alert=False)
        return
    
    await callback.answer()
    user_data[user_id]["experience"] = callback.data.replace("exp_", "")
    save_data()  # 💾 Зберігаємо прогрес
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Інфоцигани", callback_data="pain_infoscam")],
        [types.InlineKeyboardButton(text="Зливи", callback_data="pain_losses")],
        [types.InlineKeyboardButton(text="Безсистемність", callback_data="pain_chaos")],
        [types.InlineKeyboardButton(text="Купа \"експертів\" із Telegram", callback_data="pain_experts")],
        [types.InlineKeyboardButton(text="Не знаю, з чого почати", callback_data="pain_start")]
    ])
    
    await callback.message.answer(
        "<b>Respect</b> 🫡\n\n"
        "<b>3️⃣ Шо тебе більше всього бісить у крипті?</b>\n"
        "(можна кілька варіантів, жми шо в душу запало)",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await state.set_state(UserStates.pain_points_select)


# Завершення вибору pain points (ВАЖЛИВО: має бути ПЕРЕД process_pain_points)
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
        "Ага, <b>розумію тебе, бро</b> 💯\n\n"
        "<b>4️⃣ І головне — чого ти хочеш?</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await state.set_state(UserStates.goal_select)


# Pain points (можна вибрати кілька)
@dp.callback_query(F.data.startswith("pain_"), ~F.data.in_(["pain_done"]))
async def process_pain_points(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    await callback.answer("Додано! ✅")
    
    # 🛡️ Видаляємо дублікат ініціалізації (вже є вище)
    if "pain_points" not in user_data[user_id]:
        user_data[user_id]["pain_points"] = []
    
    pain = callback.data.replace("pain_", "")
    
    # 🛡️ Перевірка: якщо вже вибрано цей pain point — не додаємо
    if pain not in user_data[user_id]["pain_points"]:
        user_data[user_id]["pain_points"].append(pain)
        save_data()  # 💾 Зберігаємо прогрес
    
    # Додаємо кнопку "Далі" після вибору
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Інфоцигани", callback_data="pain_infoscam")],
        [types.InlineKeyboardButton(text="Зливи", callback_data="pain_losses")],
        [types.InlineKeyboardButton(text="Безсистемність", callback_data="pain_chaos")],
        [types.InlineKeyboardButton(text="Купа \"експертів\" із Telegram", callback_data="pain_experts")],
        [types.InlineKeyboardButton(text="Не знаю, з чого почати", callback_data="pain_start")],
        [types.InlineKeyboardButton(text="➡️ Далі", callback_data="pain_done")]
    ])
    
    # 🛡️ Обгортаємо в try/except, щоб уникнути помилки "message is not modified"
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    except Exception:
        # Якщо клавіатура вже така сама — ігноруємо помилку
        pass


# Мета користувача
@dp.callback_query(F.data.startswith("goal_"))
async def process_goal(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    
    # 🛡️ ЗАХИСТ
    if user_data.get(user_id, {}).get("goal"):
        await callback.answer("✅ Мету вже вибрано!", show_alert=False)
        return
    
    # 🛡️ ЗАХИСТ: Якщо вже запустили БЛОК 7
    if user_id in active_processes and active_processes[user_id] == "goal_to_block7":
        await callback.answer("⏳ Обробка...", show_alert=True)
        return
    
    await callback.answer()
    active_processes[user_id] = "goal_to_block7"
    
    try:
        user_data[user_id]["goal"] = callback.data.replace("goal_", "")
        user_name = user_data[user_id].get("name", "бро")
        
        # 🔥 МОМЕНТАЛЬНО відправляємо подяку
        await callback.message.answer(
            f"<b>Дякую, {user_name}!</b> 🔥\n\n"
            "Тепер я розумію, що тобі треба.\n"
            "<b>Yamato</b> — саме те місце, де ти знайдеш це.\n\n"
            "Дай мені трохи часу підготувати для тебе <b>персональну інфу</b> 👀\n"
            "Скоро напишу 😉",
            parse_mode="HTML"
        )
        
        # 🔥 ВИДАЛЕНО ЗАТРИМКУ — БЛОК 7 відправляється ОДРАЗУ
        # В продакшені можна повернути: await asyncio.sleep(129600) — 36 годин
        
        # 🔥 БЛОК 7: Соціальний доказ (відправка)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Я встигаю?", callback_data="am_i_in_time")],
            [types.InlineKeyboardButton(text="Та скільки можна, дайте доступ", callback_data="give_access")]
        ])
        
        await callback.message.answer(
            "<b>Ну шо, бро, коротко по фактах</b> 👇\n\n"
            "<b>Yamato</b> зараз відкрив <b>першу хвилю доступу</b> — і місць лишилось не так уже й багато.\n\n"
            "<b>Чому?</b>\n"
            "Бо ми не беремо всіх підряд. Тільки тих, хто <b>реально хоче діяти</b>.\n\n"
            "Хлопці, що залетіли першими, уже:\n"
            "✅ <b>Підняли профіт</b> без паніки\n"
            "✅ Спокійно <b>торгують за системою</b>\n"
            "✅ <b>Не ловлять FOMO</b> на кожній новині\n\n"
            "<b>Ось реальні відгуки:</b>\n"
            "💬 <i>\"Нарешті знайшов нормальних людей без понтів\"</i>\n"
            "💬 <i>\"За тиждень зрозумів більше, ніж за пів року на YouTube\"</i>\n"
            "💬 <i>\"Тут реально діляться альфою, а не впарюють курси\"</i>\n\n"
            "Якщо відчуваєш, що пора нарешті вирватись із кола зливів — <b>саме час</b>.\n\n"
            "Але місць на цю хвилю залишилось <b>менше 20</b>.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        user_data[user_id]["block7_sent"] = True
        save_data()  # 💾 Зберігаємо прогрес
        
    finally:
        if user_id in active_processes:
            del active_processes[user_id]


# БЛОК 8: Конверсія
@dp.callback_query(F.data.in_(["am_i_in_time", "give_access"]))
async def conversion(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)  # 🛡️ Ініціалізація
    
    # 🛡️ ЗАХИСТ
    if user_data.get(user_id, {}).get("conversion_sent"):
        await callback.answer("✅ Інфо про оплату вже надіслано!", show_alert=False)
        return
    
    await callback.answer()
    user_data[user_id]["conversion_sent"] = True
    save_data()  # 💾 Зберігаємо прогрес
    
    # 🔥 МОМЕНТАЛЬНО відправляємо інфо про оплату
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Я з вами 💪", url="https://payment.yamato.com")],  # Замінити на реальний лінк
        [types.InlineKeyboardButton(text="Хочу уточнити деталі", url="https://t.me/yamato_support")]  # Замінити
    ])
    
    await callback.message.answer(
        "<b>Окей, без мінералки.</b>\n\n"
        "<b>Yamato</b> — це закрите крипто-ком'юніті, де:\n"
        "💎 новачки <b>не губляться</b>,\n"
        "📊 трейдери <b>діляться альфою</b>,\n"
        "💬 ніхто не впарює \"поради\" за донати.\n\n"
        "<b>Що всередині:</b>\n"
        "🔐 <b>Notion-база</b> з гайдами, чек-листами і кейсами\n"
        "💬 <b>Discord-сервер</b> з каналами під різні рівні\n"
        "📈 <b>Telegram-канал</b> з щоденними апдейтами\n"
        "🎯 7-денний старт-челендж <i>\"From Zero to Hero\"</i>\n"
        "🧠 <b>Менторська підтримка</b> (не боти, а живі люди)\n\n"
        "💵 <b>Підписка: $199 / 2 місяці</b>\n"
        "(це менше <b>$4 на день</b> — одна кава в Starbucks ☕)\n\n"
        "Оплата: <b>крипта (USDT/USDC)</b> або <b>картка</b>.\n\n"
        "<b>Після оплати отримаєш:</b>\n"
        "✅ Доступ до Notion-бази (одразу)\n"
        "✅ Інвайт у Discord (протягом 5 хв)\n"
        "✅ Додавання в Telegram-канал\n"
        "✅ Старт челенджу\n\n"
        "<b>Ну шо, летимо?</b> 🚀",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await state.set_state(UserStates.ready_to_pay)


# БЛОК 9: Онбординг (викликається через webhook після оплати)
async def onboarding(user_id: int):
    """Функція для онбордингу після підтвердження оплати"""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Почати челендж 💪", callback_data="start_challenge")],
        [types.InlineKeyboardButton(text="Глянути Notion 📚", url="https://notion.yamato.com")],
        [types.InlineKeyboardButton(text="Увійти в Discord 💬", url="https://discord.gg/yamato")]
    ])
    
    await bot.send_message(
        user_id,
        "<b>ВІТАЮ, БРО!</b> 🔥🔥🔥\n\n"
        "Ти офіційно став частиною <b>Yamato</b> — місця, де замість \"паніка\" кажуть <i>\"заряджай стакан\"</i> 😎\n\n"
        "<b>Тепер ти в клубі, де:</b>\n"
        "✅ Ніхто <b>не паніє</b> при дампах\n"
        "✅ Усі <b>діляться альфою</b>, а не хейтять\n"
        "✅ Є <b>чітка система</b>, а не хаос\n\n"
        "Почнемо з легкого — наш старт-челендж <b>\"7 днів до апгрейду\"</b>:\n\n"
        "📅 <b>День 1:</b> Як налаштувати свій перший портфель\n"
        "📅 <b>День 2:</b> Топ-3 помилки новачків (і як їх уникнути)\n"
        "📅 <b>День 3:</b> Де шукати альфу (і як не попастись на скам)\n"
        "📅 <b>День 4:</b> Базова технічна аналіз (без води)\n"
        "📅 <b>День 5:</b> Психологія трейдингу (чому ти зливаєш)\n"
        "📅 <b>День 6:</b> Як використовувати Notion-базу на повну\n"
        "📅 <b>День 7:</b> Твій перший профітний трейд (під супроводом)\n\n"
        "Кожен день — коротка задача (<b>10-15 хв</b>), поради від менторів і нові апдейти 💪\n\n"
        "<b>Готовий прокачати скіли й не ловити FOMO?</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# Запуск бота
async def main():
    # 💾 Завантажуємо дані при старті
    load_data()
    
    # 🔄 Запускаємо автозбереження в фоні
    asyncio.create_task(auto_save_loop())
    
    print("🚀 Yamato Bot запущено!")
    print(f"📊 Користувачів у базі: {len(user_data)}")
    
    try:
        await dp.start_polling(bot)
    finally:
        # 💾 Зберігаємо дані перед виходом
        save_data()
        print("💾 Дані збережено перед виходом")


if __name__ == '__main__':
    asyncio.run(main())
