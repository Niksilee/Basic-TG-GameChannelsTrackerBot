import telebot
from telethon import TelegramClient
from telethon.tl.types import Channel
from collections import defaultdict, Counter
import re
import asyncio
import nest_asyncio
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Отключаем логи Telebot
telebot.logger.setLevel(logging.WARNING)

# Разрешаем вложенные event loops
nest_asyncio.apply()

# Конфигурация
API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Актуальный список игровых серий на июль 2024
GAME_SERIES = {
    'Call of Duty': ['cod', 'call of duty', 'modern warfare', 'warzone'],
    'Battlefield': ['battlefield', 'bf'],
    'Assassin\'s Creed': ['assassin\'s creed', 'ac'],
    'FIFA/EA FC': ['fifa', 'ea fc', 'ea sports fc'],
    'Counter-Strike': ['counter-strike', 'cs', 'cs2', 'cs:go'],
    'Dota 2': ['dota 2', 'dota'],
    'League of Legends': ['league of legends', 'lol', 'wild rift'],
    'Valorant': ['valorant'],
    'Apex Legends': ['apex legends', 'apex'],
    'Fortnite': ['fortnite'],
    'GTA': ['gta', 'grand theft auto'],
    'The Witcher': ['witcher', 'ведьмак'],
    'Cyberpunk 2077': ['cyberpunk', 'киберпанк'],
    'Elder Scrolls': ['elder scrolls', 'skyrim', 'oblivion'],
    'Fallout': ['fallout'],
    'Starfield': ['starfield'],
    'Star Wars': ['star wars', 'jedi', 'sw'],
    'God of War': ['god of war', 'gow'],
    'The Last of Us': ['the last of us', 'tlou'],
    'Horizon': ['horizon', 'horizon zero dawn', 'horizon forbidden west'],
    'Resident Evil': ['resident evil', 're'],
    'Final Fantasy': ['final fantasy', 'ff'],
    'Diablo': ['diablo'],
    'World of Warcraft': ['world of warcraft', 'wow'],
    'Overwatch': ['overwatch', 'ow'],
    'Minecraft': ['minecraft'],
    'PUBG': ['pubg', 'battlegrounds'],
    'Rainbow Six Siege': ['rainbow six', 'r6', 'r6 siege'],
    'Destiny': ['destiny'],
    'Halo': ['halo'],
    'Tomb Raider': ['tomb raider'],
    'Soulslike': ['dark souls', 'elden ring', 'sekiro', 'bloodborne'],
    'Xbox': ['xbox', 'xbox series'],
    'PlayStation': ['playstation', 'ps5', 'ps4'],
    'Nintendo': ['nintendo', 'switch']
}

# Стоп-слова (расширенный список)
STOP_WORDS = {
    'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да',
    'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о',
    'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него',
    'до',
    'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где',
    'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз',
    'тоже',
    'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь',
    'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда',
    'можно',
    'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про',
    'всего',
    'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда',
    'лучше',
    'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между', 'game', 'игра', 'игр', 'игры',
    'релиз', 'обзор', 'новости', 'новый', 'новостей', 'новые', 'это', 'эти', 'этот', 'эта', 'этих', 'все', 'весь',
    'свой',
    'который', 'как', 'так', 'например', 'будто', 'есть', 'нет', 'очень', 'просто', 'уже', 'еще', 'тоже', 'лишь',
    'только',
    'даже', 'именно', 'вот', 'тут', 'там', 'где', 'когда', 'спасибо', 'пожалуйста', 'хорошо', 'плохо', 'сейчас', 'потом'
}

# Ключевые слова, указывающие на основную тему поста
TOPIC_KEYWORDS = {
    'анонс', 'релиз', 'выход', 'дата выхода', 'трейлер', 'геймплей', 'обзор', 'рецензия',
    'патч', 'обновление', 'апдейт', 'исправление', 'багфикс', 'нововведение', 'фича',
    'скриншот', 'арт', 'концепт', 'превью', 'интервью', 'эксклюзив', 'сведения', 'подробности',
    'анонсировано', 'представлено', 'показано', 'демонстрация', 'анализ', 'разбор', 'оценка'
}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    help_text = (
        "🎮 Привет! Я бот для анализа игровых и технических Telegram каналов.\n\n"
        "📊 Отправь мне команду в формате:\n"
        "/analyze @username_канала\n\n"
        "Например:\n/analyze @gamenews\n\n"
        "Я проанализирую последние 100 постов и покажу:\n"
        "- Самые упоминаемые игровые серии\n"
        "- Тип упоминания (прямое/контекстное)\n"
        "- Топ-5 ключевых слов для каждой серии"
    )
    bot.reply_to(message, help_text)


def preprocess_text(text):
    """Очистка и подготовка текста"""
    # Удаляем ссылки, упоминания и специальные символы
    text = re.sub(r'http\S+|@\w+|[^\w\s]|[\d_]', ' ', text.lower())
    # Простая токенизация по пробелам
    words = text.split()
    # Удаляем стоп-слова и короткие слова
    return [word for word in words if word not in STOP_WORDS and len(word) > 3]


def detect_game_series(text):
    """Обнаруживает упоминания игровых серий в тексте"""
    mentioned_series = {}
    text_lower = text.lower()

    for series, keywords in GAME_SERIES.items():
        for keyword in keywords:
            # Ищем точные совпадения с ключевыми словами
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                # Определяем тип упоминания
                mention_type = "context"

                # Проверяем наличие ключевых слов темы вблизи упоминания
                for topic_keyword in TOPIC_KEYWORDS:
                    # Ищем ключевое слово в радиусе 10 слов от упоминания
                    pattern = r'\b' + re.escape(keyword) + r'\b.{0,20}\b' + re.escape(topic_keyword) + r'\b'
                    if re.search(pattern, text_lower):
                        mention_type = "direct"
                        break

                mentioned_series[series] = mention_type
                break

    return mentioned_series


async def fetch_channel_data(username):
    """Асинхронно получает данные канала через пользовательский аккаунт"""
    async with TelegramClient('anon', API_ID, API_HASH) as client:
        # Получаем информацию о канале
        try:
            channel = await client.get_entity(username)
        except ValueError:
            try:
                channel = await client.get_entity(f'https://t.me/{username}')
            except Exception as e:
                raise ValueError(f"Не удалось найти канал: {str(e)}")

        # Собираем последние 100 постов
        series_stats = defaultdict(lambda: {
            'direct': 0,
            'context': 0,
            'keywords': defaultdict(int)
        })

        async for message in client.iter_messages(channel, limit=100):
            if message.text:
                text = message.text
                words = preprocess_text(text)

                # Ищем упоминания игровых серий и их тип
                mentioned_series = detect_game_series(text)

                # Обновляем статистику для каждой упомянутой серии
                for series, mention_type in mentioned_series.items():
                    series_stats[series][mention_type] += 1

                    # Собираем ключевые слова для этой серии
                    for word in words:
                        # Исключаем ключевые слова самой серии
                        if not any(kw in word for kw in GAME_SERIES[series]):
                            series_stats[series]['keywords'][word] += 1

        return series_stats


@bot.message_handler(commands=['analyze'])
def analyze_channel(message):
    try:
        command, username = message.text.split()
        username = username.strip('@')
    except ValueError:
        bot.reply_to(message, "⚠️ Неверный формат команды. Используйте: /analyze @username_канала")
        return

    try:
        # Отправляем сообщение о начале анализа
        msg = bot.reply_to(message, f"🔍 Начинаю анализ канала @{username}... Это может занять 1-2 минуты")

        # Запускаем асинхронную задачу
        loop = asyncio.get_event_loop()
        series_stats = loop.run_until_complete(fetch_channel_data(username))

        if not series_stats:
            bot.reply_to(message, "ℹ️ В канале не обнаружено упоминаний известных игровых серий.")
            return

        # Формирование результатов
        current_date = datetime.now().strftime("%d.%m.%Y")
        result = f"📊 Анализ игрового канала: @{username}\n"
        result += f"📅 Дата анализа: {current_date}\n"
        result += f"🔢 Проанализировано постов: 100\n\n"

        result += "🎮 Упоминания игровых серий:\n"

        # Сортируем серии по общему количеству упоминаний
        sorted_series = sorted(
            series_stats.items(),
            key=lambda x: x[1]['direct'] + x[1]['context'],
            reverse=True
        )[:10]  # Топ-10

        for series, stats in sorted_series:
            total = stats['direct'] + stats['context']
            result += f"\n<b>{series}</b>\n"
            result += f"• Всего упоминаний: {total}\n"
            result += f"• Прямые: {stats['direct']} (основная тема поста)\n"
            result += f"• Контекстные: {stats['context']} (упоминание в других новостях)\n"

            # Получаем топ-5 ключевых слов для этой серии
            keywords = Counter(stats['keywords'])
            top_keywords = keywords.most_common(5)

            if top_keywords:
                result += f"• Топ-5 ключевых слов: "
                result += ", ".join([f"{word} ({freq})" for word, freq in top_keywords])
            else:
                result += "• Не удалось выделить ключевые слова"
            result += "\n"

        # Добавляем информацию об анализируемых сериях
        result += "\nℹ️ Анализировались упоминания следующих серий: "
        result += ", ".join(GAME_SERIES.keys())

        # Добавляем пояснение
        result += "\n\n💡 <b>Прямые упоминания</b> - когда игра является основной темой поста"
        result += "\n💡 <b>Контекстные упоминания</b> - когда игра упоминается в контексте других новостей"

        # Удаляем сообщение о загрузке
        try:
            bot.delete_message(message.chat.id, msg.message_id)
        except:
            pass

        bot.reply_to(message, result, parse_mode='HTML')

    except Exception as e:
        error_msg = f"❌ Ошибка анализа: {str(e)}\n\n"
        error_msg += "Возможные причины:\n"
        error_msg += "1. Канал не существует или не публичный\n"
        error_msg += "2. Ошибка подключения к Telegram API\n"
        error_msg += "3. Неправильные API_ID/API_HASH\n"
        error_msg += "4. Канал слишком большой или недоступен"
        bot.reply_to(message, error_msg)


if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()